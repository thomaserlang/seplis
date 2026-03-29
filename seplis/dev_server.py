from subprocess import list2cmdline

from honcho.manager import Manager


def main() -> None:
    start = [
        ('npm', ['npm', 'run', 'dev'], 'seplis-ui'),
        ('api', ['python', 'seplis/runner.py', 'api'], '.'),
        ('worker', ['python', 'seplis/runner.py', 'worker'], '.'),
    ]

    manager = Manager()
    for name, cmd, cwd in start:
        manager.add_process(  # type: ignore
            name,
            list2cmdline(cmd),
            quiet=False,
            cwd=cwd,
        )

    manager.loop()


if __name__ == '__main__':
    main()
