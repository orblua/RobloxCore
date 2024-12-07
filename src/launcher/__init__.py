import launcher.subparsers._logic as sub_logic
import launcher.routines._logic as routine_logic

import sys
import pathlib
import shlex
import argparse
import traceback
from importlib import import_module


def import_subparser_dir(d: str):
    for f in pathlib.Path(__file__).parent.glob(f"subparsers/{d}/*.py"):
        if "__" in f.stem:
            continue
        import_module(f'.subparsers.{d}.{f.stem}', __package__)


import_subparser_dir('args_launch_mode')
import_subparser_dir('args_aux')


def parse_arg_list(args: list[str] | None) -> list:
    '''
    Generates a list of routines from `launcher/subparser` scripts, filtering by the `mode` command-line parameter.
    '''
    parser = argparse.ArgumentParser()
    mode_parser = parser.add_subparsers(
        dest='mode',
    )
    sub_parsers = {
        m: mode_parser.add_parser(n, add_help=False)
        for n, m in sub_logic.MODE_ALIASES.items()
    }

    # Begins populating the argument namespace; errors aren't thrown because the subparser arguments aren't added yet.
    args_namespace = parser.parse_known_args(args)[0]

    if not args_namespace.mode:
        parser.print_help()
        parser.exit(1)

    mode = sub_logic.MODE_ALIASES[args_namespace.mode]
    chosen_sub_parser = sub_parsers[mode]

    # Adds parseable arguments for `chosen_sub_parser` which exist only under the current launch mode.
    sub_logic.call_subparser(
        sub_logic.ADD_MODE_ARGS,
        mode,
        parser,
        chosen_sub_parser,
    )

    # Adds parseable arguments, which exist under all launch modes, into `chosen_sub_parser`.
    sub_logic.call_auxs(
        sub_logic.ADD_MODE_ARGS,
        mode,
        parser,
        chosen_sub_parser,
    )

    # Adds '--help' argument manually after the high-level parser called 'parse_known_args'.
    # Otherwise, the program would stop earlier and the help-text would be incomplete.
    # The `-h` flag is replaced with `-?` here because we're using `-h` to signify `--rcc_host`.
    chosen_sub_parser.add_argument(
        '--help', '-?',
        help='show this help message and exit',
        action='help',
    )

    # Completes populating the argument namespace, with errors being thrown if an argument is invalid.
    try:
        args_namespace = parser.parse_args(args)
    except argparse.ArgumentError as x:
        print(x)
        chosen_sub_parser.print_help()
        parser.exit(1)

    routine_args_list = sub_logic.call_subparser(
        sub_logic.SERIALISE_ARGS,
        mode,
        parser,
        args_namespace,
    )

    routine_args_list += sub_logic.call_auxs(
        sub_logic.SERIALISE_ARGS,
        mode,
        args_namespace,
        routine_args_list,
    )

    return routine_args_list


def process(args: list[str] | None = None) -> None:
    '''
    Highest-level main function which takes a list of arguments
    and does everything in one go.
    '''
    if args is None:
        args = sys.argv[1:]

    def perform_with_args(args: list[str]):
        return routine_logic.routine(*parse_arg_list(args)).wait()

    if len(args) > 0:
        try:
            perform_with_args(args)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            traceback.print_exc()
            print(e)
        finally:
            return

    try:
        while True:
            try:
                arg_str = input(
                    "Enter your command-line arguments [Ctrl+C to quit]: ",
                )
                perform_with_args(shlex.split(arg_str))
            except KeyboardInterrupt:
                pass
            except Exception as e:
                traceback.print_exc()
                print(e)
    except KeyboardInterrupt:
        pass
