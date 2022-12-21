import os
from subprocess import list2cmdline
from honcho.manager import Manager

def main():
    src_path = os.path.dirname(os.path.realpath(__file__))

    start = [
        ('api', ['python', 'runner.py', 'api'], src_path),
        ('web', ['python', 'runner.py', 'web'], src_path),
        #('play-server', ['python', 'runner.py', 'play-server'], src_path),
        #('worker', ['python', 'runner.py', 'worker', '-n', '8'], src_path),
        #('play-scan-watch', ['python', 'runner.py', 'play-scan-watch'], src_path),
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

if __name__ == '__main__':
    main()