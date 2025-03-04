#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
from typing import Dict, Any

CONFIG_FILE = os.path.expanduser('~/.dnscli/config.yaml')

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f) or {}

def save_config(config: Dict[str, Any]) -> None:
    """保存配置文件"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def get_provider_config(provider: str = None) -> Dict[str, Any]:
    """获取指定云服务商的配置，如果未指定provider则返回默认配置"""
    config = load_config()
    if not provider:
        provider = config.get('default')
    
    if not provider or provider not in config.get('configs', {}):
        raise KeyError(f'未找到{provider}的配置信息')
    return config['configs'][provider]

def update_provider_config(provider: str, provider_type: str, credentials: Dict[str, str]) -> None:
    """更新云服务商的配置"""
    config = load_config()
    if 'configs' not in config:
        config['configs'] = {}
    
    config['configs'][provider] = {
        'type': provider_type,
        'credentials': credentials
    }
    
    # 如果是第一次配置，设置为默认配置
    if 'default' not in config:
        config['default'] = provider

    save_config(config)