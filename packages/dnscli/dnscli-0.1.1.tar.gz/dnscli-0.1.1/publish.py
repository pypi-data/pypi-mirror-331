#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f'已删除: {path}')

def build_package():
    """构建包"""
    print('\n开始构建包...')
    try:
        subprocess.run([sys.executable, '-m', 'build'], check=True)
        print('包构建成功')
        return True
    except subprocess.CalledProcessError as e:
        print(f'构建失败: {e}')
        return False

def check_dist():
    """检查构建的分发包"""
    print('\n检查分发包...')
    try:
        subprocess.run([sys.executable, '-m', 'twine', 'check', 'dist/*'], check=True)
        print('分发包检查通过')
        return True
    except subprocess.CalledProcessError as e:
        print(f'分发包检查失败: {e}')
        return False

def upload_to_pypi():
    """上传到 PyPI"""
    print('\n开始上传到 PyPI...')
    try:
        subprocess.run([sys.executable, '-m', 'twine', 'upload', 'dist/*'], check=True)
        print('上传成功')
        return True
    except subprocess.CalledProcessError as e:
        print(f'上传失败: {e}')
        return False

def main():
    print('=== 开始发布流程 ===')
    
    # 检查必要的依赖是否安装
    requirements = ['build', 'twine']
    for req in requirements:
        try:
            __import__(req)
        except ImportError:
            print(f'缺少必要的依赖: {req}')
            print(f'请运行: pip install {req}')
            return False
    
    # 执行发布流程
    clean_build_dirs()
    
    if not build_package():
        return False
    
    if not check_dist():
        return False
    
    if not upload_to_pypi():
        return False
    
    print('\n=== 发布流程完成 ===')
    return True

if __name__ == '__main__':
    sys.exit(0 if main() else 1)