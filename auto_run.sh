#!/bin/bash

# 设置路径环境变量，确保脚本能找到 python3 和 git
export PATH="/usr/bin:/usr/sbin:/bin:/sbin:$PATH"

# 进入仓库目录
cd "$(dirname "$0")" || exit 1

echo "========================================"
echo "开始运行 Cloudflare 测速自动脚本"
echo "时间: $(date)"
echo "========================================"

# 1. 保存当前更改（如果有）
echo "1. 保存当前更改..."
if [ -n "$(git status --porcelain)" ]; then
    echo "  发现未提交的更改，先提交..."
    git add .
    git commit -m "auto: 自动保存更改 $(date +'%Y-%m-%d %H:%M')" || echo "  提交失败，继续执行..."
fi

# 2. 拉取远程更新
echo "2. 拉取远程更新..."
git pull origin main || {
    echo "  拉取失败，尝试强制拉取..."
    git fetch origin
    git reset --hard origin/main
}

# 3. 运行测速脚本（无地区限制，直接获取前100个最快IP）
echo "3. 运行测速脚本..."
echo "   配置：无地区限制，直接获取速度前100个IP"
python3 istoreos_cf_speedtest.py --max-per-region 1000 --max-total 100 --regions "US,GB,HK,JP,SG,DE,FR,NL,CA,AU,BR,EU,ASIA,Other" || {
    echo "  测速失败，尝试使用默认配置..."
    python3 istoreos_cf_speedtest.py
}

# 4. 直接提取速度前100个IP（不限制地区）
echo "4. 提取速度前100个IP..."
if [ -f "result.csv" ]; then
    echo "  从 result.csv 提取速度最快的100个IP..."
    # 提取IP和延迟，按延迟排序，取前100个
    tail -n +2 result.csv | awk -F',' '{print $1 "," $5}' | sort -t',' -k2,2n | head -100 | cut -d',' -f1 > best_ip.txt
    ip_count=$(wc -l < best_ip.txt)
    echo "  已提取 $ip_count 个最快IP到 best_ip.txt"
    
    # 显示前10个最快IP
    if [ $ip_count -gt 0 ]; then
        echo "  前10个最快IP:"
        head -10 best_ip.txt | awk '{print "    " NR ". " $1}'
    fi
else
    echo "  错误：result.csv 文件不存在"
fi

# 5. 检查IP数量
echo "5. 检查IP数量..."
if [ -f "best_ip.txt" ]; then
    ip_count=$(wc -l < best_ip.txt)
    echo "  best_ip.txt 包含 $ip_count 个IP"
    
    if [ $ip_count -lt 50 ]; then
        echo "  警告：IP数量不足！"
    elif [ $ip_count -eq 100 ]; then
        echo "  ✓ 成功获取100个最快IP"
    else
        echo "  ⚠ 获取了 $ip_count 个IP（目标：100个）"
    fi
fi

# 6. 检查是否有文件更新并推送到 GitHub
echo "6. 检查文件更新..."
if [ -n "$(git status --porcelain)" ]; then
    echo "  发现文件更新，推送到 GitHub..."
    git add best_ip.txt result.csv 2>/dev/null || true
    git add . 2>/dev/null || true
    git commit -m "chore: istoreos auto update $(date +'%Y-%m-%d %H:%M:%S')" || echo "  提交失败"
    
    # 尝试推送，如果失败则继续
    git push origin main || echo "  推送失败，可能是网络问题或权限不足"
    echo "  Update successful: $(date)"
else
    echo "  No changes detected, skip push: $(date)"
fi

echo "========================================"
echo "自动脚本运行完成"
echo "时间: $(date)"
echo "========================================"
