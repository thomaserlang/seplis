from subprocess import list2cmdline
from honcho.manager import Manager

def main():
    start = [
        ('api', ['python', 'seplis/runner.py', 'api']),
        ('web', ['python', 'seplis/runner.py', 'web']),
        ('worker', ['python', 'seplis/runner.py', 'worker']),
    ]

    manager = Manager()
    for name, cmd in start:
        manager.add_process(
            name, 
            list2cmdline(cmd),
            quiet=False, 
        )

    manager.loop()

if __name__ == '__main__':
    main()