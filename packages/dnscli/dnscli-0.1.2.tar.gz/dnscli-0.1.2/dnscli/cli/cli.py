#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click

from ..version import __version__
from .config import config
from .domain import domain
from .record import record

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__, prog_name='dnscli', message='%(prog)s %(version)s')
def cli():
    """dnscli - 一个用于管理多云DNS记录的命令行工具"""
    pass

# 添加子命令
cli.add_command(config)
cli.add_command(domain)
cli.add_command(record)

if __name__ == '__main__':
    cli()