import os, sys
from subprocess import list2cmdline
from honcho.manager import Manager
from seplis.logger import logger

watchdog_installed = False
try:
    import watchdog
    watchdog_installed = True
except:
    pass

def main():
    src_path = os.path.dirname(os.path.realpath(__file__))
    base_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )

    start = [
        ('api', ['python', 'runner.py', 'api'], src_path),
        ('web', ['python', 'runner.py', 'web'], src_path),
        ('play-server', ['python', 'runner.py', 'play-server'], src_path),
        ('worker', ['python', 'runner.py', 'worker'], src_path),
    ]
    if watchdog_installed:
        start.append(
            ('play-scan-watch', ['python', 'runner.py', 'play-scan-watch'], src_path),
        )

    manager = Manager()
    for name, cmd, cwd in start:
        manager.add_process(
            name, 
            list2cmdline(cmd),
            quiet=False, 
            cwd=cwd,
        )

    manager.loop()
    sys.exit(manager.returncode)

if __name__ == '__main__':
    main()