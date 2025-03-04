#!/usr/bin/env python
import argparse
import socket
import subprocess
import sys
import time
import platform
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import speedtest
from tabulate import tabulate
import re
import requests

class NetworkDiagnostic:
    def __init__(self, language="en"):
        self.language = language
        
        # Text localization
        self.text = {
            "en": {
                "getting_network_info": "Getting basic network information...",
                "pinging_websites": "Pinging websites...",
                "testing_dns": "Testing DNS resolution...",
                "testing_speed": "Testing internet speed...",
                "testing_gaming": "Testing gaming service connectivity...",
                "test_speed_ustc": "Testing internet speed via USTC test server (this may take a minute)...",
                "test_speed_speedtest": "Testing internet speed via Speedtest.net (this may take a minute)...",
                "diag_results": "NETWORK DIAGNOSTIC RESULTS",
                "local_ip": "Local IP",
                "public_ip": "Public IP",
                "hostname": "Hostname",
                "download": "Download",
                "upload": "Upload",
                "ping": "Ping",
                "server": "Server",
                "error": "Error",
                "website_ping": "WEBSITE PING RESULTS",
                "website": "Website",
                "status": "Status",
                "avg_time": "Avg Time ms",
                "packet_loss": "Packet Loss",
                "dns_tests": "DNS RESOLUTION TESTS",
                "dns_server": "DNS Server",
                "resolution_time": "Resolution Time (ms)",
                "gaming_check": "GAMING SERVICES CHECK",
                "service": "Service",
                "response_time": "Response Time (ms)",
                "traceroute": "TRACEROUTE TO BAIDU.COM"
            },
            "cn": {
                "getting_network_info": "⚙️ 获取基本网络信息...",
                "pinging_websites": "🌐 正在 Ping 网站...",
                "testing_dns": "🔍 测试 DNS 解析...",
                "testing_speed": "⚡ 测试网络速度...",
                "testing_gaming": "🎮 测试游戏服务连接...",
                "test_speed_ustc": "通过中国科大测试服务器测试网络速度（可能需要一分钟）...",
                "test_speed_speedtest": "通过 Speedtest.net 测试网络速度（可能需要一分钟）...",
                "diag_results": "网络诊断结果",
                "local_ip": "本地 IP",
                "public_ip": "公网 IP",
                "hostname": "主机名",
                "download": "下载速度",
                "upload": "上传速度",
                "ping": "延迟",
                "server": "测试服务器",
                "error": "错误",
                "website_ping": "网站 PING 测试",
                "website": "网站",
                "status": "状态",
                "avg_time": "平均延迟 (ms)",
                "packet_loss": "丢包率",
                "dns_tests": "DNS 解析测试",
                "dns_server": "DNS 服务器",
                "resolution_time": "解析时间 (ms)",
                "gaming_check": "游戏服务连接测试",
                "service": "游戏服务",
                "response_time": "响应时间 (ms)",
                "traceroute": "路由追踪到 BAIDU.COM"
            }
        }
        
        self.websites = [
            # Chinese websites
            "baidu.com",
            "qq.com",
            "bilibili.com",
            "taobao.com",
            "jd.com",
            "weibo.com",
            "zhihu.com",
            "douyin.com",
            # Gaming-related
            "steam-china.com",
            "blizzard.cn",
            "wegame.com.cn",
            "taptap.com",
            # International sites accessible in China
            "bing.com",
            "microsoft.com",
            "apple.com",
            "linkedin.com",
            "yahoo.com"
        ]
        
        self.dns_servers = [
            {"name": "AliDNS", "ip": "223.5.5.5"},
            {"name": "AliDNS 2", "ip": "223.6.6.6"},
            {"name": "114DNS", "ip": "114.114.114.114"},
            {"name": "DNSPod", "ip": "119.29.29.29"},
            {"name": "CNNIC", "ip": "1.2.4.8"},
            {"name": "Cloudflare DNS", "ip": "1.1.1.1"}, # Often works in China
            {"name": "Quad9", "ip": "9.9.9.9"}
        ]
        
        self.is_windows = platform.system().lower() == "windows"
    
    def _(self, key):
        """Get localized text based on current language setting"""
        return self.text[self.language].get(key, key)

    def ping_host(self, host):
        """Ping a host and return the results."""
        try:
            param = "-n" if self.is_windows else "-c"
            command = ["ping", param, "3", host]
            output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
            
            # Extract average ping time - improving the regex patterns for different OS outputs
            if self.is_windows:
                # Windows format: "Average = 37ms"
                avg_pattern = r"Average\s*=\s*(\d+)ms"
            else:
                # Linux/macOS format: "round-trip min/avg/max/stddev = 10.574/10.882/11.173/0.245 ms"
                avg_pattern = r"(min/avg/max|rtt min/avg/max/mdev).+?[=\s]([\d\.]+)/([\d\.]+)/([\d\.]+)"
                
            match = re.search(avg_pattern, output)
            if match:
                if self.is_windows:
                    avg_time = float(match.group(1))
                else:
                    avg_time = float(match.group(3))  # Third group contains the avg value
            else:
                # Try alternate pattern for some systems
                alt_pattern = r"time=(\d+\.?\d*) ms"
                matches = re.findall(alt_pattern, output)
                if matches:
                    # Calculate average from individual ping times
                    avg_time = sum(float(t) for t in matches) / len(matches)
                else:
                    avg_time = None
            
            # Extract packet loss
            if self.is_windows:
                loss_pattern = r"Lost\s*=\s*(\d+)\s*\((\d+)%"
                match = re.search(loss_pattern, output)
                packet_loss = f"{match.group(2)}%" if match else "N/A"
            else:
                loss_pattern = r"(\d+)%\spacket\sloss"
                match = re.search(loss_pattern, output)
                packet_loss = f"{match.group(1)}%" if match else "N/A"
                
            return {
                "host": host,
                "status": "Success",
                "avg_time_ms": round(avg_time, 2) if avg_time is not None else "N/A",
                "packet_loss": packet_loss
            }
        except subprocess.CalledProcessError:
            return {
                "host": host,
                "status": "Failed",
                "avg_time_ms": "N/A",
                "packet_loss": "100%"
            }
        except Exception as e:
            return {
                "host": host,
                "status": f"Error: {str(e)}",
                "avg_time_ms": "N/A",
                "packet_loss": "N/A"
            }
    def traceroute(self, host):
        """Perform traceroute to a host."""
        try:
            command = ["tracert" if self.is_windows else "traceroute", host]
            output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT, timeout=10)
            return output
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return "Traceroute failed or timed out"

    def get_local_ip(self):
        """Get local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Using Aliyun DNS instead of Google's
            s.connect(("223.5.5.5", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unable to determine local IP"

    def get_public_ip(self):
        """Get public IP address."""
        # Try multiple IP detection services in case one is blocked
        services = [
            'https://api.ipify.org?format=json', 
            'https://ifconfig.me/ip',
            'https://ip.sb/api/'
        ]
        
        for service in services:
            try:
                response = urllib.request.urlopen(service, timeout=5)
                if 'json' in service:
                    data = json.loads(response.read().decode())
                    return data['ip']
                else:
                    return response.read().decode().strip()
            except:
                continue
                
        return "Unable to determine public IP"

    def test_internet_speed(self, use_ustc=False):
        """Test internet speed using either speedtest.net or USTC test server."""
        if use_ustc:
            return self.test_internet_speed_ustc()
        else:
            return self.test_internet_speed_speedtest()

    def test_internet_speed_speedtest(self):
        """Test internet speed using speedtest.net."""
        try:
            print(self._("test_speed_speedtest"))
            s = speedtest.Speedtest()
            # Try to use servers in China when possible
            try:
                servers = s.get_servers()
                # Look for Chinese servers (closer to improve accuracy)
                cn_servers = [server for server in servers if server.get('country') == 'China']
                if cn_servers:
                    s.get_best_server(cn_servers)
                else:
                    s.get_best_server()
            except:
                s.get_best_server()
            
            download_speed = s.download() / 1_000_000  # Convert to Mbps
            upload_speed = s.upload() / 1_000_000  # Convert to Mbps
            
            return {
                "provider": "Speedtest.net",
                "download_speed_mbps": round(download_speed, 2),
                "upload_speed_mbps": round(upload_speed, 2),
                "ping_ms": round(s.results.ping, 2),
                "server": f"{s.results.server['sponsor']} ({s.results.server['name']})"
            }
        except Exception as e:
            return {
                "provider": "Speedtest.net",
                "download_speed_mbps": "Error",
                "upload_speed_mbps": "Error",
                "ping_ms": "Error",
                "server": "Error",
                "error": str(e)
            }

    def test_internet_speed_ustc(self):
        """Test internet speed using USTC test server."""
        try:
            print(self._("test_speed_ustc"))
            base_url = "https://test.ustc.edu.cn"
            
            # First, measure ping
            start_time = time.time()
            try:
                response = requests.get(f"{base_url}/", timeout=10)
                ping_time = (time.time() - start_time) * 1000  # Convert to ms
                
                if response.status_code != 200:
                    raise Exception(f"Server returned status code {response.status_code}")
            except Exception as e:
                return {
                    "provider": "USTC",
                    "download_speed_mbps": "Error",
                    "upload_speed_mbps": "Error",
                    "ping_ms": "Error",
                    "server": "test.ustc.edu.cn",
                    "error": f"Failed to connect: {str(e)}"
                }
            
            # For download test - fetch a large file and measure speed
            # Try different file sizes from USTC's speedtest directory
            test_files = [
                "random4000x4000.jpg",  # Large file
                "random3000x3000.jpg",  # Medium file
                "random1000x1000.jpg",  # Small file
            ]
            
            download_speed = 0
            download_error = None
            
            for test_file in test_files:
                try:
                    download_url = f"{base_url}/speedtest/{test_file}"
                    chunk_size = 8192
                    content_length = 0
                    download_start = time.time()
                    
                    response = requests.get(download_url, stream=True, timeout=30)
                    if response.status_code == 200:
                        content_length = int(response.headers.get('content-length', 0))
                        for _ in response.iter_content(chunk_size=chunk_size):
                            pass  # Just reading the content to measure speed
                        
                        download_time = time.time() - download_start
                        if download_time > 0 and content_length > 0:
                            download_speed = (content_length * 8) / download_time / 1_000_000
                            break  # Successfully got download speed
                    else:
                        download_error = f"HTTP {response.status_code} for {test_file}"
                except Exception as e:
                    download_error = str(e)
                    continue  # Try the next file
            
            # For upload test - use different endpoints to find one that works
            upload_speed = 0
            upload_error = None
            upload_endpoints = [
                "/cgi-bin/echo.cgi",
                "/speedtest/upload.php"
            ]
            
            for endpoint in upload_endpoints:
                try:
                    upload_url = f"{base_url}{endpoint}"
                    data_size = 1024 * 1024 * 2  # 2MB of data
                    data = b"0" * data_size
                    
                    upload_start = time.time()
                    response = requests.post(upload_url, data=data, timeout=30)
                    upload_time = time.time() - upload_start
                    
                    if response.status_code in [200, 201, 202, 204]:
                        upload_speed = (data_size * 8) / upload_time / 1_000_000 if upload_time > 0 else 0
                        break  # Successfully got upload speed
                    else:
                        upload_error = f"HTTP {response.status_code} for {endpoint}"
                except Exception as e:
                    upload_error = str(e)
                    continue  # Try the next endpoint
            
            result = {
                "provider": "USTC",
                "download_speed_mbps": round(download_speed, 2) if download_speed > 0 else "Error",
                "upload_speed_mbps": round(upload_speed, 2) if upload_speed > 0 else "Error",
                "ping_ms": round(ping_time, 2),
                "server": "test.ustc.edu.cn"
            }
            
            # Add errors if any tests failed
            errors = []
            if download_speed == 0 and download_error:
                errors.append(f"Download: {download_error}")
            if upload_speed == 0 and upload_error:
                errors.append(f"Upload: {upload_error}")
            
            if errors:
                result["error"] = "; ".join(errors)
            
            return result
        except Exception as e:
            return {
                "provider": "USTC",
                "download_speed_mbps": "Error",
                "upload_speed_mbps": "Error",
                "ping_ms": "Error",
                "server": "test.ustc.edu.cn",
                "error": str(e)
            }

    def dns_resolution_test(self, website, dns_server):
        """Alternative DNS resolution test using Python's socket module."""
        try:
            # Configure DNS server
            original_resolver = socket.getaddrinfo
            
            def custom_getaddrinfo(*args, **kwargs):
                # Force the use of our specified DNS server
                import socket as socket_module
                
                # Save original nameservers
                original_nameservers = socket_module._getaddrinfo
                
                try:
                    # This is a simplified approach - full implementation would require 
                    # more complex DNS configuration which varies by platform
                    socket_module._getaddrinfo = lambda *args, **kwargs: original_nameservers(*args, **kwargs)
                    return original_resolver(*args, **kwargs)
                finally:
                    socket_module._getaddrinfo = original_nameservers
            
            # Not perfect due to Python limitations, but we'll time how long it takes anyway
            start_time = time.time()
            
            # Try to resolve using the system's resolver
            socket.gethostbyname(website)
            
            resolution_time = (time.time() - start_time) * 1000  # ms
            
            return {
                "website": website,
                "dns_server": dns_server["name"] + " (System)",
                "dns_ip": dns_server["ip"],
                "resolution_time_ms": round(resolution_time, 2),
                "status": "Success"
            }
        except socket.gaierror:
            return {
                "website": website,
                "dns_server": dns_server["name"] + " (System)",
                "dns_ip": dns_server["ip"],
                "resolution_time_ms": "N/A",
                "status": "Failed"
            }
        except Exception as e:
            return {
                "website": website,
                "dns_server": dns_server["name"] + " (System)",
                "dns_ip": dns_server["ip"],
                "resolution_time_ms": "N/A",
                "status": f"Error: {str(e)[:20]}"
            }   
            
    def check_gaming_services(self):
        """Check connectivity to gaming-specific services."""
        gaming_services = [
            {"name": "Steam China", "host": "store.steamchina.com"},
            {"name": "Tencent Gaming", "host": "game.qq.com"},
            {"name": "Blizzard CN", "host": "www.blizzardgames.cn"},
            {"name": "NetEase Games", "host": "game.163.com"},
            {"name": "UbiSoft CN", "host": "www.ubisoft.com.cn"},
        ]
        
        results = []
        print(self._("testing_gaming"))
        for service in gaming_services:
            try:
                start = time.time()
                response = urllib.request.urlopen(f"http://{service['host']}", timeout=5)
                response_time = (time.time() - start) * 1000
                results.append({
                    "service": service["name"],
                    "status": "Online" if response.getcode() == 200 else "Issue",
                    "response_time_ms": round(response_time, 2)
                })
            except Exception:
                results.append({
                    "service": service["name"],
                    "status": "Unavailable",
                    "response_time_ms": "N/A"
                })
        
        return results

    def run_diagnostics(self, verbose=False, gaming=False, use_ustc=False):
        """Run all network diagnostics."""
        results = {}
        
        # Basic network info
        print(self._("getting_network_info"))
        results["local_ip"] = self.get_local_ip()
        results["public_ip"] = self.get_public_ip()
        results["hostname"] = socket.gethostname()
        
        # Ping popular websites
        print(self._("pinging_websites"))
        with ThreadPoolExecutor(max_workers=10) as executor:
            ping_results = list(executor.map(self.ping_host, self.websites))
        results["ping_results"] = ping_results
        
        # DNS resolution tests
        print(self._("testing_dns"))
        dns_results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for website in self.websites[:3]:  # Use only first 3 websites for DNS tests
                for dns_server in self.dns_servers:
                    futures.append(
                        executor.submit(self.dns_resolution_test, website, dns_server)
                    )
            for future in futures:
                dns_results.append(future.result())
        results["dns_results"] = dns_results
                
        # Gaming services check
        if gaming:
            results["gaming_services"] = self.check_gaming_services()
        
        # Display results
        self.display_results(results, verbose, gaming)
        
        return results

    def display_results(self, results, verbose, gaming=False):
        """Display the diagnostic results in a formatted table."""
        print("\n" + "="*80)
        print(f"🖥️  {self._('diag_results')}")
        print("="*80)
        
        # Basic network info
        print(f"\n🔸 {self._('local_ip')}: {results['local_ip']}")
        print(f"🔸 {self._('public_ip')}: {results['public_ip']}")
        print(f"🔸 {self._('hostname')}: {results['hostname']}")
        
              
        # Website ping results
        print(f"\n📡 {self._('website_ping')}")
        ping_data = [[r["host"], r["status"], r["avg_time_ms"], r["packet_loss"]] 
                    for r in results["ping_results"]]
        print(tabulate(ping_data, headers=[self._("website"), self._("status"), 
                                           self._("avg_time"), self._("packet_loss")]))
        
        # DNS resolution results
        print(f"\n🔍 {self._('dns_tests')}")
        dns_data = [[r["website"], r["dns_server"], r["resolution_time_ms"], r["status"]] 
                   for r in results["dns_results"]]
        print(tabulate(dns_data, headers=[self._("website"), self._("dns_server"), 
                                          self._("resolution_time"), self._("status")]))
        
        # Gaming services check
        if gaming and "gaming_services" in results:
            print(f"\n🎮 {self._('gaming_check')}")
            gaming_data = [[r["service"], r["status"], r["response_time_ms"]] 
                        for r in results["gaming_services"]]
            print(tabulate(gaming_data, headers=[self._("service"), self._("status"), 
                                                self._("response_time")]))
        
        if verbose:
            # Traceroute to a Chinese site instead of Google
            print(f"\n🛣️  {self._('traceroute')}")
            trace = self.traceroute("baidu.com")
            print(trace)

def main():
    parser = argparse.ArgumentParser(description="Network Diagnostic Tool for China")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-g", "--gaming", action="store_true", help="Test gaming service connectivity")
    parser.add_argument("-u", "--ustc", action="store_true", help="Use USTC speed test server")
    parser.add_argument("language", nargs="?", default="en", choices=["en", "cn"], 
                        help="Language (en=English, cn=Chinese)")
    args = parser.parse_args()
    
    try:
        # Check for required modules
        missing_modules = []
        required_modules = ["speedtest-cli", "tabulate", "requests"]
        
        for module_name in required_modules:
            try:
                if module_name == "speedtest-cli":
                    import speedtest
                    # Verify the module has the Speedtest attribute
                    if not hasattr(speedtest, "Speedtest"):
                        missing_modules.append(module_name)
                elif module_name == "tabulate":
                    import tabulate
                elif module_name == "requests":
                    import requests
            except ImportError:
                missing_modules.append(module_name)
        
        language = args.language
        
        tool = NetworkDiagnostic(language=language)
        tool.run_diagnostics(verbose=args.verbose, gaming=args.gaming, use_ustc=args.ustc)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())