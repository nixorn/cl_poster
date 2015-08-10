Technologies in general = python + mysql + virtualenv.

Firstly, set up mysql, create database "cragapp" and user for work with this database.
In ./database.py are line like

```python
engine = create_engine('mysql+mysqldb://user:passwd@localhost/cragapp', convert_unicode=True)
```
Change user and passwd attributes to user you create.

Then epel,some python dependencies,pip, and virtualenv via pip:

```bash
$ yum -y install epel-release
$ yum -y install gcc python-devel freetds-devel python-pip libffi-devel libssl-devel libxml2-devel libxslt1-devel libxml2-python python-lxml libxslt-devel
$ yum install python-pip
$ pip install virtualenv
```

Then cd into craigslist-poster directory and type:

```bash
$ virtualenv venv
$ . venv/bin/activate
$ pip install flask
$ pip install pymysql
$ pip install pysocks
$ pip install sqlalchemy
$ pip install tornado
$ pip install scrapy
$ pip install service_identity
$ python dbinit.py
```

Setup is done. Run application:

```bash
$ python tornado_deploy.py
```

And go on http://your.server.ip.adr:5000

