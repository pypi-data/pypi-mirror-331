#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any, List
import requests
from .base import DNSProvider
from cloudflare import Cloudflare, BadRequestError


class CloudflareDNS(DNSProvider):
    def __init__(self, api_token: str | None = None, api_key: str | None = None, api_email: str | None = None):
        if api_token.strip():
            self._cf = Cloudflare(api_token=api_token)
        else:
            self._cf = Cloudflare(api_email=api_email, api_key=api_key)

    def _get_zone_id(self, domain: str) -> str:
        """获取域名的 Zone ID"""
        data = self._cf.zones.list(extra_query={"name": domain})
        if not data.result:
            raise Exception(f'无法获取域名 {domain} 的 Zone ID')
        return data.result[0].id

    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """获取域名信息"""
        zone_id = self._get_zone_id(domain)
        data = self._cf.zones.get(zone_id=zone_id)
        return data.to_dict()

    def list_records(self, domain: str) -> List[Dict[str, Any]]:
        """列出域名的所有记录"""
        zone_id = self._get_zone_id(domain)
        data = self._cf.dns.records.list(zone_id=zone_id)
        records = []
        if not data.result:
            return records
        # 转换为统一格式
        for record in data.result:
            records.append({
                'RecordId': record.id,
                'RR': record.name.replace(f'.{domain}', ''),
                'Type': record.type,
                'Value': record.content,
                'Proxied': record.proxied
            })
        return records

    def add_record(self, domain: str, rr: str, type_: str, value: str, proxied: bool = False) -> bool:
        """添加域名记录"""
        zone_id = self._get_zone_id(domain)
        if rr == '@':
            name = domain
        else:
            name = f'{rr}.{domain}'
        self._cf.dns.records.create(zone_id=zone_id, proxied=proxied, type=type_, name=name, content=value)
        return True

    def delete_record(self, domain: str, record_id: str) -> bool:
        """删除域名记录"""
        zone_id = self._get_zone_id(domain)
        self._cf.dns.records.delete(zone_id=zone_id, dns_record_id=record_id)
        return True

    def update_record(self, domain: str, record_id: str, rr: str, type_: str, value: str, proxied: bool = False) -> bool:
        """更新域名记录"""
        zone_id = self._get_zone_id(domain)
        if rr == '@':
            name = domain
        else:
            name = f'{rr}.{domain}'
        self._cf.dns.records.update(dns_record_id=record_id, zone_id=zone_id, name=name, content=value, proxied=proxied, type=type_)
        return True

    def get_record_id(self, domain: str, rr: str, type_: str, value: str = None) -> str:
        """通过主机记录名称、记录类型和记录值获取记录ID"""
        zone_id = self._get_zone_id(domain)
        if rr == '@':
            name = domain
        else:
            name = f'{rr}.{domain}'
        data = self._cf.dns.records.list(zone_id=zone_id, name=name, content=value, type=type_)
        return data.result[0].id

    def list_domains(self) -> List[Dict[str, Any]]:
        """获取域名列表"""
        data = self._cf.zones.list()
        all_domains = []
        if not data.result:
            return all_domains
        for zone in data.result:
            all_domains.append({
                'name': zone.name,
                'status': zone.status,
                'created_at': zone.created_on,
                'updated_at': zone.modified_on
            })
        return all_domains
