import logging, time, asyncio
from tornado import ioloop
from seplis import config

SHUTDOWN_WAIT = 60 # seconds
def sig_handler(server, application, sig, frame):
    io_loop = ioloop.IOLoop.instance()
    if hasattr(application, 'shutting_down') and application.shutting_down == True:
        io_loop.stop()
        return

    application.shutting_down = True

    def stop_loop(server, deadline: float):
        now = time.time()
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
        if (now < deadline and len(tasks) > 0) and not config.data.debug:
            logging.debug(f'Awaiting {len(tasks)} pending tasks {tasks}')
            io_loop.add_timeout(now + 1, stop_loop, server, deadline)
            return

        pending_connection = len(server._connections)
        if (now < deadline and pending_connection > 0) and not config.data.debug:
            logging.debug(f'Waiting on {pending_connection} connections to finish {server._connections}')
            io_loop.add_timeout(now + 1, stop_loop, server, deadline)
        else:
            logging.debug(f'Shutting down. {pending_connection} connections left')
            io_loop.stop()

    def shutdown():
        logging.debug(f'Waiting for up to {SHUTDOWN_WAIT} seconds to shutdown ...')
        try:
            stop_loop(server, time.time() + SHUTDOWN_WAIT)
        except BaseException as e:
            logging.error(f'Error trying to shutdown Tornado: {str(e)}')

    io_loop.add_callback_from_signal(shutdown)