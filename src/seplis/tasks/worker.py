import sentry_sdk
from sentry_sdk.integrations.rq import RqIntegration
from seplis import config_load, config
from rq import Connection, Worker

def main():
    from seplis.api.connections import database     
    with Connection(connection=database.queue_redis):
        w = Worker(database.queue)
        if config.data.sentry_dsn:
            sentry_sdk.init(
                config.data.sentry_dsn,
                integrations=[RqIntegration()]
            )
        w.work()

if __name__ == '__main__':
    config_load()   
    main()