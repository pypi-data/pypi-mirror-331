import os
import click
import yaml

from ..config import CONFIG_FILE, save_config, load_config

@click.group()
def config():
    """配置管理相关命令"""
    pass

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
@click.option('--config-name', '-n', prompt="请输入配置名称", help='配置名称')
@click.option('--provider', '-p', prompt="请选择DNS服务商类型", type=click.Choice(['aliyun', 'tencent', 'cloudflare']), help='指定使用的DNS服务商配置')
def add(config_name, provider):
    """添加DNS服务商配置信息"""
    # 根据不同服务商类型获取凭证信息
    if provider == 'aliyun':
        credentials = {
            'access_key_id': click.prompt('请输入Access Key ID'),
            'access_key_secret': click.prompt('请输入Access Key Secret', hide_input=True)
        }
    elif provider == 'tencent':
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
        'type': provider,
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


