Technologies in general = python + mysql + virtualenv.

Firstly, set up mysql, create database "cragapp" and user for work with this database.
In ./dbinit.py, ./cragapp.py and ./cragloop.py are line like

```python
db = MySQLdb.connect(host="localhost", user="root", passwd="passwd", db="cragapp", charset='utf8')
```
Change user and passwd attributes to user you create.

Then install pip, and virtualenv via pip:

```bash
$ yum install python-pip
$ pip install virtualenv
```

Then cd into craigslist-poster directory and type:

```bash
$ virtualenv venv
$ . venv/bin/activate
$ pip install flask
$ pip install mysql
$ pip install pysocks
$ pip install sqlalchemy
$ python dbinit.py
```

Setup is done. Run application:

```bash
$ python cragapp.py
```

And go on http://your.server.ip.adr:5000

