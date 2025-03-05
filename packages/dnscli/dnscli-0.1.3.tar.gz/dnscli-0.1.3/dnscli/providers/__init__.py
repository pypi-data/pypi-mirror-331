#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Any

from .base import DNSProvider
from .aliyun import AliyunDNS
from .tencent import TencentDNS
from .cloudflare import CloudflareDNS

__all__ = ['DNSProvider', 'AliyunDNS', 'TencentDNS', 'CloudflareDNS', 'get_provider_api']

DNSProviderAPI = {
    "aliyun": AliyunDNS,
    "tencent": TencentDNS,
    "cloudflare": CloudflareDNS
}

def get_provider_api(provider_type: str, credentials: Dict[str, Any]):
    if not DNSProviderAPI.get(provider_type):
        raise KeyError(f'不支持的DNS服务商类型： {provider_type}')
    return DNSProviderAPI.get(provider_type)(**credentials)