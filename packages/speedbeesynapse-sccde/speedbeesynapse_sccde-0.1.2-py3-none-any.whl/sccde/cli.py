"""SpeeDBeeSynapse custom component development environment tool."""
import argparse
from pathlib import Path

from . import main as sccde_main
from . import pack, utils


def main() -> None:
    """Do main process."""
    parser = argparse.ArgumentParser(description='SpeeDBee Synapse Customcomponent Development tool')
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser('init', help='see `init -h`')
    init_parser.add_argument('-n', '--name', required=False, type=str, default='Custom component package example', help='package name')
    init_parser.add_argument('-l', '--sample-language',
                             required=False, type=str,
                             choices=['c', 'python'],
                             default='python', help='sample component type')
    init_parser.add_argument('-t', '--sample-type',
                             required=False, type=str,
                             choices=['collector', 'serializer', 'emitter'],
                             default='collector', help='sample component type')
    init_parser.set_defaults(handler=sccde_init)

    add_parser = subparsers.add_parser('add', help='see `make-package -h`')
    add_parser.add_argument('-n', '--name', required=False, type=str, default='sample1', help='component name')
    add_parser.add_argument('-l', '--sample-language',
                            required=False, type=str,
                            choices=['c', 'python'],
                            default='python', help='sample component type')
    add_parser.add_argument('-t', '--sample-type',
                            required=False, type=str,
                            choices=['collector', 'serializer', 'emitter'],
                            default='collector', help='sample component type')
    add_parser.set_defaults(handler=sccde_add)

    make_package_parser = subparsers.add_parser('make-package', help='see `make-package -h`')
    make_package_parser.add_argument('-o', '--out', required=False, type=str, default=None, help='output dir')
    make_package_parser.set_defaults(handler=sccde_make_package)

    serve_parser = subparsers.add_parser('serve', help='see `serve -h`')
    serve_parser.add_argument('-b', '--bind', required=False, type=str, default='127.0.0.1', help='ip address')
    serve_parser.add_argument('-p', '--port', required=False, type=int, default=8121, help='port number')
    serve_parser.set_defaults(handler=sccde_serve)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


def sccde_init(args: argparse.Namespace) -> None:
    """Handle 'init' subcommand."""
    info_path = Path('scc-info.json')
    if info_path.exists():
        utils.print_error('Project is already initialized')
        return

    sccde_main.init(info_path, args.name, args.sample_language, args.sample_type)


def sccde_add(args: argparse.Namespace) -> None:
    """Handle 'add' subcommand."""
    info_path = Path('scc-info.json')
    if not info_path.exists():
        utils.print_error('Project is not initialized yet')
        return

    sccde_main.add_sample(info_path, args.sample_language, args.sample_type)


def sccde_make_package(args: argparse.Namespace) -> None:
    """Handle 'make-package' subcommand."""
    info_path = Path('scc-info.json')
    if not info_path.exists():
        utils.print_error('Project is not initialized yet')
        return

    pack.make_package(info_path, args.out)


def sccde_serve(args: argparse.Namespace) -> None:
    """Handle 'serve' subcommand."""
    utils.print_info('serve', vars(args))


if __name__ == '__main__':
    main()
