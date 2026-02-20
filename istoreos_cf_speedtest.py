#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iStoreOS/N1 专用 Cloudflare 测速脚本 - 独立版本
将所有功能整合到一个文件中，方便在 iStoreOS/N1 上使用
"""

import os
import sys
import csv
import json
import shutil
import tarfile
import zipfile
import urllib.request
import subprocess
import platform
from pathlib import Path
import hashlib
import argparse
import time
from datetime import datetime

class CloudflareSpeedTestIStoreOS:
    """iStoreOS/N1 专用的 Cloudflare 测速类"""
    
    def __init__(self, config=None):
        """初始化测速器"""
        self.config = config or {}
        self.repo_root = Path(os.getenv("GITHUB_WORKSPACE", Path.cwd())).resolve()
        self.work_dir = self.repo_root / ".cfst_cache"
        self.setup_directories()
        
        # 默认配置
        self.default_config = {
            'max_per_region': 10,
            'max_total': 100,
            'priority_regions': ["US", "GB", "IN", "JP", "KR", "SG", "HK"],
            'cfst_args': "-n 200 -t 4 -dn 100 -dt 8 -p 0 -o result.csv",
            'ip_txt_url': "https://raw.githubusercontent.com/XIU2/CloudflareSpeedTest/master/ip.txt",
            'work_dir': str(self.work_dir),
            'output_dir': str(self.repo_root),
        }
        
        # 合并配置
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
    
    def setup_directories(self):
        """设置必要的目录"""
        self.work_dir.mkdir(parents=True, exist_ok=True)
        (self.work_dir / "bin").mkdir(parents=True, exist_ok=True)
    
    def get_cfst_url(self):
        """根据系统架构和操作系统返回正确的 cfst 下载链接"""
        machine = platform.machine().lower()
        system = platform.system().lower()
        
        print(f"  检测到系统: {system}, 架构: {machine}")
        
        # macOS (Darwin)
        if system == 'darwin':
            if machine in ('aarch64', 'arm64'):
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_darwin_arm64.zip"
            elif machine in ('x86_64', 'amd64'):
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_darwin_amd64.zip"
            else:
                print(f"  警告: macOS 上未知的架构 {machine}，使用 ARM64 版本")
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_darwin_arm64.zip"
        
        # Linux
        elif system == 'linux':
            if machine in ('aarch64', 'arm64'):
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_arm64.tar.gz"
            elif machine in ('x86_64', 'amd64'):
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_amd64.tar.gz"
            elif machine == 'i386':
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_386.tar.gz"
            elif machine in ('armv7l', 'armv7'):
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_armv7.tar.gz"
            elif machine == 'armv6l':
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_armv6.tar.gz"
            elif machine == 'armv5l':
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_armv5.tar.gz"
            else:
                print(f"  警告: Linux 上未知的架构 {machine}，使用 ARM64 版本")
                return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_arm64.tar.gz"
        
        # 其他系统（Windows 等）
        else:
            print(f"  警告: 不支持的系统 {system}，尝试使用 Linux ARM64 版本")
            return "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/cfst_linux_arm64.tar.gz"
    
    def download_file(self, url: str, dst: Path) -> bool:
        """下载文件，支持断点续传"""
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查是否已存在部分下载的文件
        temp_file = dst.with_suffix(dst.suffix + '.part')
        
        headers = {"User-Agent": "iStoreOS-CFST/1.0"}
        
        # 如果临时文件存在，尝试续传
        if temp_file.exists():
            try:
                with open(temp_file, 'rb') as f:
                    downloaded = len(f.read())
                headers['Range'] = f'bytes={downloaded}-'
                print(f"继续下载: 已下载 {downloaded} 字节")
            except:
                downloaded = 0
        else:
            downloaded = 0
        
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                mode = 'ab' if downloaded > 0 else 'wb'
                with open(temp_file, mode) as f:
                    if downloaded > 0:
                        print(f"从字节 {downloaded} 开始续传...")
                    shutil.copyfileobj(r, f)
            
            # 下载完成后重命名
            temp_file.rename(dst)
            print(f"下载完成: {dst.name} ({dst.stat().st_size} 字节)")
            return True
            
        except Exception as e:
            print(f"下载失败: {e}")
            if temp_file.exists():
                print(f"部分文件保存在: {temp_file}")
            return False
    
    def extract_archive(self, archive: Path, out_dir: Path) -> bool:
        """解压归档文件"""
        out_dir.mkdir(parents=True, exist_ok=True)
        name = archive.name.lower()

        try:
            print(f"  解压文件: {archive.name}")
            
            if name.endswith(".tar.gz") or name.endswith(".tgz"):
                with tarfile.open(archive, "r:gz") as t:
                    members = t.getmembers()
                    print(f"  找到 {len(members)} 个文件")
                    for member in members[:5]:  # 显示前5个文件
                        print(f"    - {member.name}")
                    if len(members) > 5:
                        print(f"    ... 还有 {len(members)-5} 个文件")
                    
                    t.extractall(out_dir)
                    print(f"  解压完成到: {out_dir}")
                return True

            if name.endswith(".zip"):
                with zipfile.ZipFile(archive, "r") as z:
                    members = z.namelist()
                    print(f"  找到 {len(members)} 个文件")
                    for member in members[:5]:
                        print(f"    - {member}")
                    if len(members) > 5:
                        print(f"    ... 还有 {len(members)-5} 个文件")
                    
                    z.extractall(out_dir)
                    print(f"  解压完成到: {out_dir}")
                return True
            
            print(f"不支持的归档格式: {archive}")
            return False
        except Exception as e:
            print(f"解压失败: {e}")
            return False
    
    def find_cfst_binary(self, bin_dir: Path) -> Path:
        """查找 cfst 二进制文件"""
        # 首先检查常见的文件名
        for c in (bin_dir / "cfst", bin_dir / "CloudflareST", bin_dir / "cloudflareST"):
            if c.exists():
                return c
        
        # 递归查找
        for p in bin_dir.rglob("*"):
            if p.is_file() and p.name in ("cfst", "CloudflareST"):
                return p
        
        raise FileNotFoundError("在解压目录中未找到 cfst 二进制文件")
    
    def check_cfst_executable(self, cfst_path: Path) -> bool:
        """检查 cfst 二进制文件是否可执行"""
        if not cfst_path.exists():
            print(f"  ✗ 文件不存在: {cfst_path}")
            return False
        
        try:
            # 检查文件大小
            file_size = cfst_path.stat().st_size
            if file_size < 1000:  # 至少1KB
                print(f"  ✗ 文件大小异常: {file_size} 字节")
                return False
            
            # 检查文件权限
            if not os.access(cfst_path, os.X_OK):
                print(f"  ⚠ 文件不可执行，设置权限...")
                cfst_path.chmod(0o755)
            
            # 在 iStoreOS/OpenWrt 上，第一次运行二进制文件可能需要额外时间
            # 添加预热步骤：先运行一次简单的命令
            print(f"  ⚠ 预热二进制文件（iStoreOS/OpenWrt 兼容性）...")
            try:
                # 尝试运行一个简单的命令来预热
                subprocess.run(
                    [str(cfst_path), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            except:
                # 预热失败也没关系，继续验证
                pass
            
            # 尝试不同的版本参数，增加超时时间并添加重试
            version_params = ["--version", "-version", "-v", "--v", "-V", "--V"]
            
            max_retries = 3
            for attempt in range(max_retries):
                for param in version_params:
                    try:
                        if attempt > 0:
                            print(f"  ⚠ 尝试验证参数: {param} (第 {attempt + 1} 次重试)")
                        else:
                            print(f"  ⚠ 尝试验证参数: {param}")
                        
                        # 增加超时时间到15秒，特别是对于ARM设备
                        timeout_seconds = 15 if attempt == 0 else 20
                        result = subprocess.run(
                            [str(cfst_path), param],
                            capture_output=True,
                            text=True,
                            timeout=timeout_seconds
                        )
                        
                        if result.returncode == 0:
                            version_output = result.stdout.strip() or result.stderr.strip()
                            if version_output:
                                print(f"  ✓ 验证成功: {version_output}")
                            else:
                                print(f"  ✓ 验证成功 (无版本输出)")
                            return True
                        elif "flag provided but not defined" in result.stderr:
                            # 参数不支持，尝试下一个
                            continue
                        else:
                            # 其他错误，可能是二进制文件有问题
                            print(f"  ✗ 验证失败，退出码: {result.returncode}")
                            if result.stderr:
                                print(f"    错误输出: {result.stderr[:100]}")
                            break
                            
                    except subprocess.TimeoutExpired:
                        print(f"  ✗ 验证超时 (第 {attempt + 1} 次尝试)")
                        if attempt < max_retries - 1:
                            print(f"    等待 2 秒后重试...")
                            time.sleep(2)
                        else:
                            print(f"  ✗ 所有重试均超时")
                            return False
                    except Exception as e:
                        print(f"  ✗ 验证异常: {e}")
                        if attempt < max_retries - 1:
                            print(f"    等待 2 秒后重试...")
                            time.sleep(2)
                        else:
                            return False
                        continue
            
            # 如果所有参数都失败，尝试运行不带参数的帮助命令
            print(f"  ⚠ 尝试运行帮助命令...")
            try:
                result = subprocess.run(
                    [str(cfst_path)],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0 or result.returncode == 1:  # 帮助命令通常返回0或1
                    print(f"  ✓ 二进制文件可执行 (帮助命令成功)")
                    return True
                else:
                    print(f"  ✗ 帮助命令失败，退出码: {result.returncode}")
                    return False
                    
            except Exception as e:
                print(f"  ✗ 帮助命令异常: {e}")
                return False
                
        except Exception as e:
            print(f"  ✗ 验证过程异常: {e}")
            return False
    
    def run_command(self, cmd: list[str], cwd=None) -> bool:
        """运行命令并显示输出"""
        print(">>", " ".join(cmd))
        try:
            subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e}")
            return False
    
    def get_region_for_ip(self, ip: str) -> str:
        """根据 IP 地址判断地区"""
        ip_parts = ip.split('.')
        if len(ip_parts) < 2:
            return "Other"
        
        first_octet = int(ip_parts[0])
        second_octet = int(ip_parts[1])
        
        # 美国IP段 (US)
        if first_octet == 104 and 16 <= second_octet <= 31:
            return "US"
        elif first_octet == 172 and 64 <= second_octet <= 71:
            return "US"
        elif first_octet == 162 and second_octet in [158, 159]:
            return "US"
        elif first_octet == 198 and second_octet == 41:
            return "US"
        elif first_octet == 108 and second_octet == 162:
            return "US"
        elif first_octet == 172 and 65 <= second_octet <= 67:
            return "US"
        elif 172 <= first_octet <= 173:  # 扩展美国IP段
            return "US"
        
        # 英国IP段 (GB)
        elif first_octet == 141 and second_octet == 101:
            return "GB"
        
        # 日本IP段 (JP)
        elif first_octet == 103 and second_octet == 21:
            return "JP"
        elif first_octet == 103 and second_octet == 22:
            return "JP"
        
        # 韩国IP段 (KR)
        elif first_octet == 103 and second_octet == 22:
            return "KR"
        elif first_octet == 103 and second_octet == 23:
            return "KR"
        
        # 新加坡IP段 (SG)
        elif first_octet == 103 and second_octet == 31:
            return "SG"
        elif first_octet == 103 and second_octet == 4:
            return "SG"
        
        # 香港IP段 (HK)
        elif first_octet == 190 and second_octet == 93:
            return "HK"
        elif first_octet == 188 and second_octet == 114:
            return "HK"
        
        # 印度IP段 (IN)
        elif first_octet == 197 and second_octet == 234:
            return "IN"
        
        # 德国IP段 (DE)
        elif first_octet == 188 and second_octet == 114:
            return "DE"
        
        # 澳大利亚IP段 (AU)
        elif first_octet == 104 and second_octet == 28:
            return "AU"
        
        # 加拿大IP段 (CA)
        elif first_octet == 104 and second_octet == 20:
            return "CA"
        
        # 巴西IP段 (BR)
        elif first_octet == 104 and second_octet == 24:
            return "BR"
        
        # 法国IP段 (FR)
        elif first_octet == 104 and second_octet == 27:
            return "FR"
        
        # 荷兰IP段 (NL)
        elif first_octet == 104 and second_octet == 18:
            return "NL"
        
        # 其他地区 - 根据常见Cloudflare IP段分类
        elif first_octet == 173 and second_octet == 245:
            return "US"  # Cloudflare美国节点
        elif first_octet == 198 and second_octet == 41:
            return "US"  # Cloudflare美国节点
        elif first_octet == 104 and second_octet <= 15:
            return "US"  # Cloudflare美国节点
        elif first_octet == 104 and 32 <= second_octet <= 47:
            return "EU"  # 欧洲节点
        elif first_octet == 104 and 48 <= second_octet <= 63:
            return "ASIA"  # 亚洲节点
        
        # 其他地区
        else:
            return "Other"
    
    def parse_top_ips_by_region(self, csv_path: Path) -> list[str]:
        """解析CSV文件，按地区选择最快的前N个IP"""
        ip_data = []  # 存储(ip, latency, region)元组
        try:
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    return []
                
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
                    
                    # 获取地区
                    region = self.get_region_for_ip(ip)
                    
                    ip_data.append((ip, latency, region))
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return []
        
        # 按延迟排序
        ip_data.sort(key=lambda x: x[1])
        
        # 按地区分组选择IP
        selected_ips = []
        region_counts = {}
        regions = self.config['priority_regions']
        max_per_region = self.config['max_per_region']
        max_total = self.config['max_total']
        
        # 初始化地区计数
        for region in regions:
            region_counts[region] = 0
        
        # 首先选择指定地区的IP
        for ip, latency, region in ip_data:
            if region in regions and region_counts.get(region, 0) < max_per_region:
                selected_ips.append(ip)
                region_counts[region] = region_counts.get(region, 0) + 1
            
            # 如果达到总数限制，停止
            if len(selected_ips) >= max_total:
                break
        
        # 如果还有空位，选择其他地区的IP
        if len(selected_ips) < max_total:
            for ip, latency, region in ip_data:
                if ip in selected_ips:
                    continue
                    
                if region not in regions:
                    selected_ips.append(ip)
                
                if len(selected_ips) >= max_total:
                    break
        
        return selected_ips
    
    def ensure_ip_txt(self) -> bool:
        """确保 ip.txt 文件存在"""
        ip_txt = self.repo_root / "ip.txt"
        if ip_txt.exists():
            print(f"✓ ip.txt 已存在")
            return True
        
        print(f"下载 ip.txt...")
        print(f"从: {self.config['ip_txt_url']}")
        
        if self.download_file(self.config['ip_txt_url'], ip_txt):
            print(f"✓ ip.txt 下载完成")
            return True
        else:
            print(f"✗ ip.txt 下载失败")
            return False
    
    def prepare_cfst_binary(self):
        """准备 cfst 二进制文件"""
        # 根据URL确定文件扩展名
        cfst_url = self.get_cfst_url()
        
        # 从URL提取文件名
        import urllib.parse
        url_path = urllib.parse.urlparse(cfst_url).path
        filename = os.path.basename(url_path)
        
        archive = self.work_dir / filename
        bin_dir = self.work_dir / "bin"
        cfst_bin = bin_dir / "cfst"
        
        # 检查是否已有可用的 cfst 二进制文件
        if cfst_bin.exists() and self.check_cfst_executable(cfst_bin):
            print(f"✓ cfst 二进制文件已存在且可用")
            return cfst_bin
        
        print(f"准备 cfst 二进制文件...")
        
        # 下载归档文件（如果不存在）
        if not archive.exists():
            print(f"下载 cfst ({platform.machine()})...")
            print(f"从: {cfst_url}")
            
            if not self.download_file(cfst_url, archive):
                print(f"✗ 下载失败")
                return None
            print(f"✓ 下载完成")
        else:
            print(f"✓ 归档文件已存在: {archive.name}")
        
        # 解压归档文件
        if bin_dir.exists():
            shutil.rmtree(bin_dir)
        
        print(f"解压归档文件...")
        if not self.extract_archive(archive, bin_dir):
            print(f"✗ 解压失败")
            return None
        print(f"✓ 解压完成")
        
        # 查找并设置权限
        try:
            cfst_bin = self.find_cfst_binary(bin_dir)
            cfst_bin.chmod(0o755)
            print(f"✓ 找到 cfst: {cfst_bin}")
            
            # 验证可执行性
            if self.check_cfst_executable(cfst_bin):
                print(f"✓ cfst 验证通过")
                return cfst_bin
            else:
                print(f"✗ cfst 验证失败")
                return None
        except Exception as e:
            print(f"✗ 查找 cfst 失败: {e}")
            return None
    
    def run_speed_test(self, cfst_bin: Path) -> bool:
        """运行测速"""
        print(f"运行 Cloudflare 测速...")
        cmd = [str(cfst_bin)] + self.config['cfst_args'].split()
        
        if self.run_command(cmd, cwd=self.repo_root):
            print(f"✓ 测速完成")
            return True
        else:
            print(f"✗ 测速失败")
            return False
    
    def process_results(self) -> bool:
        """处理测速结果"""
        csv_path = self.repo_root / "result.csv"
        if not csv_path.exists():
            print(f"✗ 错误: result.csv 未找到")
            print(f"   请检查 CFST_ARGS 参数是否正确指定了输出文件")
            return False
        
        print(f"处理测速结果...")
        print(f"结果文件: {csv_path}")
        
        ips = self.parse_top_ips_by_region(csv_path)
        
        if not ips:
            print(f"⚠ 警告: 未找到有效的IP地址")
            return False
        
        # 保存最佳IP
        best_path = self.repo_root / "best_ip.txt"
        best_path.write_text("\n".join(ips) + ("\n" if ips else ""), encoding="utf-8")
        
        print(f"✓ 找到 {len(ips)} 个最佳IP")
        print(f"保存到: {best_path}")
        return True
    
    def run(self) -> bool:
        """运行完整的测速流程"""
        print("=" * 60)
        print("iStoreOS/N1 Cloudflare 测速脚本")
        print(f"系统架构: {platform.machine()}")
        print(f"Python版本: {platform.python_version()}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        print(f"工作目录: {self.repo_root}")
        print(f"配置参数:")
        print(f"  - 每个地区最多IP数: {self.config['max_per_region']}")
        print(f"  - 总共最多IP数: {self.config['max_total']}")
        print(f"  - 优先地区: {', '.join(self.config['priority_regions'])}")
        print(f"  - CFST参数: {self.config['cfst_args']}")
        
        # 1. 确保 ip.txt 存在
        if not self.ensure_ip_txt():
            return False
        
        # 2. 准备 cfst 二进制文件
        cfst_bin = self.prepare_cfst_binary()
        if not cfst_bin:
            return False
        
        # 3. 运行测速
        if not self.run_speed_test(cfst_bin):
            return False
        
        # 4. 处理结果
        if not self.process_results():
            return False
        
        # 5. 输出摘要
        self.print_summary()
        return True
    
    def print_summary(self):
        """输出执行摘要"""
        csv_path = self.repo_root / "result.csv"
        best_path = self.repo_root / "best_ip.txt"
        ip_txt = self.repo_root / "ip.txt"
        
        print(f"\n" + "=" * 60)
        print(f"任务完成!")
        print(f"  - 优先地区: {', '.join(self.config['priority_regions'])}")
        print(f"  - 每个地区最多IP数: {self.config['max_per_region']}")
        
        # 读取实际找到的IP数量
        if best_path.exists():
            with open(best_path, 'r', encoding='utf-8') as f:
                ips = [line.strip() for line in f if line.strip()]
                print(f"  - 总共IP数: {len(ips)}/{self.config['max_total']}")
        
        print(f"  - 结果文件: {csv_path}")
        print(f"  - 最佳IP文件: {best_path}")
        print(f"  - IP列表文件: {ip_txt}")
        print(f"  - 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示前5个IP
        if best_path.exists():
            with open(best_path, 'r', encoding='utf-8') as f:
                ips = [line.strip() for line in f if line.strip()]
                if ips:
                    print(f"\n前5个最佳IP:")
                    for i, ip in enumerate(ips[:5], 1):
                        print(f"   {i}. {ip}")
        
        print("\n" + "=" * 60)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='iStoreOS/N1 Cloudflare 测速脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 使用默认配置
  %(prog)s --max-per-region 5 --max-total 50
  %(prog)s --regions US,JP,KR
  %(prog)s --cfst-args "-n 100 -t 2 -o result.csv"
  
环境变量:
  支持通过环境变量覆盖所有配置参数
        """
    )
    
    parser.add_argument('--max-per-region', type=int, default=10,
                       help='每个地区最多选择的IP数量 (默认: 10)')
    parser.add_argument('--max-total', type=int, default=100,
                       help='总共最多选择的IP数量 (默认: 100)')
    parser.add_argument('--regions', type=str, default='US,GB,IN,JP,KR,SG,HK',
                       help='优先处理的地区，逗号分隔 (默认: US,GB,IN,JP,KR,SG,HK)')
    parser.add_argument('--cfst-args', type=str, 
                       default='-n 200 -t 4 -dn 100 -dt 8 -p 0 -o result.csv',
                       help='CloudflareSpeedTest 参数 (默认: -n 200 -t 4 -dn 100 -dt 8 -p 0 -o result.csv)')
    parser.add_argument('--work-dir', type=str,
                       help='工作目录，用于缓存文件 (默认: 当前目录/.cfst_cache)')
    parser.add_argument('--output-dir', type=str,
                       help='输出目录，结果文件保存位置 (默认: 当前目录)')
    parser.add_argument('--no-cache', action='store_true',
                       help='忽略缓存，强制重新下载 cfst 二进制文件')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式，显示详细日志')
    
    return parser.parse_args()

def config_from_args(args):
    """从命令行参数创建配置"""
    config = {
        'max_per_region': args.max_per_region,
        'max_total': args.max_total,
        'priority_regions': [r.strip() for r in args.regions.split(',') if r.strip()],
        'cfst_args': args.cfst_args,
    }
    
    if args.work_dir:
        config['work_dir'] = args.work_dir
    if args.output_dir:
        config['output_dir'] = args.output_dir
    
    # 环境变量覆盖
    env_vars = {
        'MAX_PER_REGION': 'max_per_region',
        'MAX_TOTAL': 'max_total',
        'PRIORITY_REGIONS': 'priority_regions',
        'CFST_ARGS': 'cfst_args',
    }
    
    for env_var, config_key in env_vars.items():
        if env_var in os.environ:
            if config_key == 'priority_regions':
                config[config_key] = [r.strip() for r in os.environ[env_var].split(',') if r.strip()]
            elif config_key in ['max_per_region', 'max_total']:
                config[config_key] = int(os.environ[env_var])
            else:
                config[config_key] = os.environ[env_var]
    
    return config

def main():
    """主函数"""
    args = parse_arguments()
    
    # 创建配置
    config = config_from_args(args)
    
    # 创建测速器实例
    speedtest = CloudflareSpeedTestIStoreOS(config)
    
    # 运行测速
    try:
        success = speedtest.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        return 130
    except Exception as e:
        print(f"\n发生未预期的错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
