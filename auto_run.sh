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

# 3. 运行测速脚本（使用优化配置）
echo "3. 运行测速脚本..."
echo "   使用优化配置：每个地区最多20个IP，总共100个IP"
python3 istoreos_cf_speedtest.py --max-per-region 20 --max-total 100 --regions "US,GB,HK,JP,SG,DE,FR,NL,CA,AU,BR,EU,ASIA,Other" || {
    echo "  测速失败，尝试使用默认配置..."
    python3 istoreos_cf_speedtest.py
}

# 4. 修复 best_ip.txt 文件，确保有100个IP
echo "4. 修复 best_ip.txt 文件..."
if [ -f "fix_best_ip.py" ]; then
    echo "  运行修复脚本..."
    python3 fix_best_ip.py
else
    echo "  警告：修复脚本 fix_best_ip.py 不存在"
    echo "  尝试从 result.csv 直接提取IP..."
    if [ -f "result.csv" ]; then
        # 简单的提取逻辑
        tail -n +2 result.csv | cut -d',' -f1 | head -100 > best_ip.txt
        echo "  已提取 $(wc -l < best_ip.txt) 个IP到 best_ip.txt"
    fi
fi

# 5. 检查IP数量
echo "5. 检查IP数量..."
if [ -f "best_ip.txt" ]; then
    ip_count=$(wc -l < best_ip.txt)
    echo "  best_ip.txt 包含 $ip_count 个IP"
    
    if [ $ip_count -lt 50 ]; then
        echo "  警告：IP数量不足，尝试重新提取..."
        if [ -f "result.csv" ]; then
            tail -n +2 result.csv | cut -d',' -f1 | head -100 > best_ip.txt
            echo "  重新提取后：$(wc -l < best_ip.txt) 个IP"
        fi
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
