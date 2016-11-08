import os, sys
from subprocess import list2cmdline
from honcho.manager import Manager
from seplis.logger import logger

def main():
    src_path = os.path.dirname(os.path.realpath(__file__))
    base_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
    node_bin = os.path.join(base_path, 'node_modules/.bin')

    start = [
        ('api', ['python', 'runner.py', 'api'], src_path),
        ('web', ['python', 'runner.py', 'web'], src_path),
        ('play_server', ['python', 'runner.py', 'play_server'], src_path),
        ('worker', ['python', 'runner.py', 'worker'], src_path),
        #('webpack', [node_bin+'/webpack', '-d', '-w'], base_path),
        ('webpack-dev-server', [node_bin+'/webpack-dev-server', '--host', '0.0.0.0'], base_path),
    ]

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