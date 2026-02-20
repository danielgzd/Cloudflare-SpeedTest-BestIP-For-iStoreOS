#!/bin/bash

# 直接获取速度前100个IP（不限制地区）
echo "========================================"
echo "获取速度最快的100个Cloudflare IP"
echo "时间: $(date)"
echo "========================================"

# 检查 result.csv 文件
if [ ! -f "result.csv" ]; then
    echo "错误：result.csv 文件不存在"
    echo "请先运行测速脚本：python3 istoreos_cf_speedtest.py"
    exit 1
fi

# 检查文件大小
file_size=$(wc -l < result.csv)
if [ $file_size -lt 10 ]; then
    echo "警告：result.csv 文件太小（只有 $file_size 行）"
    echo "测速结果可能不完整"
fi

echo "从 result.csv 提取速度最快的100个IP..."

# 提取IP和延迟，按延迟排序，取前100个
# 第1列：IP地址，第5列：平均延迟
tail -n +2 result.csv | awk -F',' '{print $1 "," $5}' | sort -t',' -k2,2n | head -100 | cut -d',' -f1 > best_ip.txt

# 检查提取结果
ip_count=$(wc -l < best_ip.txt)
echo "已提取 $ip_count 个最快IP到 best_ip.txt"

if [ $ip_count -eq 0 ]; then
    echo "错误：未能提取任何IP"
    echo "请检查 result.csv 文件格式"
    exit 1
fi

# 显示前10个最快IP
echo ""
echo "前10个最快IP（按延迟排序）:"
echo "------------------------------"
head -10 best_ip.txt | awk '{printf "  %2d. %-15s\n", NR, $1}'

# 显示延迟信息（如果可用）
echo ""
echo "延迟统计:"
echo "------------------------------"
if [ $ip_count -ge 5 ]; then
    # 获取前5个IP的延迟
    echo "前5个IP的延迟:"
    for i in $(seq 1 5); do
        ip=$(head -$i best_ip.txt | tail -1)
        latency=$(grep "^$ip," result.csv | head -1 | cut -d',' -f5 2>/dev/null || echo "N/A")
        printf "  %2d. %-15s 延迟: %s ms\n" $i "$ip" "$latency"
    done
fi

# 显示IP段分布
echo ""
echo "IP段分布:"
echo "------------------------------"
cut -d'.' -f1-2 best_ip.txt | sort | uniq -c | sort -rn | head -10 | while read count segment; do
    printf "  %-10s %3d 个IP\n" "$segment.x.x" $count
done

echo ""
echo "========================================"
echo "完成！best_ip.txt 包含 $ip_count 个最快IP"
echo "时间: $(date)"
echo "========================================"

# 验证文件
if [ $ip_count -lt 50 ]; then
    echo "警告：IP数量不足（只有 $ip_count 个）"
    echo "建议重新运行完整测速"
elif [ $ip_count -eq 100 ]; then
    echo "✓ 成功获取100个最快IP"
else
    echo "⚠ 获取了 $ip_count 个IP（目标：100个）"
fi