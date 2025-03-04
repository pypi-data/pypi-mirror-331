# DNSCLI

一个用于管理多云DNS记录的命令行工具，支持阿里云DNS、腾讯云DNS和Cloudflare DNS。

## 功能特点

- 支持阿里云DNS、腾讯云DNS和Cloudflare DNS
- 支持多配置管理，可同时管理多个云服务商的DNS记录
- 支持DNS记录的增删改查，包括A、AAAA、CNAME、MX、TXT等记录类型
- 支持Cloudflare CDN代理功能，轻松开启/关闭CDN加速
- 命令行界面，操作简单直观，支持批量操作
- 支持按记录类型、域名等条件筛选和查询

## 安装

### 使用 pip 安装

```bash
pip install dnscli
```

### 依赖要求

- Python >= 3.6
- click >= 8.0.0
- PyYAML >= 6.0
- prettytable >= 3.14.0
- aliyun-python-sdk-core >= 2.13.36
- aliyun-python-sdk-alidns >= 2.6.42
- tencentcloud-sdk-python >= 3.0.0

## 配置说明

### 配置文件格式

配置文件默认保存在用户目录下的 `.dnscli/config.yaml`，格式如下：

```yaml
default: aliyun  # 默认使用的配置名称
configs:
  aliyun:  # 阿里云配置
    provider: aliyun
    access_key_id: your_access_key_id
    access_key_secret: your_access_key_secret
  tencent:  # 腾讯云配置
    provider: tencent
    secret_id: your_secret_id
    secret_key: your_secret_key
  cloudflare:  # Cloudflare配置
    provider: cloudflare
    token: your_api_token
```

### 生成示例配置

```bash
dnscli config example
```

### 添加云服务商配置

```bash
# 添加阿里云配置
dnscli config add --provider aliyun

# 添加腾讯云配置
dnscli config add --provider tencent

# 添加Cloudflare配置
dnscli config add --provider cloudflare
```

## 使用示例

### 查看DNS记录

```bash
# 查看指定域名的所有记录
dnscli record list example.com

# 按记录类型筛选
dnscli record list example.com --type A

# 使用指定的配置
dnscli record list example.com --provider config_name
```

### 添加DNS记录

```bash
# 添加A记录
dnscli record add example.com www A "192.168.1.1"

# 添加CNAME记录
dnscli record add example.com www CNAME "cdn.example.com"

# 添加TXT记录
dnscli record add example.com @ TXT "v=spf1 include:spf.example.com ~all"

# 添加启用CDN代理的记录（仅Cloudflare）
dnscli record add example.com www A "192.168.1.1" --proxied
```

### 更新DNS记录

```bash
# 更新记录值
dnscli record update example.com <record-id> www A "192.168.1.2"

# 更新CDN代理状态（仅Cloudflare）
dnscli record update example.com <record-id> www A "192.168.1.2" --proxy
```

### 删除DNS记录

```bash
# 删除单条记录
dnscli record delete example.com <record-id>

# 批量删除记录（谨慎使用）
dnscli record delete example.com <record-id1> <record-id2>
```

## 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
