#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化配置运行脚本
"""

import sys
import os
import subprocess

def run_optimized():
    """使用优化配置运行测速"""
    
    # 方案1：增加每个地区的IP数量限制
    print("方案1：增加每个地区的IP数量限制")
    print("=" * 60)
    cmd1 = [
        sys.executable, "istoreos_cf_speedtest.py",
        "--max-per-region", "20",  # 每个地区最多20个IP
        "--max-total", "100",      # 总共最多100个IP
        "--regions", "US,GB,IN,JP,KR,SG,HK,DE,FR,NL,CA,AU,BR,EU,ASIA"  # 更多地区
    ]
    
    print("执行命令:", " ".join(cmd1))
    print()
    
    # 方案2：减少每个地区的限制，但增加地区数量
    print("\n方案2：减少每个地区的限制，但增加地区数量")
    print("=" * 60)
    cmd2 = [
        sys.executable, "istoreos_cf_speedtest.py",
        "--max-per-region", "5",   # 每个地区最多5个IP
        "--max-total", "100",      # 总共最多100个IP
        "--regions", "US,GB,HK,JP,SG,DE,FR,NL,CA,AU,BR,EU,ASIA,Other"  # 包括Other
    ]
    
    print("执行命令:", " ".join(cmd2))
    print()
    
    # 方案3：完全禁用地区限制
    print("\n方案3：完全禁用地区限制（只按延迟排序）")
    print("=" * 60)
    cmd3 = [
        sys.executable, "istoreos_cf_speedtest.py",
        "--max-per-region", "1000",  # 非常大的数字，相当于无限制
        "--max-total", "100",        # 总共最多100个IP
        "--regions", "US,GB,HK,JP,SG,DE,FR,NL,CA,AU,BR,EU,ASIA,Other"  # 所有地区
    ]
    
    print("执行命令:", " ".join(cmd3))
    print()
    
    # 询问用户选择哪个方案
    print("\n请选择要运行的方案:")
    print("1. 方案1 (每个地区最多20个IP，总共100个IP)")
    print("2. 方案2 (每个地区最多5个IP，总共100个IP)")
    print("3. 方案3 (无地区限制，总共100个IP)")
    print("4. 自定义配置")
    print("5. 退出")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
    if choice == "1":
        cmd = cmd1
    elif choice == "2":
        cmd = cmd2
    elif choice == "3":
        cmd = cmd3
    elif choice == "4":
        print("\n自定义配置:")
        max_per_region = input("每个地区最多IP数 (默认: 10): ").strip() or "10"
        max_total = input("总共最多IP数 (默认: 100): ").strip() or "100"
        regions = input("优先地区 (逗号分隔，默认: US,GB,HK,JP,SG): ").strip() or "US,GB,HK,JP,SG"
        
        cmd = [
            sys.executable, "istoreos_cf_speedtest.py",
            "--max-per-region", max_per_region,
            "--max-total", max_total,
            "--regions", regions
        ]
    elif choice == "5":
        print("退出")
        return
    else:
        print("无效选择，使用方案1")
        cmd = cmd1
    
    # 执行命令
    print(f"\n执行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print("\n✓ 测速完成")
            
            # 检查结果
            best_ip_file = "best_ip.txt"
            if os.path.exists(best_ip_file):
                with open(best_ip_file, 'r', encoding='utf-8') as f:
                    ips = [line.strip() for line in f if line.strip()]
                    print(f"✓ 找到 {len(ips)} 个最佳IP")
                    
                    # 显示前10个IP
                    if ips:
                        print("\n前10个最佳IP:")
                        for i, ip in enumerate(ips[:10], 1):
                            print(f"  {i:2}. {ip}")
                        
                        if len(ips) > 10:
                            print(f"  ... 还有 {len(ips)-10} 个IP")
        else:
            print(f"\n✗ 测速失败，退出码: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 命令执行失败: {e}")
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    run_optimized()