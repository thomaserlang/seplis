seplis
======


# Installation

**Debian Jessie**

Supported Python versions: Python>=3.3


```shell
sudo apt-get install python3 python3-dev build-essential supervisor 
```
 
Install Redis: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis    

Install Elasticsearch: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html

Install MySQL (Percona/MariaDB). Postgres might work, not tested!

Supervisor config:

```
[program:seplis-web]
process_name = seplis-web-%(process_num)s
directory=/home/te/virtualenv/seplis/
command=/home/te/virtualenv/seplis/bin/seplis web --port=%(process_num)s
numprocs=2
numprocs_start=8000
autostart=true
autorestart=true
redirect_stderr=true
user=seplis

[program:seplis-api]
process_name = seplis-api-%(process_num)s
directory=/home/te/virtualenv/seplis/
command=/home/te/virtualenv/seplis/bin/seplis api --port=%(process_num)s
numprocs=8
numprocs_start=9000
autostart=true
autorestart=true
redirect_stderr=true
user=seplis
```

Create a schema:

```
CREATE schema seplis;
```

Create a database user and give it access to the schema:

```
CREATE USER 'seplis'@'localhost' IDENTIFIED BY 'mypass';

GRANT ALL ON seplis.* TO 'seplis'@'localhost';
```

Create a user for seplis to run as:

```
sudo adduser --quiet --system --no-create-home --disabled-password --disabled-login --group seplis
```

Setup and activate the virtualenv:

```
virtualenv -p python3 ~/virtualenv/seplis
source ~/virtualenv/seplis/bin/activate
```

Install SEPLIS:

    pip install https://github.com/thomaserlang/seplis/archive/master.zip --upgrade
    

Create the log directory:

```
sudo mkdir /var/log/seplis
sudo chown -R seplis:seplis /var/log/seplis
```
    

Add the config to `/etc/seplis.yaml`. Example:

```yml
web:
    url: http://example.net
    cookie_secret: CHANGE ME
api:
    url: http://api.example.net
    elasticsearch: localhost:9200
    database: mysql+pymysql://seplis:mypass@127.0.0.1/seplis
    redis:
        ip: localhost
        port: 6379
logging:
    level: info
    path: /var/log/seplis
client:
    id: client id
```
    
Upgrade the database:

    seplis upgrade
