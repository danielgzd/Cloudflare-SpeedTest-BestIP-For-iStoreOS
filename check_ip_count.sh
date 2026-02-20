#!/bin/bash

# 检查 best_ip.txt 中的IP数量
check_ip_count() {
    local ip_file="best_ip.txt"
    local min_expected=50
    
    if [ ! -f "$ip_file" ]; then
        echo "错误：文件 $ip_file 不存在"
        return 1
    fi
    
    # 计算IP数量
    ip_count=$(wc -l < "$ip_file")
    
    echo "检查 $ip_file..."
    echo "当前IP数量: $ip_count"
    
    if [ $ip_count -lt $min_expected ]; then
        echo "警告：$ip_file 只有 $ip_count 个IP，少于预期 ($min_expected)"
        
        # 检查是否有修复脚本
        if [ -f "fix_best_ip.py" ]; then
            echo "运行修复脚本..."
            python3 fix_best_ip.py
        else
            echo "错误：修复脚本 fix_best_ip.py 不存在"
            echo "请手动运行测速脚本：python3 istoreos_cf_speedtest.py"
        fi
    else
        echo "✓ $ip_file 包含足够的IP ($ip_count 个)"
        
        # 显示前5个IP
        echo ""
        echo "前5个最佳IP:"
        head -5 "$ip_file"
    fi
}

# 检查 result.csv 中的IP数量
check_result_csv() {
    local csv_file="result.csv"
    
    if [ ! -f "$csv_file" ]; then
        echo "信息：$csv_file 文件不存在"
        return 0
    fi
    
    # 计算CSV中的IP数量（跳过标题行）
    csv_count=$(tail -n +2 "$csv_file" | wc -l)
    
    echo ""
    echo "检查 $csv_file..."
    echo "测速IP总数: $csv_count"
    
    if [ $csv_count -lt 100 ]; then
        echo "警告：测速IP数量较少，建议重新运行测速"
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "Cloudflare SpeedTest IP 数量检查工具"
    echo "========================================"
    
    check_ip_count
    check_result_csv
    
    echo ""
    echo "========================================"
    echo "检查完成"
    echo "========================================"
}

# 运行主函数
main