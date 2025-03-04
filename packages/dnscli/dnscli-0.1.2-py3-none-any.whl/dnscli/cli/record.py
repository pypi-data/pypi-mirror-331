import click

from prettytable import PrettyTable

from ..config import get_provider_config
from ..providers import AliyunDNS, TencentDNS, CloudflareDNS

@click.group()
def record():
    """DNS记录管理相关命令"""
    pass

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
