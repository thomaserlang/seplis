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
command=/home/te/virtualenv/seplis/bin/seplis --config=/etc/seplis_conf.yml web --port=%(process_num)s
numprocs=2
numprocs_start=8000
autostart=true
autorestart=true
redirect_stderr=true
user=seplis

[program:seplis-api]
process_name = seplis-web-%(process_num)s
directory=/home/te/virtualenv/seplis/
command=/home/te/virtualenv/seplis/bin/seplis --config=/etc/seplis_conf.yml api --port=%(process_num)s
numprocs=8
numprocs_start=9000
autostart=true
autorestart=true
redirect_stderr=true
user=seplis
```

Create a schema:

```
CREATE schema SEPLIS;
```

Create a database user and give it access to the schema:

```
CREATE USER 'seplis'@'localhost' IDENTIFIED BY 'mypass';

GRANT SELECT, INSERT, UPDATE, DELETE ON seplis.* TO 'seplis'@'localhost';
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
    
Add the config to `/etc/seplis_conf.yml`. Example:

```yml
web:
    url: "http://example.net"
    api_url: "http://api.example.net/1"
    client_id: "client_id"
    cookie_secret: "secret"
api:
    url: "http://api.example.net"
database:
    url: "mysql+pymysql://seplis:mypass@127.0.0.1/seplis"
redis:
    ip: localhost
    port: 6379
logging:
    level: info
    path: /var/log/seplis
debug: true
elasticsearch: localhost:9200
```
    
Upgrade the database:

    seplis --config=/etc/seplis_conf.yml upgrade
