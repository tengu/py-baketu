#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import driver

class Entry(driver.Entry):

    # hooks
    def imp_init(self, bucket, key):
        pass

    # interface
    def data(self):
        return file(self._fs_path()).read()

    def set_data(self, data, content_type=None):
        """saves the data to the remote location"""

        epath=self._fs_path()
        try:
            os.makedirs(os.path.dirname(epath))
        except OSError, ex:
            if ex.errno==17:
                pass
            else:
                raise
        file(epath, 'w').write(data)

    def url(self):
        return 'file://'+os.path.abspath(self._fs_path())

    # helpers
    def _fs_path(self):
        if self.key.startswith('/'):
            print >>sys.stderr, 'warn: abspath key', self.key
        segs=[s.lstrip('/') for s in [self.bucket._fs_root, self.bucket.name, self.key]]
        return os.path.join(*segs)

class Bucket(driver.Bucket):

    def imp_init(self, session, name, create=True):
        self._fs_root=session._fs_root

class Session(driver.Session):

    bucket_class=Bucket
    entry_class=Entry

    def imp_init(self, token, secret):
        self._fs_root=token
