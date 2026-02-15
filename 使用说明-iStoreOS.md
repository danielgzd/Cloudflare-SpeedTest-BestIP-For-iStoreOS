# iStoreOS/N1 Cloudflare 测速脚本 - 独立版本

## 简介

这是一个专为 iStoreOS（基于 OpenWrt）和 N1 盒子（ARM64 架构）优化的 Cloudflare 测速脚本。所有功能都整合在一个文件中，方便在资源有限的设备上使用。

## 文件说明

- `istoreos_cf_speedtest.py` - 主脚本，所有功能都在这个文件中
- `使用说明-iStoreOS.md` - 本使用说明文件

## 快速开始

### 1. 下载脚本

```bash
# 下载独立脚本
wget https://raw.githubusercontent.com/danielgzd/Cloudflare-SpeedTest-BestIP/main/istoreos_cf_speedtest.py

# 添加执行权限
chmod +x istoreos_cf_speedtest.py
```

### 2. 运行测速

```bash
# 使用默认配置运行
python3 istoreos_cf_speedtest.py

# 或者直接运行（如果已添加执行权限）
./istoreos_cf_speedtest.py
```

### 3. 查看结果

```bash
# 查看最佳IP列表
cat best_ip.txt

# 查看详细测速结果
cat result.csv

# 查看IP列表文件
cat ip.txt
```

## 命令行参数

```bash
# 查看帮助
python3 istoreos_cf_speedtest.py --help

# 自定义配置运行
python3 istoreos_cf_speedtest.py \
  --max-per-region 5 \
  --max-total 50 \
  --regions "US,JP,KR" \
  --cfst-args "-n 100 -t 2 -o result.csv"
```

### 参数说明

- `--max-per-region` - 每个地区最多选择的IP数量（默认：10）
- `--max-total` - 总共最多选择的IP数量（默认：100）
- `--regions` - 优先处理的地区，逗号分隔（默认：US,GB,IN,JP,KR,SG,HK）
- `--cfst-args` - CloudflareSpeedTest 参数（默认：-n 200 -t 4 -dn 100 -dt 8 -p 0 -o result.csv）
- `--work-dir` - 工作目录，用于缓存文件
- `--output-dir` - 输出目录，结果文件保存位置
- `--no-cache` - 忽略缓存，强制重新下载 cfst 二进制文件
- `--debug` - 启用调试模式，显示详细日志

## 环境变量

支持通过环境变量覆盖所有配置参数：

```bash
# 使用环境变量配置
export MAX_PER_REGION=5
export MAX_TOTAL=50
export PRIORITY_REGIONS="US,JP"
export CFST_ARGS="-n 100 -t 2 -o result.csv"

# 运行脚本（会自动使用环境变量）
python3 istoreos_cf_speedtest.py
```

## 在 iStoreOS/N1 上的使用

### 1. 安装 Python（如果需要）

```bash
# 在 OpenWrt/iStoreOS 上安装 Python3
opkg update
opkg install python3 python3-pip
```

### 2. 运行脚本

```bash
# 下载脚本
cd /tmp
wget https://raw.githubusercontent.com/danielgzd/Cloudflare-SpeedTest-BestIP/main/istoreos_cf_speedtest.py

# 运行测速（适合N1性能的参数）
python3 istoreos_cf_speedtest.py \
  --max-per-region 5 \
  --max-total 30 \
  --cfst-args "-n 100 -t 2 -dn 50 -dt 5 -p 0 -o result.csv"
```

### 3. 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨4点运行）
0 4 * * * cd /root && python3 /root/istoreos_cf_speedtest.py > /var/log/cf_speedtest.log 2>&1
```

## 脚本特性

### 1. 架构自适应
- 自动检测系统架构（ARM64/x86_64/ARMv7等）
- 下载对应的 cfst 二进制文件
- 未知架构回退到 ARM64 版本

### 2. 避免重复下载
- 检查现有 cfst 二进制文件是否可用
- 如果文件存在且可执行，跳过下载步骤
- 减少网络流量和等待时间

### 3. 断点续传
- 支持下载中断后继续下载
- 适合不稳定的网络环境
- 保存部分下载文件，避免重新开始

### 4. 详细的执行日志
- 显示每个步骤的执行状态
- 清晰的成功/失败提示
- 执行时间统计

### 5. 错误处理
- 网络错误重试机制
- 文件权限自动修复
- 详细的错误信息

## 地区支持

脚本支持以下 Cloudflare 数据中心地区：

- **US** - 美国（多个IP段）
- **GB** - 英国（141.101.64.0/18）
- **JP** - 日本（103.21.244.0/22）
- **KR** - 韩国（103.22.200.0/22）
- **SG** - 新加坡（103.31.4.0/22）
- **HK** - 香港（190.93.240.0/20）
- **IN** - 印度（197.234.240.0/22）
- **Other** - 其他地区

## 性能建议

### 对于 N1 盒子
```bash
# 推荐配置（平衡性能和准确性）
python3 istoreos_cf_speedtest.py \
  --max-per-region 5 \
  --max-total 30 \
  --cfst-args "-n 150 -t 3 -dn 80 -dt 6 -p 0 -o result.csv"
```

### 对于低性能设备
```bash
# 最小化资源使用
python3 istoreos_cf_speedtest.py \
  --max-per-region 3 \
  --max-total 20 \
  --cfst-args "-n 80 -t 2 -dn 40 -dt 4 -p 0 -o result.csv"
```

### 对于高性能设备
```bash
# 最大化准确性
python3 istoreos_cf_speedtest.py \
  --max-per-region 10 \
  --max-total 100 \
  --cfst-args "-n 300 -t 6 -dn 150 -dt 10 -p 0 -o result.csv"
```

## 故障排除

### 1. Python 模块缺失
```bash
# 安装必要的模块
pip3 install --upgrade pip
```

### 2. 网络连接问题
```bash
# 测试网络连接
ping -c 3 github.com

# 测试下载
wget https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_arm64.tar.gz
```

### 3. 权限问题
```bash
# 确保有执行权限
chmod +x istoreos_cf_speedtest.py

# 以 root 用户运行（如果需要）
sudo python3 istoreos_cf_speedtest.py
```

### 4. 磁盘空间不足
```bash
# 检查磁盘空间
df -h

# 清理缓存
rm -rf .cfst_cache
```

### 5. 查看详细日志
```bash
# 启用调试模式
python3 istoreos_cf_speedtest.py --debug

# 保存日志到文件
python3 istoreos_cf_speedtest.py > speedtest.log 2>&1
```

## 更新说明

### 版本 1.0
- 初始版本，所有功能整合到一个文件中
- 支持架构自适应下载
- 支持断点续传
- 详细的执行日志
- 命令行参数和环境变量支持

## 许可证

MIT License

## 技术支持

如有问题，请：
1. 查看本使用说明
2. 运行 `python3 istoreos_cf_speedtest.py --help`
3. 启用调试模式 `python3 istoreos_cf_speedtest.py --debug`
4. 查看日志文件

## 注意事项

1. 测速过程可能需要几分钟时间，请耐心等待
2. 确保设备有足够的网络带宽
3. 建议在网络空闲时运行测速
4. 定期更新 IP 列表以获得最佳效果
5. 结果可能因网络环境而异