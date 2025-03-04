#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DNSProvider(ABC):
    @abstractmethod
    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """获取域名信息"""
        pass

    @abstractmethod
    def list_records(self, domain: str) -> List[Dict[str, Any]]:
        """列出域名的所有记录"""
        pass

    @abstractmethod
    def add_record(self, domain: str, rr: str, type_: str, value: str) -> bool:
        """添加域名记录"""
        pass

    @abstractmethod
    def delete_record(self, domain: str, record_id: str) -> bool:
        """删除域名记录"""
        pass

    @abstractmethod
    def update_record(self, domain: str, record_id: str, rr: str, type_: str, value: str) -> bool:
        """更新域名记录"""
        pass

    @abstractmethod
    def get_record_id(self, domain: str, rr: str, type_: str, value: str = None) -> str:
        """通过主机记录名称、记录类型和记录值获取记录ID"""
        pass

    @abstractmethod
    def list_domains(self) -> List[Dict[str, Any]]:
        """获取域名列表
        
        Returns:
            List[Dict[str, Any]]: 域名列表，每个域名包含以下信息：
                - name: 域名
                - status: 域名状态
                - created_at: 创建时间
                - updated_at: 更新时间
        """
        pass