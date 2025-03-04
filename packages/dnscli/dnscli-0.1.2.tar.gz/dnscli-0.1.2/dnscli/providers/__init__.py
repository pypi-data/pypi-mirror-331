#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .base import DNSProvider
from .aliyun import AliyunDNS
from .tencent import TencentDNS
from .cloudflare import CloudflareDNS

__all__ = ['DNSProvider', 'AliyunDNS', 'TencentDNS', 'CloudflareDNS']