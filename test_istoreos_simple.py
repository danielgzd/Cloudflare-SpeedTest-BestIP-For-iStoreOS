#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 iStoreOS 独立脚本的基本功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入要测试的模块
import istoreos_cf_speedtest as script_module

def test_class_initialization():
    """测试类初始化"""
    print("测试类初始化...")
    
    # 创建实例
    speedtest = script_module.CloudflareSpeedTestIStoreOS()
    
    # 检查默认配置
    assert speedtest.config['max_per_region'] == 10
    assert speedtest.config['max_total'] == 100
    assert speedtest.config['priority_regions'] == ["US", "GB", "IN", "JP", "KR", "SG", "HK"]
    assert speedtest.config['cfst_args'] == "-n 200 -t 4 -dn 100 -dt 8 -p 0 -o result.csv"
    
    print("  ✓ 类初始化成功")
    print(f"    工作目录: {speedtest.work_dir}")
    print(f"    仓库根目录: {speedtest.repo_root}")
    print()

def test_architecture_detection():
    """测试架构检测"""
    print("测试架构检测...")
    
    speedtest = script_module.CloudflareSpeedTestIStoreOS()
    url = speedtest.get_cfst_url()
    
    # 根据当前架构检查URL
    import platform
    machine = platform.machine().lower()
    
    if machine in ('aarch64', 'arm64'):
        assert 'arm64' in url
        print(f"  ✓ ARM64 架构检测正确: {url}")
    elif machine in ('x86_64', 'amd64'):
        assert 'amd64' in url
        print(f"  ✓ x86_64 架构检测正确: {url}")
    elif machine == 'i386':
        assert '386' in url
        print(f"  ✓ i386 架构检测正确: {url}")
    elif machine in ('armv7l', 'armv7'):
        assert 'armv7' in url
        print(f"  ✓ ARMv7 架构检测正确: {url}")
    elif machine == 'armv6l':
        assert 'armv6' in url
        print(f"  ✓ ARMv6 架构检测正确: {url}")
    elif machine == 'armv5l':
        assert 'armv5' in url
        print(f"  ✓ ARMv5 架构检测正确: {url}")
    else:
        # 未知架构应该回退到 ARM64
        assert 'arm64' in url
        print(f"  ✓ 未知架构回退到 ARM64: {url}")
    
    print()

def test_region_detection():
    """测试地区检测"""
    print("测试地区检测...")
    
    speedtest = script_module.CloudflareSpeedTestIStoreOS()
    
    test_cases = [
        ("104.16.0.1", "US"),
        ("141.101.64.1", "GB"),
        ("103.21.244.1", "JP"),
        ("103.22.200.1", "KR"),
        ("103.31.4.1", "SG"),
        ("190.93.240.1", "HK"),
        ("197.234.240.1", "IN"),
        ("8.8.8.8", "Other"),
        ("1.1.1.1", "Other"),
    ]
    
    for ip, expected in test_cases:
        result = speedtest.get_region_for_ip(ip)
        if result == expected:
            print(f"  ✓ {ip} -> {result}")
        else:
            print(f"  ✗ {ip} -> 期望 {expected}, 实际 {result}")
    
    print()

def test_argument_parsing():
    """测试参数解析"""
    print("测试参数解析...")
    
    # 模拟命令行参数
    import argparse
    
    class MockArgs:
        def __init__(self):
            self.max_per_region = 5
            self.max_total = 50
            self.regions = "US,JP,KR"
            self.cfst_args = "-n 100 -t 2 -o test.csv"
            self.work_dir = None
            self.output_dir = None
            self.no_cache = False
            self.debug = False
    
    mock_args = MockArgs()
    
    # 测试配置创建
    config = script_module.config_from_args(mock_args)
    
    assert config['max_per_region'] == 5
    assert config['max_total'] == 50
    assert config['priority_regions'] == ["US", "JP", "KR"]
    assert config['cfst_args'] == "-n 100 -t 2 -o test.csv"
    
    print("  ✓ 参数解析成功")
    print(f"    max_per_region: {config['max_per_region']}")
    print(f"    max_total: {config['max_total']}")
    print(f"    priority_regions: {config['priority_regions']}")
    print(f"    cfst_args: {config['cfst_args']}")
    print()

def test_environment_variables():
    """测试环境变量覆盖"""
    print("测试环境变量覆盖...")
    
    # 保存原始环境变量
    original_env = {
        'MAX_PER_REGION': os.environ.get('MAX_PER_REGION'),
        'MAX_TOTAL': os.environ.get('MAX_TOTAL'),
        'PRIORITY_REGIONS': os.environ.get('PRIORITY_REGIONS'),
        'CFST_ARGS': os.environ.get('CFST_ARGS'),
    }
    
    try:
        # 设置测试环境变量
        os.environ['MAX_PER_REGION'] = '3'
        os.environ['MAX_TOTAL'] = '30'
        os.environ['PRIORITY_REGIONS'] = 'US,JP'
        os.environ['CFST_ARGS'] = '-n 50 -t 1 -o env_test.csv'
        
        # 创建模拟参数
        class MockArgs:
            def __init__(self):
                self.max_per_region = 10  # 默认值，应该被环境变量覆盖
                self.max_total = 100      # 默认值，应该被环境变量覆盖
                self.regions = "US,GB,JP,KR"  # 默认值，应该被环境变量覆盖
                self.cfst_args = "-n 200 -t 4 -o default.csv"  # 默认值，应该被环境变量覆盖
                self.work_dir = None
                self.output_dir = None
                self.no_cache = False
                self.debug = False
        
        mock_args = MockArgs()
        config = script_module.config_from_args(mock_args)
        
        # 验证环境变量覆盖
        assert config['max_per_region'] == 3
        assert config['max_total'] == 30
        assert config['priority_regions'] == ["US", "JP"]
        assert config['cfst_args'] == "-n 50 -t 1 -o env_test.csv"
        
        print("  ✓ 环境变量覆盖成功")
        print(f"    MAX_PER_REGION 覆盖: {config['max_per_region']}")
        print(f"    MAX_TOTAL 覆盖: {config['max_total']}")
        print(f"    PRIORITY_REGIONS 覆盖: {config['priority_regions']}")
        print(f"    CFST_ARGS 覆盖: {config['cfst_args']}")
        
    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value
    
    print()

def main():
    """运行所有测试"""
    print("=" * 60)
    print("iStoreOS 独立脚本功能测试")
    print("=" * 60)
    print()
    
    try:
        test_class_initialization()
        test_architecture_detection()
        test_region_detection()
        test_argument_parsing()
        test_environment_variables()
        
        print("=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
        return 0
        
    except AssertionError as e:
        print(f"测试失败: {e}")
        return 1
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())