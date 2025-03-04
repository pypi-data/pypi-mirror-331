#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any, List
import requests
from .base import DNSProvider

class CloudflareDNS(DNSProvider):
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = 'https://api.cloudflare.com/client/v4'
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def _get_zone_id(self, domain: str) -> str:
        """获取域名的 Zone ID"""
        response = requests.get(
            f'{self.base_url}/zones',
            params={'name': domain},
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        if data['success'] and data['result']:
            return data['result'][0]['id']
        raise Exception(f'无法获取域名 {domain} 的 Zone ID')

    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """获取域名信息"""
        zone_id = self._get_zone_id(domain)
        response = requests.get(
            f'{self.base_url}/zones/{zone_id}',
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        if data['success']:
            return data['result']
        raise Exception(f'获取域名 {domain} 信息失败')

    def list_records(self, domain: str) -> List[Dict[str, Any]]:
        """列出域名的所有记录"""
        zone_id = self._get_zone_id(domain)
        response = requests.get(
            f'{self.base_url}/zones/{zone_id}/dns_records',
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        if data['success']:
            # 转换为统一格式
            records = []
            for record in data['result']:
                records.append({
                    'RecordId': record['id'],
                    'RR': record['name'].replace(f'.{domain}', ''),
                    'Type': record['type'],
                    'Value': record['content'],
                    'Proxied': record.get('proxied', False)
                })
            return records
        raise Exception(f'获取域名 {domain} 的记录列表失败')

    def add_record(self, domain: str, rr: str, type_: str, value: str, proxied: bool = None) -> bool:
        """添加域名记录"""
        zone_id = self._get_zone_id(domain)
        response = requests.post(
            f'{self.base_url}/zones/{zone_id}/dns_records',
            headers=self.headers,
            json={
                'type': type_,
                'name': f'{rr}.{domain}' if rr else domain,
                'content': value,
                'proxied': bool(proxied) if proxied is not None else False
            }
        )
        response.raise_for_status()
        return response.json()['success']

    def delete_record(self, domain: str, record_id: str) -> bool:
        """删除域名记录"""
        zone_id = self._get_zone_id(domain)
        response = requests.delete(
            f'{self.base_url}/zones/{zone_id}/dns_records/{record_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()['success']

    def update_record(self, domain: str, record_id: str, rr: str, type_: str, value: str) -> bool:
        """更新域名记录"""
        zone_id = self._get_zone_id(domain)
        response = requests.put(
            f'{self.base_url}/zones/{zone_id}/dns_records/{record_id}',
            headers=self.headers,
            json={
                'type': type_,
                'name': f'{rr}.{domain}' if rr else domain,
                'content': value
            }
        )
        response.raise_for_status()
        return response.json()['success']

    def get_record_id(self, domain: str, rr: str, type_: str, value: str = None) -> str:
        """通过主机记录名称、记录类型和记录值获取记录ID"""
        zone_id = self._get_zone_id(domain)
        params = {
            'type': type_,
            'name': f'{rr}.{domain}' if rr else domain
        }
        if value:
            params['content'] = value

        response = requests.get(
            f'{self.base_url}/zones/{zone_id}/dns_records',
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        if data['success'] and data['result']:
            return data['result'][0]['id']
        return ''

    def list_domains(self) -> List[Dict[str, Any]]:
        """获取域名列表"""
        response = requests.get(
            f'{self.base_url}/zones',
            headers=self.headers,
            params={'per_page': 100}
        )
        response.raise_for_status()
        data = response.json()

        if not data['success']:
            raise Exception('获取域名列表失败')

        all_domains = []
        for zone in data['result']:
            all_domains.append({
                'name': zone['name'],
                'status': zone['status'],
                'created_at': zone['created_on'],
                'updated_at': zone['modified_on']
            })

        return all_domains

    def get_record_id(self, domain: str, rr: str, type_: str, value: str = None) -> str:
        """通过主机记录名称、记录类型和记录值获取记录ID"""
        records = self.list_records(domain)
        for record in records:
            if record['RR'] == rr and record['Type'] == type_:
                if value is None or record['Value'] == value:
                    return record['RecordId']
        return ''