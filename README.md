# microblog

Flask-MySQL(Python 2.7) based minimal blog application uses OAuth for Twitter and Facebook.

Use run.py to run the application

Certificate verification

It is highly recommended to always use SSL certificate verification. By default, urllib3 does not verify HTTPS requests.

In order to enable verification you will need a set of root certificates. The easiest and most reliable method is to use the certifi package which provides Mozilla’s root certificate bundle: can cause SSL warnings SNIMissingWarning and InsecurePlatformWarning

Solution: 

sudo apt-get install build-essential libssl-dev libffi-dev python-dev 

https://urllib3.readthedocs.io/en/latest/user-guide.html#certificate-verification-in-python-2


