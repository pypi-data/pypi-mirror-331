# Copyright (c) 2018 Cobus Nel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
import shlex
import textwrap
from abc import ABCMeta, abstractmethod

from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as echo
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.history import FileHistory
from ..exceptions import (
    DKitApplicationException, DKitArgumentException, DKitShellException
)
from .console import to_columns


"""
Prompt Toolkit extensions
"""


class ProxyCmd(metaclass=ABCMeta):

    cmd = ""

    @abstractmethod
    def run(self, args):
        pass

    def complete(self, tokens, document):
        yield from []

    def get_help(self):
        return self.__doc__

    def echo(self, *values):
        """print to console

        print using prompt toolkit print_formatted_text
        """
        echo(*values)


class CmdCompleter(Completer):
    """
    Command dispatcher and completer
    """
    cmd_map = {}

    def __init__(self, lst_commands):
        # self.cmd_map["clear"] = ClearCmd()
        # self.cmd_map["help"] = HelpCmd(self),
        self.cmd_map.update({i.cmd: i for i in lst_commands})

    @property
    def commands(self):
        return sorted(["exit"] + list(self.cmd_map.keys()))

    def get_completions(self, document, complete_event):
        """
        Main completer entry point
        """
        line = document.current_line_before_cursor
        if complete_event.completion_requested:

            try:
                tokens = shlex.split(line)
                if line.endswith(" "):
                    tokens.append("")
            except ValueError:
                return

            # provide  a list of commands
            if len(tokens) == 0:
                yield from (Completion(i, 0) for i in self.commands)

            # complete a command
            if len(tokens) == 1:
                yield from self.complete_commands(line)

            # complete commands parameters
            elif len(tokens) > 1:
                cmd = tokens[0]
                if cmd in self.commands:
                    runner = self.cmd_map[cmd]
                    yield from runner.complete(tokens, document)

    def complete_commands(self, line):
        completions = [i for i in self.commands if i.startswith(line)]
        pos = len(line)
        yield from (Completion(i, start_position=-pos) for i in completions)


class SetCmd(ProxyCmd):

    def __init__(self, model, initial=None):
        self.model = model

    def run(self, args):
        pass


class CmdApplication(object):
    """
    Abstract Base Class for Async Command Applications

    args:
        lst_commands: list of commmands
        debug: True to defeat error handling
        history_file: filename for history (ignored if None)
    """
    def __init__(self, commands=None, debug=False, history_file: str = None,
                 settings=None, default_cmd=None):
        self.debug = debug
        self.completer = CmdCompleter([])
        self.quit = False
        self.history_file = history_file
        self.commands = commands
        self.settings = settings
        self.default_cmd = default_cmd
        if self.commands is not None:
            self.add_commands(self.commands)

    def _process_line(self):
        # Complete command and options
        str_line = self.session.prompt(
            "$ ",
            completer=self.completer,
            mouse_support=False,
            # history=history,
        )

        try:
            line = shlex.split(str_line)
        except ValueError:
            return

        if len(line) > 0:
            command = line[0]

            # exit
            if command.lower() == 'exit':
                echo("Good bye..")
                self.quit = True
                return

            if command not in self.completer.cmd_map:
                command = self.default_cmd
                line.insert(0, self.default_cmd)

            # run registered command
            if command in self.completer.cmd_map:
                runner = self.completer.cmd_map[command]
                runner.run(line)
            else:
                raise DKitShellException(f"Invalid command: {command}")

    def run(self):
        """
        Run application
        """
        self.session = self._make_session()
        # history = InMemoryHistory()
        if self.debug:
            while not self.quit:
                self._process_line()
        else:
            while not self.quit:
                try:
                    with patch_stdout():
                        self._process_line()
                except (
                    AssertionError,
                    FileNotFoundError,
                    IndexError,
                    ValueError,
                    argparse.ArgumentError,
                    DKitApplicationException,
                    DKitArgumentException,
                    DKitShellException,
                ) as E:
                    echo(str(E))
                except KeyError as E:
                    echo("Invalid Key: {}".format(E))
                except (EOFError, KeyboardInterrupt):
                    return

    def _make_session(self):
        if self.history_file:
            history = FileHistory(self.history_file)
        else:
            history = None
        return PromptSession(history=history)

    def add_commands(self, commands):
        self.completer.cmd_map.update(
            {i.cmd: i for i in commands}
        )


class ClearCmd(ProxyCmd):
    """
    clear screen
    """
    cmd = "clear"

    def run(self, args):
        clear()


class HelpCmd(ProxyCmd):
    """
    show help

    example usage:
    > help
    > help mv
    """
    cmd = "help"

    def __init__(self, completer):
        self.completer = completer
        self.map_commands = completer.cmd_map

    def complete(self, tokens, document):
        token = tokens[-1]
        length = len(token)
        yield from (
            Completion(i, -length)
            for i in sorted(self.map_commands.keys())
            if i.startswith(token)
        )

    def run(self, args):
        if len(args) == 1:
            commands = list(self.map_commands.keys())
            self.echo(to_columns(commands))
        else:
            cmd = args[-1]
            help_text = self.map_commands[cmd].get_help()
            if help_text is not None:
                help_text = textwrap.dedent(help_text).strip()
                self.echo(help_text)
                self.echo()
            else:
                self.echo("No help available")
