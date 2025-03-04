#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any

from tencentcloud.common import credential
from tencentcloud.dnspod.v20210323 import dnspod_client, models

from .base import DNSProvider

class TencentDNS(DNSProvider):
    def __init__(self, secret_id: str, secret_key: str):
        cred = credential.Credential(secret_id, secret_key)
        self.client = dnspod_client.DnspodClient(cred, "")

    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        request = models.DescribeDomainRequest()
        request.Domain = domain
        try:
            response = self.client.DescribeDomain(request)
            return response.DomainInfo
        except Exception:
            return None

    def list_records(self, domain: str) -> List[Dict[str, Any]]:
        request = models.DescribeRecordListRequest()
        request.Domain = domain
        request.Limit = 100  # 设置每页记录数
        offset = 0
        all_records = []

        while True:
            request.Offset = offset
            response = self.client.DescribeRecordList(request)
            records = response.RecordList
            all_records.extend(records)

            if len(records) < request.Limit:
                break
            offset += len(records)

        return all_records

    def add_record(self, domain: str, rr: str, type_: str, value: str) -> bool:
        request = models.CreateRecordRequest()
        request.Domain = domain
        request.SubDomain = rr
        request.RecordType = type_
        request.RecordLine = "默认"
        request.Value = value
        try:
            self.client.CreateRecord(request)
            return True
        except Exception as e:
            print(f"添加记录失败：{str(e)}")
            return False

    def delete_record(self, domain: str, record_id: str) -> bool:
        request = models.DeleteRecordRequest()
        request.Domain = domain
        request.RecordId = int(record_id)
        try:
            self.client.DeleteRecord(request)
            return True
        except Exception:
            return False

    def update_record(self, domain: str, record_id: str, rr: str, type_: str, value: str) -> bool:
        request = models.ModifyRecordRequest()
        request.Domain = domain
        request.RecordId = int(record_id)
        request.SubDomain = rr
        request.RecordType = type_
        request.RecordLine = "默认"
        request.Value = value
        try:
            self.client.ModifyRecord(request)
            return True
        except Exception:
            return False

    def get_record_id(self, domain: str, rr: str, type_: str, value: str = None) -> str:
        request = models.DescribeRecordListRequest()
        request.Domain = domain
        request.Subdomain = rr
        request.RecordType = type_
        # 如果指定了记录值，则查找匹配的记录
        # 如果未指定记录值，返回第一条记录的ID
        if value:
            request.Keyword = value
        try:
            response = self.client.DescribeRecordList(request)
            if response.RecordList:
                return str(response.RecordList[0].RecordId)
        except Exception:
            pass
        return ''

    def list_domains(self) -> List[Dict[str, Any]]:
        request = models.DescribeDomainListRequest()
        request.Limit = 100  # 设置每页记录数
        offset = 0
        all_domains = []

        while True:
            request.Offset = offset
            try:
                response = self.client.DescribeDomainList(request)
                domains = response.DomainList
                for domain in domains:
                    all_domains.append({
                        'name': domain.Name,
                        'status': domain.Status,
                        'created_at': domain.CreatedOn,
                        'updated_at': domain.UpdatedOn
                    })

                if len(domains) < request.Limit:
                    break
                offset += len(domains)
            except Exception as e:
                raise Exception(f'获取域名列表失败：{str(e)}')

        return all_domains