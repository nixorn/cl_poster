Technologies in general = sqlite + python + virtualenv + flask + sqlalchemy + scrapy + requests.


Firstly install epel, scl, python27, install python dependencies,pip, and virtualenv via pip:

```bash
yum -y install epel-release
yum install centos-release-SCL
yum install python27
yum -y install gcc python-devel freetds-devel python-pip libffi-devel libssl-devel libxml2-devel libxslt1-devel libxml2-python python-lxml libxslt-devel
yum install python-pip
pip install virtualenv
```



Then cd into craigslist-poster directory and type:
```bash
virtualenv venv
. venv/bin/activate
pip install flask
pip install pymysql
pip install pysocks
pip install sqlalchemy
pip install tornado
pip install scrapy
pip install requests
pip install service_identity
pip install imbox
pip install twilio
python2.7 dbinit.py
```

Setup python 2.7 for this session and reactivate virtualenv:
```bash
scl enable python27 'which python'
scl enable python27 'python --version'
scl enable python27 bash
source /opt/rh/python27/enable
. venv/bin/activate
```

Run application:

```bash

python2.7 tornado_deploy.py
```

And go on http://your.server.ip.adr:5000

