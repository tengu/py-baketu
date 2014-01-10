#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sync local files to bucketed key-value store

* todo:
  * list remote
  * delete remote
"""
import sys,os
import time
import json
import hashlib
import re
import mimetypes
import urlparse

from driver import Struct
import driver_fs
import driver_s3

drivers=dict([ (k.replace('driver_',''),v) for k,v in locals().items() if k.startswith('driver_')])

class Url(object):
    """universal url reader
    adop any adhoc url-like identifier to content
    """
    def __init__(self, url):
        self.url=url
        try:
            self.scheme,self.rest=url.split('://')
        except ValueError, e:
            e.args+=(url,)
            raise
    def read(self):
        return getattr(self, 'read_'+self.scheme)()
    def read_file(self):
        return file(self.rest).read()
    def read_str(self):
        return self.rest
    def read_http(self):
        return urllib2.urlopen(self.url).read()
    def read_json(self):
        return self.rest

    def val(self):
        return json.loads(self.read())

def format_path(fmt, local_path):
    """instantiate 'name' template with local_path attributes
    """

    # setup environment in which the exprs are evaluated.
    # xx reuse this between invocations.
    frame=dict(
        path=local_path,
        rpath=local_path.lstrip('/'),
        basename=os.path.basename(local_path),
        md5=hashlib.md5(file(local_path).read()).hexdigest(), # xx surping..
        named=(local_path.split('\t')+[None])[1], # if two-col tsv
        suffix=os.path.splitext(local_path)[1],
        )

    # namer: eval any expression in {}, like $s=~s/{(.*)}/eval($1)/g in perl
    def replace(m):
        expr=m.group(1)
        return eval(expr, frame)
    return re.sub(r'{(.*?)}', replace, fmt)

# xx log entry method
def already_pushed(logpath):

    if not logpath:
        return None             # not sure

    records=[json.loads(line) for line in file(logpath).readlines()]
    if not records:
        return False            # hasn't been pushed
    
    r=records[-1]
    return ('op', 'push') in r.items() and not r.get('error')

def log_write(logpath, local_path, e):

    if not logpath:
        return

    file(logpath, 'a').write(json.dumps(dict(op='push',
                                             time=time.time(),
                                             local=local_path,
                                             error=None,
                                             remote=e.url()))+'\n')

def _push(b, files, name, log='{path}.synclog', dryrun=False, force=False):

    for local_path in files:

        mime_type,_=mimetypes.guess_type(local_path)

        key=format_path(name, local_path)
        logpath=format_path(log, local_path) if log else None

        e=b.entry(key)

        if dryrun:
            status='dryrun'
        elif already_pushed(logpath) and not force:
            status='skip'
        else:
            status='push'
            e.set_data(file(local_path).read(), content_type=mime_type)
            log_write(logpath, local_path, e)

        print '\t'.join([status, local_path, e.url()])

def make_bucket(driver, access, bucket):
    return _make_bucket(driver, access, bucket)

def _make_bucket(driver_name, access_url, bucket_name):

    driver=drivers[driver_name]
    accessd=Url(access_url).val()
    c=driver.Session(accessd['token'], accessd.get('secret'))
    print >>sys.stderr, 'session:', c
    return c.bucket(bucket_name)

def register_commands(baker=None):

    if not baker:
        import baker

    @baker.command
    def pushs(bucket, 
              access, 
              name, 
              log='{path}.synclog', 
              driver='s3', 
              dryrun=False,
              force=False,
              ):
        """push a stream of local file paths, read from stdin, to remote store.
        """

        b=make_bucket(driver, access, bucket)
        files=(line.strip('\n').split('\t')[0] for line in sys.stdin.readlines())
        _push(b, files, name, log, dryrun, force)


    @baker.command
    def push(bucket, 
             access, 
             name, 
             log='{path}.synclog', 
             driver='s3', 
             dryrun=False,
             force=False,
             *files
             ):
        """push files given on commandline.
        """
        b=make_bucket(driver, access, bucket)
        _push(b, files, name, log, dryrun, force)

    @baker.command
    def pushc(cfg, *files):
        """push Concisely using Config file.
        usage: baketu.py pushc ./test.cfg src/*.jpg
        """
        # allow shorthand
        if cfg.startswith('/') or cfg.startswith('.'):
            cfg='file://'+cfg
        cfg=json.loads(Url(cfg).read())

        name=cfg.pop('name')
        if 'access_token' in cfg:
            access_token=cfg.pop('access_token')
            accessd=dict(token=access_token)
        else:
            accessd=cfg['access']
        cfg['access']='json://'+json.dumps(accessd)
            
            
        print cfg

        b=make_bucket(**cfg)
        _push(b, files, name)

        
    return baker


def main():
    register_commands().run()

if __name__=='__main__':

    main()
