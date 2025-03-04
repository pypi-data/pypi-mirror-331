#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import List, Dict, Any

from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteDomainRecordRequest import DeleteDomainRecordRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainsRequest import DescribeDomainsRequest

from .base import DNSProvider

class AliyunDNS(DNSProvider):
    def __init__(self, access_key_id: str, access_key_secret: str):
        self.client = AcsClient(access_key_id, access_key_secret)

    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        from aliyunsdkalidns.request.v20150109.DescribeDomainInfoRequest import DescribeDomainInfoRequest
        request = DescribeDomainInfoRequest()
        request.set_DomainName(domain)
        try:
            response = self.client.do_action_with_exception(request)
            return json.loads(response)
        except Exception:
            return None

    def list_records(self, domain: str) -> List[Dict[str, Any]]:
        request = DescribeDomainRecordsRequest()
        request.set_DomainName(domain)
        request.set_PageSize(100)  # 设置每页记录数
        page_number = 1
        all_records = []

        while True:
            request.set_PageNumber(page_number)
            response = self.client.do_action_with_exception(request)
            response = json.loads(response)
            records = response['DomainRecords']['Record']
            all_records.extend(records)

            total_count = response['TotalCount']
            if len(all_records) >= total_count:
                break
            page_number += 1

        return all_records

    def add_record(self, domain: str, rr: str, type_: str, value: str) -> bool:
        request = AddDomainRecordRequest()
        request.set_DomainName(domain)
        request.set_RR(rr)
        request.set_Type(type_)
        request.set_Value(value)
        try:
            self.client.do_action_with_exception(request)
            return True
        except Exception:
            return False

    def delete_record(self, domain: str, record_id: str) -> bool:
        request = DeleteDomainRecordRequest()
        request.set_RecordId(record_id)
        try:
            self.client.do_action_with_exception(request)
            return True
        except Exception:
            return False

    def update_record(self, domain: str, record_id: str, rr: str, type_: str, value: str) -> bool:
        request = UpdateDomainRecordRequest()
        request.set_RecordId(record_id)
        request.set_RR(rr)
        request.set_Type(type_)
        request.set_Value(value)
        try:
            self.client.do_action_with_exception(request)
            return True
        except Exception:
            return False

    def get_record_id(self, domain: str, rr: str, type_: str, value: str = None) -> str:
        request = DescribeDomainRecordsRequest()
        request.set_DomainName(domain)
        request.set_RRKeyWord(rr)
        request.set_TypeKeyWord(type_)
        # 如果指定了记录值，则查找匹配的记录
        # 如果未指定记录值，返回第一条记录的ID
        if value:
            request.set_ValueKeyWord(value)
        try:
            response = self.client.do_action_with_exception(request)
            response = json.loads(response)
            records = response['DomainRecords']['Record']
            if records:
                return records[0]['RecordId']
        except Exception:
            pass
        return ''

    def list_domains(self) -> List[Dict[str, Any]]:
        request = DescribeDomainsRequest()
        request.set_PageSize(100)  # 设置每页记录数
        page_number = 1
        all_domains = []

        while True:
            request.set_PageNumber(page_number)
            try:
                response = self.client.do_action_with_exception(request)
                response = json.loads(response)
                domains = response['Domains']['Domain']
                for domain in domains:
                    all_domains.append({
                        'name': domain['DomainName'],
                        'status': domain.get('DomainStatus', 'UNKNOWN'),  # 使用get方法获取状态，如果不存在则返回UNKNOWN
                        'created_at': domain.get('CreateTime', '-'),
                        'updated_at': domain.get('CreateTime', '-')  # 阿里云API没有提供更新时间
                    })

                total_count = response['TotalCount']
                if len(all_domains) >= total_count:
                    break
                page_number += 1
            except Exception as e:
                raise Exception(f'获取域名列表失败：{str(e)}')

        return all_domains