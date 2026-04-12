import pandas as pd
import os
from datetime import datetime, timezone

input_file = 'country_asn.csv'

if not os.path.exists(input_file):
    print(f"错误: 未找到文件 {input_file}")
else:
    df = pd.read_csv(input_file)

    print("列名：", df.columns.tolist())

    # country_asn.csv 列名是 start_ip/end_ip/country，需要先看看有没有 network 列
    # 如果有 network 列直接用，没有就用 start_ip
    if 'network' in df.columns:
        col_network = 'network'
        col_country = 'country_code'
    else:
        col_network = None
        col_country = 'country'

    output_dir = 'Country_CIDR'
    os.makedirs(output_dir, exist_ok=True)

    stats = {}
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    import ipaddress

    def get_cidrs(row):
        if col_network:
            net = row[col_network]
            return [str(net)]
        else:
            try:
                return [str(c) for c in ipaddress.summarize_address_range(
                    ipaddress.ip_address(row['start_ip']),
                    ipaddress.ip_address(row['end_ip'])
                )]
            except:
                return []

    # 先展开所有行成 (country, cidr) 对
    rows = []
    for _, row in df.iterrows():
        cc = row[col_country]
        if not isinstance(cc, str):
            continue
        for cidr in get_cidrs(row):
            rows.append((cc, cidr))

    from collections import defaultdict
    v4 = defaultdict(list)
    v6 = defaultdict(list)
    for cc, cidr in rows:
        if ':' in cidr:
            v6[cc].append(cidr)
        else:
            v4[cc].append(cidr)

    for cc, cidrs in v4.items():
        filename = os.path.join(output_dir, f"{cc}.list")
        print(f"生成 {filename} ({len(cidrs)} 条)...")
        with open(filename, 'w') as f:
            f.write(f"# {cc} IPv4 Surge Ruleset\n")
            f.write(f"# Data source: ipinfo.io\n")
            f.write(f"# Updated: {now}\n")
            f.write(f"# Total: {len(cidrs)} rules\n")
            f.write("#\n")
            for net in cidrs:
                f.write(f"IP-CIDR,{net},no-resolve\n")
        stats[cc] = len(cidrs)

    for cc, cidrs in v6.items():
        filename = os.path.join(output_dir, f"{cc}_IPv6.list")
        print(f"生成 {filename} ({len(cidrs)} 条)...")
        with open(filename, 'w') as f:
            f.write(f"# {cc} IPv6 Surge Ruleset\n")
            f.write(f"# Data source: ipinfo.io\n")
            f.write(f"# Updated: {now}\n")
            f.write(f"# Total: {len(cidrs)} rules\n")
            f.write("#\n")
            for net in cidrs:
                f.write(f"IP-CIDR6,{net},no-resolve\n")
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
