
all:

clean:
	rm -f *.pyc


python=$(HOME)/ve/bin/python
#python=python

bucket=cdn.ikulist.me

tt:
	find x.img -name '*.jpg' \
	| $(python) baketu.py pushs $(bucket) --access=./x.s3.cred --name=md5 --log=.log \
		--dryrun

s3:
	find x.img -name '*.jpg' \
	| $(python) baketu.py pushs $(bucket) \
		--access=file://./x.s3.cred \
		--driver=s3 \
		--name=/test/{md5}{suffix} \
		--force

fs:
	find x.img -name '*.jpg' \
	| $(python) baketu.py pushs $(bucket) \
		--access='str://{"token":"./x.root"}' \
		--driver=fs \
		--name=./test/{md5}{suffix} \
		--force

url=http://$(bucket)/test/a5f8a79fc8bb70389378015b0eb125a0
fetch:
	curl -D/dev/stdout $(url)

t:
	$(python) baketu.py push \
		$(bucket) \
		'str://{"token":"./x.root"}' \
		./test/{md5}{suffix} \
		--driver=fs \
		x.img/*.jpg

fs-c:
	$(python) baketu.py pushc example/test-fs.bkt x.img/*.jpg

s3-c:
	$(python) baketu/baketu.py pushc ./x.test-s3.bkt x.img/*.jpg

cc:
	$(HOME)/ve/bin/baketu pushc ./x.test-s3.bkt x.img/*.jpg

install:
	rm -fr /home/tengu/ve/lib/python2.7/site-packages/*baketu*
	$(python) setup.py install

c:
	$(HOME)/ve/bin/baketu
