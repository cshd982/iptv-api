#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动扫描 subscribe.txt -> 解析/归类/过滤 -> 生成 config/user_demo.txt
简化版：
  1. 过滤国外台/外语台（纯英文/日文/韩文等非中文台名）
  2. 过滤直播频道（虎牙/斗鱼/哔哩直播/网红直播等）
  3. 过滤资源很少的频道（只在极少数源出现的冷门台）
  4. 台号归一化：CCTV-1/CCTV1/CCTV-1 综合/CCTV-1高清 归拢成一个主台号
  5. 自然排序：CCTV-1,2,3,...10,11
  6. 高清/4K 单独分类
"""
import os
import re
import urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBSCRIBE = os.path.join(ROOT, "config", "subscribe.txt")
OUT = os.path.join(ROOT, "config", "user_demo.txt")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"

NOISE_GROUPS = re.compile(r"更新时间|专享|电影点播|电视剧|直播回看|回看|预告|相关|源", re.I)

# ---- 省份表：中文省名 + 英文/拼音名 -> 分类标题 ----
PROV = {
    "北京": ("☘️北京频道", r"北京|Beijing|BRTV|BTV"),
    "上海": ("☘️上海频道", r"上海|Shanghai"),
    "天津": ("☘️天津频道", r"天津|Tianjin"),
    "重庆": ("☘️重庆频道", r"重庆|Chongqing"),
    "河北": ("☘️河北频道", r"河北|Hebei|石家庄|Shijiazhuang"),
    "山西": ("☘️山西频道", r"山西|Shanxi|太原|Taiyuan"),
    "内蒙古": ("☘️内蒙古频道", r"内蒙古|Nei Monggol|Inner Mongolia|呼和浩特|Hohhot"),
    "辽宁": ("☘️辽宁频道", r"辽宁|Liaoning|沈阳|Shenyang|大连|Dalian"),
    "吉林": ("☘️吉林频道", r"吉林|Jilin|长春|Changchun"),
    "黑龙江": ("☘️黑龙江频道", r"黑龙江|Heilongjiang|哈尔滨|Harbin"),
    "江苏": ("☘️江苏频道", r"江苏|Jiangsu|南京|Nanjing"),
    "浙江": ("☘️浙江频道", r"浙江|Zhejiang|杭州|Hangzhou"),
    "安徽": ("☘️安徽频道", r"安徽|Anhui|合肥|Hefei"),
    "福建": ("☘️福建频道", r"福建|Fujian|福州|Fuzhou|厦门|Xiamen"),
    "江西": ("☘️江西频道", r"江西|Jiangxi|南昌|Nanchang"),
    "山东": ("☘️山东频道", r"山东|Shandong|济南|Jinan|青岛|Qingdao"),
    "河南": ("☘️河南频道", r"河南|Henan|郑州|Zhengzhou"),
    "湖北": ("☘️湖北频道", r"湖北|Hubei|武汉|Wuhan"),
    "湖南": ("☘️湖南频道", r"湖南|Hunan|长沙|Changsha"),
    "广东": ("☘️广东频道", r"广东|Guangdong|广州|Guangzhou|深圳|Shenzhen|东莞|Dongguan|佛山|Foshan|珠江|Zhujiang"),
    "广西": ("☘️广西频道", r"广西|Guangxi|南宁|Nanning"),
    "海南": ("☘️海南频道", r"海南|Hainan|海口|Haikou"),
    "四川": ("☘️四川频道", r"四川|Sichuan|成都|Chengdu"),
    "贵州": ("☘️贵州频道", r"贵州|Guizhou|贵阳|Guiyang"),
    "云南": ("☘️云南频道", r"云南|Yunnan|昆明|Kunming"),
    "西藏": ("☘️西藏频道", r"西藏|Xizang|Tibet|拉萨|Lhasa"),
    "陕西": ("☘️陕西频道", r"陕西|Shaanxi|西安|Xi.?an"),
    "甘肃": ("☘️甘肃频道", r"甘肃|Gansu|兰州|Lanzhou"),
    "青海": ("☘️青海频道", r"青海|Qinghai|西宁|Xining"),
    "宁夏": ("☘️宁夏频道", r"宁夏|Ningxia|银川|Yinchuan"),
    "新疆": ("☘️新疆频道", r"新疆|Xinjiang|乌鲁木齐|Urumqi"),
}
PROV_ORDER = [
    "广东", "浙江", "湖南", "上海", "湖北", "山东", "江苏", "黑龙江", "河北", "河南",
    "陕西", "海南", "北京", "天津", "山西", "内蒙古", "辽宁", "吉林", "安徽", "福建",
    "江西", "四川", "贵州", "云南", "广西", "甘肃", "青海", "宁夏", "新疆", "西藏", "重庆",
]
PROV_CAT = {k: PROV[k][0] for k in PROV}
PROV_PAT = {k: re.compile(PROV[k][1]) for k in PROV}

CAT_MAP = {
    "动画": "🪁动画少儿", "少儿": "🪁动画少儿", "卡通": "🪁动画少儿",
    "电影": "🎬电影频道", "影院": "🎬电影频道", "CHC": "🎬电影频道", "剧场": "🎬电影频道",
    "体育": "🏀体育频道", "足球": "🏀体育频道", "篮球": "🏀体育频道", "围棋": "🏀体育频道",
    "钓鱼": "🏀体育频道", "赛车": "🏀体育频道", "搏击": "🏀体育频道", "高尔夫": "🏀体育频道",
    "音乐": "🎵音乐频道", "歌声": "🎵音乐频道", "MV": "🎵音乐频道",
    "纪实": "🎞️纪实频道", "纪录": "🎞️纪实频道", "地理": "🎞️纪实频道", "人文": "🎞️纪实频道",
    "新闻": "📰新闻频道", "资讯": "📰新闻频道",
    "教育": "🏫教育频道", "课堂": "🏫教育频道",
    "游戏": "🎮游戏频道",
}
RADIO = re.compile(r"广播|电台|调频|之声|Radio|FM|CNR|CRI|交通台|音乐台|经济台")
HI_RES = re.compile(r"4K|超清|高清|HD", re.I)
GANGAO = re.compile(r"凤凰|TVB|翡翠|明珠|东森|中天|纬来|三立|香港|澳门|无线|J2|Viutv|VIUTV|星空|靖天|寰宇|Viu|HOY|RHK|台视|华视|民视|中视")
# 直播频道：虎牙/斗鱼/哔哩直播/网红直播等
LIVE = re.compile(r"虎牙|斗鱼|哔哩.*直播|网红|一直播|游戏直播|竞技直播|格斗直播", re.I)
# 国外台/外语台：纯非中文台名（含大量英文/日文/韩文，无中文字符）
FOREIGN_ONLY = re.compile(r"^[^一-鿿]{4,}$")

ORDER = [
    "📺央视频道", "💰央视付费频道", "📡卫视频道", "🌊港·澳·台",
] + [PROV_CAT[p] for p in PROV_ORDER] + [
    "🏀体育频道", "🎬电影频道", "🪁动画少儿", "🎵音乐频道", "🎞️纪实频道",
    "📰新闻频道", "🏫教育频道", "🎮游戏频道", "📻广播电台", "🔢高清4K频道", "🔢数字频道", "☘️地方频道",
]

JUNK = re.compile(
    r"《|》|「|」|[Dd][Jj]|车载|串烧|舞曲|神曲|情歌|老歌|伤感|歌曲|MV|解说|春晚"
    r"|第.?[一二三四五六七八九十百\d]{1,3}集|[\d]{1,3}集$"
    r"|^[0-9]+首|^20\d\d|^\d+年|^\d+首"
    r"|泰山|黄山|乌镇|张家界|丽江|峨眉|桂林|漓江|九华山|西递|宏村|鼓浪|崂山|鸣沙|月牙泉|张掖|七彩丹霞|水长城|飞来石|乐山大佛|玉龙雪山|普陀山|黄果树|武夷山|朱鹮|电视塔|南浦大桥|玄武湖|望乡台|天涯石|五彩池|雪山|瀑布|栈道|悬崖|景区|全景|鸟瞰|宝峰湖|玻璃栈道|醉美|沙滩|半山亭|天界山|观景|坐观|日出|云海|灯杆山|定海神针|马牙山|龙形田|西市河|赏樱阁|蓝月谷|崇圣寺|冰川|大水车|万古楼|蓝印花布"
    r"|甄嬛传|雪中悍刀行|拆弹专家|九品芝麻官|无间道|让子弹飞|人在囧途|卧虎藏龙|倩女幽魂|我不是药神|龙门飞甲|满城尽带黄金甲|变形金刚|寒战|死神来了|爱难求|爱一回|原谅你的谎|蜜雪冰城|闯天涯|英雄泪|红尘|朋友|拥抱你离去|武则天|三国演义|乡村爱情|七龙珠|CSI|大秦赋|乱世丽人|与凤行|乌龙闯情关|中华小当家|封神榜"
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


def clean_name(name):
    n = name
    n = re.sub(r"\(\d{3,4}[ip]?\)", "", n)
    n = re.sub(r"\[[^\]]*\]", "", n)
    n = re.sub(r"\s*HD\s*$", "", n)
    n = re.sub(r"\s+", " ", n).strip(" -")
    return n


def normalize_taihao(name):
    """台号归一化：去掉高清/4K/空格/连字符，统一字母大小写，
    CCTV-1 / CCTV1 / CCTV-1 综合 / CCTV-1高清 都归成 cctv1综合 一类的基名。"""
    n = name
    n = re.sub(r"高清|超清|4K|4k|HD", "", n)
    n = re.sub(r"[-\s]", "", n)
    n = n.lower()
    return n


def is_foreign(name):
    """是否国外台/外语台：台名没有中文字符（纯英文/日文/韩文/符号）。"""
    return bool(FOREIGN_ONLY.match(name)) and not re.search(r"[一-鿿]", name)


def is_live(name):
    return bool(LIVE.search(name))


def natural_key(name):
    return [int(g) if g.isdigit() else g.lower() for g in re.split(r"(\d+)", name)]


def get_cat(group, name):
    if RADIO.search(name):
        return "📻广播电台"
    if re.match(r"^CCTV|^CGTN|^CETV", name) or re.match(r"^CCTV|^CGTN|^CETV", group):
        if HI_RES.search(name):
            return "🔢高清4K频道"
        return "📺央视频道"
    if GANGAO.search(name):
        if HI_RES.search(name):
            return "🔢高清4K频道"
        return "🌊港·澳·台"
    if HI_RES.search(name):
        return "🔢高清4K频道"
    for p in PROV_ORDER:
        if PROV_PAT[p].search(name) or PROV_PAT[p].search(group):
            if "卫视" in name or "Satellite" in name:
                return "📡卫视频道"
            return PROV_CAT[p]
    for k, v in CAT_MAP.items():
        if k and re.search(k, name):
            return v
    return "☘️地方频道"


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
        name = clean_name(name)
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
    dropped_foreign = dropped_live = dropped_junk = 0
    for url in urls:
        for name, group in parse_source(url):
            total_inf += 1
            if re.search(NOISE_GROUPS, group):
                continue
            if is_junk(name):
                dropped_junk += 1
                continue
            if is_foreign(name):
                dropped_foreign += 1
                continue
            if is_live(name):
                dropped_live += 1
                continue
            bucket.setdefault(get_cat(group, name), set()).add(name)

    # 按归一化台号统计出现次数，只保留出现 >=2 的（过滤资源极少的冷门台）
    taihao_count = {}
    for cat, names in bucket.items():
        for n in names:
            th = normalize_taihao(n)
            taihao_count[th] = taihao_count.get(th, 0) + 1

    lines, count, dropped_cold = [], 0, 0
    for cat in ORDER:
        if cat in bucket and bucket[cat]:
            names = bucket[cat]
            keep = [n for n in names if taihao_count.get(normalize_taihao(n), 0) >= 2]
            dropped_cold += len(names) - len(keep)
            if keep:
                lines.append(f"{cat},#genre#")
                for n in sorted(keep, key=natural_key):
                    lines.append(n)
                    count += 1
    for cat in bucket:
        if cat not in ORDER and bucket[cat]:
            names = bucket[cat]
            keep = [n for n in names if taihao_count.get(normalize_taihao(n), 0) >= 2]
            if keep:
                lines.append(f"{cat},#genre#")
                for n in sorted(keep, key=natural_key):
                    lines.append(n)
                    count += 1

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"scanned urls={len(urls)} inf={total_inf} "
          f"drop_foreign={dropped_foreign} drop_live={dropped_live} drop_junk={dropped_junk} "
          f"drop_cold={dropped_cold} categories={len(bucket)} channels={count}")


if __name__ == "__main__":
    main()
