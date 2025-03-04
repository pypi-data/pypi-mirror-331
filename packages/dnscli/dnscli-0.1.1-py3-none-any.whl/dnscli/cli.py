#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import yaml
import os
from prettytable import PrettyTable
from .providers import AliyunDNS, TencentDNS, CloudflareDNS
from .config import update_provider_config, load_config, save_config, get_provider_config
from .version import __version__

CONFIG_FILE = os.path.expanduser('~/.dnscli/config.yaml')

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__, prog_name='dnscli', message='%(prog)s %(version)s')
def cli():
    """dnscli - 一个用于管理多云DNS记录的命令行工具"""
    pass

@cli.group(context_settings=dict(help_option_names=["-h", "--help"]))
def config():
    """配置管理相关命令"""
    pass

@cli.group(context_settings=dict(help_option_names=["-h", "--help"]))
def domain():
    """域名管理相关命令"""
    pass

@cli.group(context_settings=dict(help_option_names=["-h", "--help"]))
def record():
    """DNS记录管理相关命令"""
    pass

@domain.command()
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
def list(provider):
    """列出所有域名"""
    try:
        provider_config = get_provider_config(provider)
        provider_type = provider_config['type']
        credentials = provider_config['credentials']

        # 根据服务商类型创建对应的DNS提供商实例
        if provider_type == 'aliyun':
            dns = AliyunDNS(**credentials)
        elif provider_type == 'tencent':
            dns = TencentDNS(**credentials)
        elif provider_type == 'cloudflare':
            dns = CloudflareDNS(**credentials)
        else:
            click.echo(f'不支持的DNS服务商类型：{provider_type}')
            return

        # 获取域名列表
        domains = dns.list_domains()

        # 创建表格并显示域名信息
        table = PrettyTable()
        table.field_names = ['域名', '状态', '创建时间', '更新时间']
        for domain in domains:
            table.add_row([
                domain['name'],
                domain['status'],
                domain.get('created_at', '-'),
                domain.get('updated_at', '-')
            ])
        click.echo(table)

    except Exception as e:
        click.echo(f'获取域名列表失败：{str(e)}')
        return

@config.command()
def example():
    """生成示例配置文件"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'configs': {
                'default': {
                    'type': 'aliyun',
                    'credentials': {
                        'access_key_id': '',
                        'access_key_secret': ''
                    }
                },
                'tencent': {
                    'type': 'tencent',
                    'credentials': {
                        'secret_id': '',
                        'secret_key': ''
                    }
                }
            },
            'default': 'default'
        }
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        click.echo(f'配置文件已创建: {CONFIG_FILE}')
    else:
        click.echo('配置文件已存在')

@config.command()
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
def configure(provider):
    """交互式配置DNS服务商信息"""
    # 输入配置名称
    config_name = click.prompt('请输入配置名称')

    if provider:
        provider_type = provider
    else:
        # 选择DNS服务商类型
        provider_type = click.prompt(
            '请选择DNS服务商类型',
            type=click.Choice(['aliyun', 'tencent', 'cloudflare']),
            show_choices=True
        )

    # 根据不同服务商类型获取凭证信息
    if provider_type == 'aliyun':
        credentials = {
            'access_key_id': click.prompt('请输入Access Key ID'),
            'access_key_secret': click.prompt('请输入Access Key Secret', hide_input=True)
        }
    elif provider_type == 'tencent':
        credentials = {
            'secret_id': click.prompt('请输入Secret ID'),
            'secret_key': click.prompt('请输入Secret Key', hide_input=True)
        }
    else:  # cloudflare
        credentials = {
            'api_token': click.prompt('请输入API Token', hide_input=True)
        }

    # 更新配置
    provider_config = {
        'type': provider_type,
        'credentials': credentials
    }
    config = load_config()
    if 'configs' not in config:
        config['configs'] = {}
    config['configs'][config_name] = provider_config

    # 询问是否设置为默认配置
    if click.confirm('是否将此配置设置为默认配置？'):
        config['default'] = config_name
    
    save_config(config)
    click.echo(f'配置 {config_name} 已更新')
    if config.get('default') == config_name:
        click.echo(f'已将 {config_name} 设置为默认配置')

@config.command()
def list():
    """列出所有配置"""
    config = load_config()
    if not config or 'configs' not in config:
        click.echo('暂无配置')
        return

    default_config = config.get('default')
    click.echo('当前配置列表：')
    for name, provider_config in config['configs'].items():
        prefix = '* ' if name == default_config else '  '
        click.echo(f"{prefix}{name} ({provider_config['type']})")

@config.command()
@click.argument('name', metavar='配置名')
def set_default(name):
    """设置默认配置"""
    config = load_config()
    if not config or 'configs' not in config:
        click.echo('暂无配置')
        return

    if name not in config['configs']:
        click.echo(f'配置 {name} 不存在')
        return

    config['default'] = name
    save_config(config)
    click.echo(f'已将 {name} 设置为默认配置')

@config.command()
@click.argument('name', metavar='配置名')
def delete(name):
    """删除指定配置"""
    config = load_config()
    if not config or 'configs' not in config:
        click.echo('暂无配置')
        return

    if name not in config['configs']:
        click.echo(f'配置 {name} 不存在')
        return

    if name == config.get('default'):
        click.echo('无法删除默认配置，请先设置其他配置为默认配置')
        return

    del config['configs'][name]
    save_config(config)
    click.echo(f'配置 {name} 已删除')

@record.command()
@click.argument('domain', metavar='域名')
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
@click.option('--rr', '-r', help='按主机记录名称过滤')
@click.option('--type', '-t', 'record_type', help='按记录类型过滤')
def list(domain, provider, rr, record_type):
    """列出域名的所有DNS记录"""
    try:
        config = get_provider_config(provider)
        
        if config['type'] == 'aliyun':
            dns = AliyunDNS(**config['credentials'])
        elif config['type'] == 'tencent':
            dns = TencentDNS(**config['credentials'])
        else:  # cloudflare
            dns = CloudflareDNS(**config['credentials'])
        
        records = dns.list_records(domain)
        if not records:
            click.echo('未找到任何记录')
            return
        
        # 创建表格
        table = PrettyTable()
        if config['type'] == 'cloudflare':
            table.field_names = ['记录ID', '主机记录', '记录类型', '记录值', 'CDN']
        else:
            table.field_names = ['记录ID', '主机记录', '记录类型', '记录值']
        table.align = 'l'  # 左对齐

        # 过滤记录
        filtered_records = []
        for record in records:
            if config['type'] == 'aliyun':
                record_rr = record['RR']
                record_type_val = record['Type']
            elif config['type'] == 'tencent':
                record_rr = record.Name
                record_type_val = record.Type
            else:  # cloudflare
                record_rr = record['RR']
                record_type_val = record['Type']
            
            if rr and record_rr != rr:
                continue
            if record_type and record_type_val != record_type:
                continue
            filtered_records.append(record)

        # 添加记录
        for record in filtered_records:
            if config['type'] == 'aliyun':
                table.add_row([
                    record['RecordId'],
                    record['RR'],
                    record['Type'],
                    record['Value']
                ])
            elif config['type'] == 'tencent':
                table.add_row([
                    record.RecordId,
                    record.Name,
                    record.Type,
                    record.Value
                ])
            else:  # cloudflare
                table.add_row([
                    record['RecordId'],
                    record['RR'],
                    record['Type'],
                    record['Value'],
                    record['Proxied']
                ])
        click.echo(table)
    except Exception as e:
        click.echo(f'错误: {str(e)}')

@record.command()
@click.argument('domain', metavar='域名')
@click.argument('rr', metavar='主机记录')
@click.argument('type', metavar='记录类型')
@click.argument('value', metavar='记录值')
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
@click.option('--proxy/--no-proxy', default=False, help='是否启用 Cloudflare CDN 代理, 默认禁用')
def add(domain, rr, type, value, provider, proxy):
    """添加DNS记录"""
    try:
        config = get_provider_config(provider)
        
        if config['type'] == 'aliyun':
            dns = AliyunDNS(**config['credentials'])
        elif config['type'] == 'tencent':
            dns = TencentDNS(**config['credentials'])
        else:  # cloudflare
            dns = CloudflareDNS(**config['credentials'])

        if config['type'] == 'cloudflare':
            if dns.add_record(domain, rr, type, value, proxy):
                click.echo('记录添加成功')
            else:
                click.echo('记录添加失败')
        else:
            if dns.add_record(domain, rr, type, value):
                click.echo('记录添加成功')
            else:
                click.echo('记录添加失败')
    except Exception as e:
        click.echo(f'错误: {str(e)}')

@record.command()
@click.argument('domain', metavar='域名')
@click.argument('record_id', nargs=-1, metavar='记录ID...')
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
def delete(domain, record_id, provider):
    """删除DNS记录"""
    try:
        config = get_provider_config(provider)
        
        if config['type'] == 'aliyun':
            dns = AliyunDNS(**config['credentials'])
        elif config['type'] == 'tencent':
            dns = TencentDNS(**config['credentials'])
        else:  # cloudflare
            dns = CloudflareDNS(**config['credentials'])
        for rid in record_id:
            if dns.delete_record(domain, rid):
                click.echo(f'{rid} 记录删除成功')
            else:
                click.echo(f'{rid} 记录删除失败')
    except Exception as e:
        click.echo(f'错误: {str(e)}')

@record.command()
@click.argument('domain', metavar='域名')
@click.argument('record_id', metavar='记录ID')
@click.argument('rr', metavar='主机记录')
@click.argument('type', metavar='记录类型')
@click.argument('value', metavar='记录值')
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
def update(domain, record_id, rr, type, value, provider):
    """更新DNS记录"""
    try:
        config = get_provider_config(provider)
        
        if config['type'] == 'aliyun':
            dns = AliyunDNS(**config['credentials'])
        elif config['type'] == 'tencent':
            dns = TencentDNS(**config['credentials'])
        else:  # cloudflare
            dns = CloudflareDNS(**config['credentials'])
        
        if dns.update_record(domain, record_id, rr, type, value):
            click.echo('记录更新成功')
        else:
            click.echo('记录更新失败')
    except Exception as e:
        click.echo(f'错误: {str(e)}')

@record.command()
@click.argument('domain', metavar='域名')
@click.argument('rr', metavar='主机记录')
@click.argument('type', metavar='记录类型')
@click.option('--value', '-v', help='记录值，用于精确匹配特定记录')
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
def get_id(domain, rr, type, value, provider):
    """获取DNS记录ID"""
    try:
        config = get_provider_config(provider)
        
        if config['type'] == 'aliyun':
            dns = AliyunDNS(**config['credentials'])
        elif config['type'] == 'tencent':
            dns = TencentDNS(**config['credentials'])
        else:  # cloudflare
            dns = CloudflareDNS(**config['credentials'])
        
        record_id = dns.get_record_id(domain, rr, type, value)
        if record_id:
            click.echo(record_id)
        else:
            click.echo('未找到匹配的记录')
    except Exception as e:
        click.echo(f'错误: {str(e)}')

if __name__ == '__main__':
    cli()