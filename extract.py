import pandas as pd
import os
from datetime import datetime, timezone

input_file = 'ipinfo_lite.csv'

if not os.path.exists(input_file):
    print(f"错误: 未找到文件 {input_file}")
else:
    df = pd.read_csv(input_file)

    df_ipv4 = df[~df['network'].str.contains(':')].copy()
    df_ipv6 = df[df['network'].str.contains(':')].copy()

    output_dir = 'Country_CIDR'
    os.makedirs(output_dir, exist_ok=True)

    stats = {}
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    for cc, group in df_ipv4.groupby('country_code'):
        filename = os.path.join(output_dir, f"{cc}.list")
        cidrs = list(group['network'])
        print(f"生成 {filename} ({len(cidrs)} 条)...")
        with open(filename, 'w') as f:
            f.write(f"# {cc} IPv4 Surge Ruleset\n")
            f.write(f"# Data source: ipinfo.io (IPInfo Lite)\n")
            f.write(f"# Updated: {now}\n")
            f.write(f"# Total: {len(cidrs)} rules\n")
            f.write("#\n")
            for net in cidrs:
                if '/' not in str(net):
                    net = f"{net}/32"
                f.write(f"IP-CIDR,{net}\n")
        stats[cc] = len(cidrs)

    for cc, group in df_ipv6.groupby('country_code'):
        filename = os.path.join(output_dir, f"{cc}_IPv6.list")
        cidrs = list(group['network'])
        print(f"生成 {filename} ({len(cidrs)} 条)...")
        with open(filename, 'w') as f:
            f.write(f"# {cc} IPv6 Surge Ruleset\n")
            f.write(f"# Data source: ipinfo.io (IPInfo Lite)\n")
            f.write(f"# Updated: {now}\n")
            f.write(f"# Total: {len(cidrs)} rules\n")
            f.write("#\n")
            for net in cidrs:
                if '/' not in str(net):
                    net = f"{net}/128"
                f.write(f"IP-CIDR6,{net}\n")
        stats[f"{cc}_IPv6"] = len(cidrs)

    total_countries = len(set(k.replace('_IPv6', '') for k in stats))
    total_cidrs = sum(stats.values())
    top20 = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:20]
    top20_rows = "\n".join(f"| {cc} | {count} |" for cc, count in top20)

    readme = f"""# Surge Ruleset - Global IP by Country

**Note:** This data is automatically updated daily from [ipinfo.io](https://ipinfo.io/).

---

## Statistics

**Last Updated:** {now}

### Overall

- **Total Countries/Regions with data:** {total_countries}
- **Total IP CIDR blocks:** {total_cidrs}

### Top 20 Countries by CIDR Count

| Country Code | CIDR Count |
| --- | --- |
{top20_rows}

---

*This information was automatically updated by GitHub Actions on {now}*
"""

    with open('README.md', 'w') as f:
        f.write(readme)

    print("全部完成！")
