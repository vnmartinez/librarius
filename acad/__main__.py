import sys

from acad import __version__


def _main() -> int:
    if "--versao" in sys.argv[1:]:
        print(__version__)
        return 0
    try:
        from acad.cli import main
    except ImportError:
        print(__version__)
        return 0
    return main()


sys.exit(_main())
