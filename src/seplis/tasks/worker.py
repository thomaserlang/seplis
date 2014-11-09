from seplis import config_load, config
from rq import Connection, Queue, Worker

def main():
    from seplis.api.connections import database     
    with Connection(connection=database.queue_redis):
        w = Worker(database.queue)
        if config['sentry_dsn']:
            from raven import Client
            from rq.contrib.sentry import register_sentry
            client = Client('sync+'+config['sentry_dsn'])
            register_sentry(client, w)    
        w.work()

if __name__ == '__main__':
    config_load()   
    main()