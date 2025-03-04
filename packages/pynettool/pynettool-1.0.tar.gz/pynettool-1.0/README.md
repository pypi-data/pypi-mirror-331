# pynettool

A command line tool that displays comprehensive information about the internet connection of the current system, designed with special considerations for networks in China.

## Features

- 📊 Basic network information (local IP, public IP, hostname)
- 🌐 Ping tests to popular websites
- ⚡ Internet speed testing (both Speedtest.net and USTC test server)
- 🔍 DNS resolution testing with multiple DNS servers
- 🎮 Gaming service connectivity checks
- 🛣️ Network route tracing
- 🌏 Multi-language support (English and Chinese)

## Installation

```bash
pip install pynettool
```

Required dependencies:
- speedtest-cli
- tabulate
- requests
- distro

## Usage

Run the basic network test:

```bash
pynettool
```

### Options

```
pynettool [-v] [-g] [-u] [language]
```

- `-v`, `--verbose`: Enable verbose output including traceroute
- `-g`, `--gaming`: Test gaming service connectivity
- `-u`, `--ustc`: Use USTC speed test server (may be faster in China)
- `language`: Select language (`en` for English or `cn` for Chinese)

### Examples

Run in verbose mode:
```bash
pynettool -v
```

Run with gaming service checks in Chinese:
```bash
pynettool -g cn
```

Run with USTC speed test server:
```bash
pynettool -u
```

## Output

The tool provides detailed information including:

1. Basic network details
   - Local IP address
   - Public IP address
   - Hostname

2. Website ping results
   - Status (Success/Failed)
   - Average response time
   - Packet loss percentage

3. DNS resolution tests
   - Multiple DNS servers (AliDNS, 114DNS, DNSPod, etc.)
   - Resolution time
   - Status

4. Internet speed test results (when using `-u` flag)
   - Download speed
   - Upload speed 
   - Ping latency
   - Server information

5. Gaming service connectivity (when using `-g` flag)
   - Status checks for Steam China, Tencent Gaming, etc.
   - Response times

6. Traceroute information (when using `-v` flag)
   - Network path to baidu.com

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.