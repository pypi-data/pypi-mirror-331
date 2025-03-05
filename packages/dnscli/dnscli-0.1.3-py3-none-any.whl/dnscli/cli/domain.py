
import click

from prettytable import PrettyTable

from ..providers import get_provider_api
from ..config import get_config

@click.group()
def domain():
    """域名管理相关命令"""
    pass

@domain.command(name="list")
@click.option('--provider', '-p', help='指定使用的DNS服务商配置')
def _list(provider):
    """列出所有域名"""
    try:
        provider_config = get_config(provider)
        provider_type = provider_config['type']
        credentials = provider_config['credentials']
        dns = get_provider_api(provider_type, credentials)

        # 获取域名列表
        domains = dns.list_domains()

        # 创建表格并显示域名信息
        table = PrettyTable()
        table.field_names = ['域名', '状态', '创建时间', '更新时间']
        table.align = 'l'  # 左对齐
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

