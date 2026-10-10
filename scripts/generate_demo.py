#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动扫描 subscribe.txt -> 解析/归类/过滤 -> 生成 config/user_demo.txt"""
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBSCRIBE = os.path.join(ROOT, "config", "subscribe.txt")
OUT = os.path.join(ROOT, "config", "user_demo.txt")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"

NOISE_GROUPS = re.compile(r"更新时间|专享|电影点播|电视剧|直播回看|回看|预告|相关|源", re.I)

CAT_MAP = {
    "央视频道": "📺央视频道", "央视付费": "💰央视付费频道", "央视数字": "💰央视付费频道",
    "卫视频道": "📡卫视频道", "专享卫视": "📡卫视频道",
    "港澳台": "🌊港·澳·台", "台湾台": "🌊港·澳·台",
    "广东频道": "☘️广东频道", "浙江频道": "☘️浙江频道", "湖南频道": "☘️湖南频道",
    "上海频道": "☘️上海频道", "湖北频道": "☘️湖北频道", "山东频道": "☘️山东频道",
    "江苏频道": "☘️江苏频道", "黑龙江频道": "☘️黑龙江频道", "河北频道": "☘️河北频道",
    "河南频道": "☘️河南频道", "陕西频道": "☘️陕西频道", "海南频道": "☘️海南频道",
    "北京频道": "☘️北京频道", "天津频道": "☘️天津频道", "山西频道": "☘️山西频道",
    "内蒙古频道": "☘️内蒙古频道", "辽宁频道": "☘️辽宁频道", "吉林频道": "☘️吉林频道",
    "安徽频道": "☘️安徽频道", "福建频道": "☘️福建频道", "江西频道": "☘️江西频道",
    "四川频道": "☘️四川频道", "贵州频道": "☘️贵州频道", "云南频道": "☘️云南频道",
    "广西频道": "☘️广西频道", "甘肃频道": "☘️甘肃频道", "青海频道": "☘️青海频道",
    "宁夏频道": "☘️宁夏频道", "新疆频道": "☘️新疆频道", "西藏频道": "☘️西藏频道",
    "重庆频道": "☘️重庆频道", "地方频道": "☘️地方频道",
    "动画": "🪁动画少儿", "少儿": "🪁动画少儿", "电影": "🎬电影频道",
    "体育": "🏀体育频道", "游戏": "🎮游戏频道", "音乐": "🎵音乐频道",
    "纪实": "🎞️纪实频道", "新闻": "📰新闻频道", "教育": "🏫教育频道",
    "数字": "🔢数字频道", "海外": "🌍海外频道", "国际": "🌍海外频道",
}

ORDER = ["📺央视频道","💰央视付费频道","📡卫视频道","🌊港·澳·台","☘️广东频道","☘️浙江频道","☘️湖南频道","☘️上海频道","☘️湖北频道","☘️山东频道","☘️江苏频道","☘️黑龙江频道","☘️河北频道","☘️河南频道","☘️陕西频道","☘️海南频道","☘️北京频道","☘️天津频道","☘️山西频道","☘️内蒙古频道","☘️辽宁频道","☘️吉林频道","☘️安徽频道","☘️福建频道","☘️江西频道","☘️四川频道","☘️贵州频道","☘️云南频道","☘️广西频道","☘️甘肃频道","☘️青海频道","☘️宁夏频道","☘️新疆频道","☘️西藏频道","☘️重庆频道","☘️地方频道","🏀体育频道","🎬电影频道","🪁动画少儿","🎵音乐频道","🎞️纪实频道","📰新闻频道","🏫教育频道","🎮游戏频道","🔢数字频道","🌍海外频道"]

JUNK = re.compile(
    r"《|》|「|」|[Dd][Jj]|车载|串烧|舞曲|神曲|情歌|老歌|伤感|歌曲|MV|解说|春晚"
    r"|第.?[一二三四五六七八九十百\d]{1,3}集|[\d]{1,3}集$"
    r"|^[0-9]+首|^20\d\d|^\d+年|^\d+首"
    r"|泰山|黄山|乌镇|张家界|丽江|峨眉|桂林|漓江|九华山|西递|宏村|鼓浪|崂山|鸣沙|月牙泉|张掖|七彩丹霞|水长城|飞来石|乐山大佛|玉龙雪山|普陀山|黄果树|武夷山|朱鹮|电视塔|南浦大桥|玄武湖|望乡台|天涯石|五彩池|雪山|瀑布|栈道|悬崖|景区|全景|鸟瞰|宝峰湖|玻璃栈道|醉美|沙滩|半山亭|天界山|观景|坐观|日出|云海|灯杆山|定海神针|马牙山|龙形田|西市河|赏樱阁|蓝月谷|崇圣寺|冰川|大水车|万古楼|蓝印花布"
    r"|甄嬛传|雪中悍刀行|拆弹专家|九品芝麻官|无间道|让子弹飞|人在囧途|卧虎藏龙|倩女幽魂|我不是药神|龙门飞甲|满城尽带黄金甲|变形金刚|寒战|死神来了|爱难求|爱一回|原谅你的谎|蜜雪冰城|闯天涯|英雄泪|红尘|朋友|拥抱你离去"
    r"|^CCTV\d{3,}$"
)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def decode(data):
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "ignore")

def is_junk(name):
    return bool(JUNK.search(name))

def get_cat(group, name):
    for k, v in CAT_MAP.items():
        if group == k:
            return v
    for k, v in CAT_MAP.items():
        if k and re.search(k, group):
            return v
    if re.match(r"^CCTV|^CGTN|^CETV", name):
        return "📺央视频道"
    if "卫视" in name:
        return "📡卫视频道"
    if re.search(r"凤凰|TVB|翡翠|明珠|东森|TVBS|纬来|三立|香港|澳门|无线|J2|Viutv|星空|靖天|寰宇|中天", name):
        return "🌊港·澳·台"
    if re.search(r"体育|足球|篮球|围棋|钓鱼|赛车|搏击|高尔夫", name):
        return "🏀体育频道"
    if re.search(r"电影|影院|影视频道|CHC|家庭影院|剧场", name):
        return "🎬电影频道"
    if re.search(r"卡通|动画|少儿|金鹰|优漫|炫动|嘉佳|哈哈", name):
        return "🪁动画少儿"
    if re.search(r"音乐|歌声|风云音乐", name):
        return "🎵音乐频道"
    if re.search(r"纪实|纪录|地理|人文", name):
        return "🎞️纪实频道"
    if re.search(r"新闻|资讯", name):
        return "📰新闻频道"
    if re.search(r"教育|课堂", name):
        return "🏫教育频道"
    if re.search(r"游戏", name):
        return "🎮游戏频道"
    if re.search(r"4K|高清|超清", name):
        return "🔢数字频道"
    return "📡卫视频道"

def parse_source(url):
    pairs = []
    try:
        data = fetch(url)
        text = decode(data).replace("\r", "")
    except Exception:
        return pairs
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln.startswith("#EXTINF"):
            continue
        name, group = "", ""
        m = re.search(r'group-title="([^"]*)"', ln)
        if m:
            group = m.group(1).strip()
        m = re.search(r'tvg-name="([^"]*)"', ln)
        if m and m.group(1).strip():
            name = m.group(1).strip()
        else:
            i = ln.rfind(",")
            if i >= 0:
                name = ln[i + 1:].strip()
        if not name:
            continue
        pairs.append((name, group))
    return pairs

def main():
    urls = []
    with open(SUBSCRIBE, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            urls.append(ln)
    bucket = {}
    total_inf = 0
    for url in urls:
        for name, group in parse_source(url):
            total_inf += 1
            if re.search(NOISE_GROUPS, group):
                continue
            if is_junk(name):
                continue
            bucket.setdefault(get_cat(group, name), set()).add(name)
    lines, count = [], 0
    for cat in ORDER:
        if cat in bucket and bucket[cat]:
            lines.append(f"{cat},#genre#")
            for n in sorted(bucket[cat]):
                lines.append(n)
                count += 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"scanned urls={len(urls)} inf={total_inf} categories={len(bucket)} channels={count}")

if __name__ == "__main__":
    main()
