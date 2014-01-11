#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import time
import json
import hashlib
import boto.s3.connection
import boto.exception
import boto.s3.key
import driver

class Entry(driver.Entry):

    def imp_init(self, bucket, key):
        self.s3_key=boto.s3.key.Key(bucket.s3_bucket)
        self.s3_key.key=key

    def data(self):
        return self.s3_key.read()

    def set_data(self, data, content_type=None, force=False):
        """saves the data to the remote location"""

        if content_type:
            # print 'content_type:', self.s3_key.key, content_type
            self.s3_key.content_type=content_type
        self.s3_key.set_contents_from_string(data, replace=force)

class Bucket(driver.Bucket):

    def imp_init(self, session, name, create=True):
        try:
            self.s3_bucket=session.s3_conn.get_bucket(name)
        except boto.exception.S3ResponseError, e:
            if e.error_code==404 and create:
                self.s3_bucket=session.s3_conn.create_bucket(name)
            else:
                print >>sys.stderr, 'no bucket', name, 'in', session, create
                raise

class Session(driver.Session):

    bucket_class=Bucket
    entry_class=Entry

    def imp_init(self, token, secret):
        self.s3_conn=boto.s3.connection.S3Connection(token, secret)
