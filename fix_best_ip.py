#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 best_ip.txt 文件，使其包含更多IP
"""

import csv
import os
import sys

def fix_best_ip():
    """修复 best_ip.txt 文件"""
    
    # 读取 result.csv
    csv_file = "result.csv"
    if not os.path.exists(csv_file):
        print(f"错误: {csv_file} 文件不存在")
        return False
    
    print(f"读取 {csv_file}...")
    
    ip_latency_list = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                print("错误: CSV文件为空")
                return False
            
            # 查找延迟列的索引
            latency_idx = 4 if len(header) > 4 else -1  # 平均延迟在第5列
            
            for row in reader:
                if not row or len(row) <= latency_idx:
                    continue
                
                ip = row[0].strip()
                if not ip:
                    continue
                
                # 解析延迟
                try:
                    latency = float(row[latency_idx]) if latency_idx != -1 else 0.0
                except (ValueError, IndexError):
                    latency = 9999.0
                
                ip_latency_list.append((ip, latency))
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return False
    
    # 按延迟排序
    ip_latency_list.sort(key=lambda x: x[1])
    
    print(f"找到 {len(ip_latency_list)} 个IP")
    
    # 选择前N个IP
    target_count = 100  # 目标IP数量
    selected_ips = [ip for ip, _ in ip_latency_list[:target_count]]
    
    # 保存到 best_ip_fixed.txt
    output_file = "best_ip_fixed.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(selected_ips))
        if selected_ips:  # 如果列表不为空，添加换行符
            f.write("\n")
    
    print(f"已保存 {len(selected_ips)} 个IP到 {output_file}")
    
    # 显示前20个IP
    print("\n前20个最佳IP (按延迟排序):")
    for i, (ip, latency) in enumerate(ip_latency_list[:20], 1):
        print(f"{i:3}. {ip:20} 延迟: {latency:.2f}ms")
    
    # 自动覆盖原来的 best_ip.txt
    print(f"\n自动覆盖 best_ip.txt...")
    try:
        with open("best_ip.txt", 'w', encoding='utf-8') as f:
            f.write("\n".join(selected_ips))
            if selected_ips:
                f.write("\n")
        print(f"✓ 已覆盖 best_ip.txt，包含 {len(selected_ips)} 个IP")
    except Exception as e:
        print(f"✗ 覆盖 best_ip.txt 失败: {e}")
        return False
    
    return True

def analyze_current_best_ip():
    """分析当前的 best_ip.txt 文件"""
    best_ip_file = "best_ip.txt"
    if not os.path.exists(best_ip_file):
        print(f"文件不存在: {best_ip_file}")
        return
    
    with open(best_ip_file, 'r', encoding='utf-8') as f:
        ips = [line.strip() for line in f if line.strip()]
    
    print(f"当前 {best_ip_file} 包含 {len(ips)} 个IP")
    
    # 分析IP段分布
    ip_segments = {}
    for ip in ips:
        parts = ip.split('.')
        if len(parts) >= 2:
            segment = f"{parts[0]}.{parts[1]}"
            ip_segments[segment] = ip_segments.get(segment, 0) + 1
    
    print("\nIP段分布:")
    for segment, count in sorted(ip_segments.items(), key=lambda x: x[1], reverse=True):
        print(f"  {segment}.x.x: {count:3} 个IP")

if __name__ == "__main__":
    print("=" * 60)
    print("修复 best_ip.txt 文件")
    print("=" * 60)
    
    # 分析当前文件
    analyze_current_best_ip()
    
    print("\n" + "=" * 60)
    print("开始修复...")
    print("=" * 60)
    
    fix_best_ip()