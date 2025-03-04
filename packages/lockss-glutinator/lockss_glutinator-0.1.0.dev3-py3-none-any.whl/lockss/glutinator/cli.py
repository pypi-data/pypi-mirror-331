#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
from pathlib import Path
import rich_argparse

import lockss.glutinator
from . import __copyright__, __license__, __version__
from .app import GlutinatorApp
from .item import load_sample_data


class GlutinatorCli(object):

    PROG = 'glutinator'

    def __init__(self):
        super().__init__()
        self._app = GlutinatorApp()
        self._args = None

    def run(self):
        self._make_parser()
        self._args = self._parser.parse_args()
        if self._args.debug_cli:
            print(self._args)
        self._args.fun()

    def _copyright(self):
        print(__copyright__)

    def _generate_static_site(self):
        outdir = '/tmp/emh'
        from .item import Item
        from collections import ChainMap
        import importlib.resources
        import os
        import shutil
        from jinja2 import Environment, PackageLoader, select_autoescape
        publishers = load_sample_data()
        env = Environment(loader=PackageLoader("lockss.glutinator.resources.editorial"),
                          autoescape=select_autoescape())
        home_item = Item(None)
        home_item.kind = 'NONE'
        home_item.title = 'Welcome'
        home_item.children = publishers
        home_item.path = lambda s: '/index.html'
        home_template = env.get_template("home.html")
        home_context = ChainMap(dict(breadcrumbs=[],
                                     current=home_item,
#                                     is_local=True,
#                                     local_base=f'file://{outdir}',
                                     menu=[home_item.children]))
        home_template.stream(home_context).dump(f'{outdir}{home_item.path(None)}')
        for publisher in publishers:
            publisher_template = env.get_template("publisher.html")
            publisher_context = home_context.new_child(dict(breadcrumbs=[*home_context['breadcrumbs'], publisher],
                                                            current=publisher,
                                                            menu=[*home_context['menu'], publisher.children]))
            os.makedirs(os.path.dirname(f'{outdir}{publisher.path()}'), exist_ok=True)
            publisher_template.stream(publisher_context).dump(f'{outdir}{publisher.path()}')
            for journal in publisher.children:
                journal_template = env.get_template("journal.html")
                journal_context = publisher_context.new_child(dict(breadcrumbs=[*publisher_context['breadcrumbs'], journal],
                                                              current=journal,
                                                              menu=[*publisher_context['menu'], journal.children]))
                os.makedirs(os.path.dirname(f'{outdir}{journal.path()}'), exist_ok=True)
                journal_template.stream(journal_context).dump(f'{outdir}{journal.path()}')
                for volume in journal.children:
                    volume_template = env.get_template("volume.html")
                    volume_context = journal_context.new_child(
                        dict(breadcrumbs=[*journal_context['breadcrumbs'], volume],
                             current=volume,
                             menu=[*journal_context['menu'], volume.children]))
                    os.makedirs(os.path.dirname(f'{outdir}{volume.path()}'), exist_ok=True)
                    volume_template.stream(volume_context).dump(f'{outdir}{volume.path()}')
                    for issue in volume.children:
                        issue_template = env.get_template("issue.html")
                        issue_context = volume_context.new_child(
                            dict(breadcrumbs=[*volume_context['breadcrumbs'], issue],
                                 current=issue)) # NOTE: same menu
                        os.makedirs(os.path.dirname(f'{outdir}{issue.path()}'), exist_ok=True)
                        issue_template.stream(issue_context).dump(f'{outdir}{issue.path()}')
                        for article in issue.children:
                            article_template = env.get_template("article.html")
                            article_context = issue_context.new_child(
                                dict(breadcrumbs=[*issue_context['breadcrumbs'], article],
                                     current=article))  # NOTE: same menu
                            os.makedirs(os.path.dirname(f'{outdir}{article.path()}'), exist_ok=True)
                            article_template.stream(article_context).dump(f'{outdir}{article.path()}')

        with importlib.resources.path(lockss.glutinator.resources.editorial, 'assets') as assets:
            shutil.copytree(assets, f'{outdir}/assets', dirs_exist_ok=True)

    def _license(self):
        print(__license__)

    def _make_option_configuration(self, container):
        container.add_argument('--configuration', '-c',
                               metavar='FILE',
                               type=Path,
                               default='glutinator.yaml',
                               help='read configuration from FILE (default: %(default)s)')

    def _make_option_debug_cli(self, container):
        container.add_argument('--debug-cli',
                               action='store_true',
                               help='print the result of parsing command line arguments')

    def _make_parser(self):
        for cls in [rich_argparse.RichHelpFormatter]:
            cls.styles.update({
                'argparse.args': f'bold {cls.styles["argparse.args"]}',
                'argparse.groups': f'bold {cls.styles["argparse.groups"]}',
                'argparse.metavar': f'bold {cls.styles["argparse.metavar"]}',
                'argparse.prog': f'bold {cls.styles["argparse.prog"]}',
            })
        self._parser = argparse.ArgumentParser(prog=GlutinatorCli.PROG,
                                               formatter_class=rich_argparse.RichHelpFormatter)
        self._subparsers = self._parser.add_subparsers(title='commands',
                                                       description="Add --help to see the command's own help message.",
                                                       # With subparsers, metavar is also used as the heading of the column of subcommands
                                                       metavar='COMMAND',
                                                       # With subparsers, help is used as the heading of the column of subcommand descriptions
                                                       help='DESCRIPTION')
        self._make_option_debug_cli(self._parser)
        self._make_parser_copyright(self._subparsers)
        self._make_parser_generate_static_site(self._subparsers)
        self._make_parser_license(self._subparsers)
        self._make_parser_unpack_sources(self._subparsers)
        self._make_parser_usage(self._subparsers)
        self._make_parser_version(self._subparsers)

    def _make_parser_copyright(self, container):
        parser = container.add_parser('copyright',
                                      description='Show copyright and exit.',
                                      help='show copyright and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._copyright)

    def _make_parser_generate_static_site(self, container):
        parser = container.add_parser('generate-static-site', aliases=['gss'],
                                      description='Generate static site from sources.',
                                      help='generate static site from sources',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._generate_static_site)

    def _make_parser_license(self, container):
        parser = container.add_parser('license',
                                      description='Show license and exit.',
                                      help='show license and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._license)

    def _make_parser_unpack_sources(self, container):
        parser = container.add_parser('unpack-sources', aliases=['us'],
                                      description='Re-assemble and unpack source directories.',
                                      help='re-assemble and unpack source directories',
                                      formatter_class=self._parser.formatter_class)
        self._make_option_configuration(parser)
        parser.set_defaults(fun=self._unpack_sources)

    def _make_parser_usage(self, container):
        parser = container.add_parser('usage',
                                      description='Show detailed usage and exit.',
                                      help='show detailed usage and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._usage)

    def _make_parser_version(self, container):
        parser = container.add_parser('version',
                                      description='Show version and exit.',
                                      help='show version and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._version)

    def _unpack_sources(self):
        self._app.load_configuration(self._args.configuration)
        self._app.unpack_sources()

    def _usage(self):
        self._parser.print_usage()
        print()
        uniq = set()
        for cmd, par in self._subparsers.choices.items():
            if par not in uniq:
                uniq.add(par)
                for s in par.format_usage().split('\n'):
                    usage = 'usage: '
                    print(f'{" " * len(usage)}{s[len(usage):]}' if s.startswith(usage) else s)

    def _version(self):
        print(__version__)

def main():
    GlutinatorCli().run()

if __name__ == '__main__':
    main()
