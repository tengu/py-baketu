# -*- coding: utf-8 -*-

class Struct(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

class Entry(object):

    def __init__(self, bucket, key):
        self.bucket=bucket
        self.key=key
        self.imp_init(bucket, key)

    def __repr__(self):
        return "%s(%s/%s)" % (self.__class__.__name__, self.bucket.name, self.key)

    def url(self):
        return 'http://{host}{path}'.format(host=self.bucket.name, path=self.key)

class Bucket(object):
    """Absctract Bucket"""

    def __init__(self, session, name, **opt):
        self.session=session
        self.name=name
        # xx session and name can be accessed as an attribute..xb
        self.imp_init(session, name, **opt)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    def entry(self, key):
        return self.session.entry_class(self, key)

class Session(object):
    """Abstract Session class.
    Represents connection to the remote store.
    * token: key to open a store
      * s3: access token
      * fs: root path
    """
    
    def __init__(self, token, secret):
        """
        * token: access-key, access-token, login etc that identifies the user
        """
        self.token=token
        self.imp_init(token, secret)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.token)

    def bucket(self, name, create=True):
        return self.bucket_class(self, name, create=create)
