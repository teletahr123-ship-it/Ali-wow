# -*- coding: utf-8 -*-
import asyncio
import json
import os
import random
import re
import socket
import subprocess
import time

import aiohttp
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# ======================= الإعدادات =======================
BOT_TOKEN = "8980281589:AAEqY4nk6POnwVwNJ85tZ4GKhh8j7fGbUgw"
OWNER_ID = 6668195885
DATA_FILE = "data.json"

FETCH_TIMEOUT = 20          # مهلة كل مصدر بالثواني
MAX_CONCURRENT = 200        # عدد المصادر التي تُسحب بنفس اللحظة
CACHE_TTL = 60              # مدة بقاء النتيجة قبل إعادة السحب (ثانية)

DEFAULT_START = (
    "<b>◈ بوت استخراج البروكسيات ◈</b>\n\n"
    "▸ سحب متزامن من مئات المصادر\n"
    "▸ نتائج مكررة محذوفة تلقائيا\n"
    "▸ اختر من القائمة بالأسفل"
)

# ======================= المصادر =======================
_GH = "https://raw.githubusercontent.com/"
SOURCES = list(dict.fromkeys([
    # TheSpeedX
    _GH + "TheSpeedX/PROXY-List/master/http.txt",
    _GH + "TheSpeedX/PROXY-List/master/socks4.txt",
    _GH + "TheSpeedX/PROXY-List/master/socks5.txt",
    _GH + "TheSpeedX/SOCKS-List/master/http.txt",
    _GH + "TheSpeedX/SOCKS-List/master/socks4.txt",
    _GH + "TheSpeedX/SOCKS-List/master/socks5.txt",
    # monosans
    _GH + "monosans/proxy-list/main/proxies/all.txt",
    _GH + "monosans/proxy-list/main/proxies/http.txt",
    _GH + "monosans/proxy-list/main/proxies/socks4.txt",
    _GH + "monosans/proxy-list/main/proxies/socks5.txt",
    _GH + "monosans/proxy-list/main/proxies_anonymous/all.txt",
    _GH + "monosans/proxy-list/main/proxies_anonymous/http.txt",
    _GH + "monosans/proxy-list/main/proxies_anonymous/socks4.txt",
    _GH + "monosans/proxy-list/main/proxies_anonymous/socks5.txt",
    # clarketm / ShiftyTR
    _GH + "clarketm/proxy-list/master/proxy-list-raw.txt",
    _GH + "ShiftyTR/Proxy-List/master/proxy.txt",
    _GH + "ShiftyTR/Proxy-List/master/http.txt",
    _GH + "ShiftyTR/Proxy-List/master/https.txt",
    _GH + "ShiftyTR/Proxy-List/master/socks4.txt",
    _GH + "ShiftyTR/Proxy-List/master/socks5.txt",
    # jetkai
    _GH + "jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
    _GH + "jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    _GH + "jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    _GH + "jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
    _GH + "jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    # hookzof / roosterkid
    _GH + "hookzof/socks5_list/master/proxy.txt",
    _GH + "roosterkid/openproxylist/main/HTTPS_RAW.txt",
    _GH + "roosterkid/openproxylist/main/SOCKS4_RAW.txt",
    _GH + "roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    # MuRongPIG
    _GH + "MuRongPIG/Proxy-Master/main/http.txt",
    _GH + "MuRongPIG/Proxy-Master/main/socks4.txt",
    _GH + "MuRongPIG/Proxy-Master/main/socks5.txt",
    # proxifly
    _GH + "proxifly/free-proxy-list/main/proxies/all/data.txt",
    _GH + "proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    _GH + "proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",
    _GH + "proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    # KangProxy
    _GH + "officialputuid/KangProxy/KangProxy/http/http.txt",
    _GH + "officialputuid/KangProxy/KangProxy/https/https.txt",
    _GH + "officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
    _GH + "officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    _GH + "officialputuid/KangProxy/KangProxy/xResults/RAW.txt",
    # hideip.me
    _GH + "zloi-user/hideip.me/main/http.txt",
    _GH + "zloi-user/hideip.me/main/https.txt",
    _GH + "zloi-user/hideip.me/main/socks4.txt",
    _GH + "zloi-user/hideip.me/main/socks5.txt",
    # Zaeem20
    _GH + "Zaeem20/FREE_PROXIES_LIST/master/http.txt",
    _GH + "Zaeem20/FREE_PROXIES_LIST/master/https.txt",
    _GH + "Zaeem20/FREE_PROXIES_LIST/master/socks4.txt",
    _GH + "Zaeem20/FREE_PROXIES_LIST/master/socks5.txt",
    # vakhov
    _GH + "vakhov/fresh-proxy-list/master/http.txt",
    _GH + "vakhov/fresh-proxy-list/master/https.txt",
    _GH + "vakhov/fresh-proxy-list/master/socks4.txt",
    _GH + "vakhov/fresh-proxy-list/master/socks5.txt",
    # sunny9577 / mmpx12
    _GH + "sunny9577/proxy-scraper/master/proxies.txt",
    _GH + "mmpx12/proxy-list/master/http.txt",
    _GH + "mmpx12/proxy-list/master/https.txt",
    _GH + "mmpx12/proxy-list/master/socks4.txt",
    _GH + "mmpx12/proxy-list/master/socks5.txt",
    # rdavydov
    _GH + "rdavydov/proxy-list/main/proxies/http.txt",
    _GH + "rdavydov/proxy-list/main/proxies/socks4.txt",
    _GH + "rdavydov/proxy-list/main/proxies/socks5.txt",
    # ErcinDedeoglu
    _GH + "ErcinDedeoglu/proxies/main/proxies/http.txt",
    _GH + "ErcinDedeoglu/proxies/main/proxies/https.txt",
    _GH + "ErcinDedeoglu/proxies/main/proxies/socks4.txt",
    _GH + "ErcinDedeoglu/proxies/main/proxies/socks5.txt",
    # Anonym0usWork1221
    _GH + "Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
    _GH + "Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt",
    _GH + "Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt",
    _GH + "Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt",
    # prxchk
    _GH + "prxchk/proxy-list/main/all.txt",
    _GH + "prxchk/proxy-list/main/http.txt",
    _GH + "prxchk/proxy-list/main/socks4.txt",
    _GH + "prxchk/proxy-list/main/socks5.txt",
    # B4RC0DE-TM
    _GH + "B4RC0DE-TM/proxy-list/main/HTTP.txt",
    _GH + "B4RC0DE-TM/proxy-list/main/SOCKS4.txt",
    _GH + "B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
    # saschazesiger
    _GH + "saschazesiger/Free-Proxies/master/proxies/http.txt",
    _GH + "saschazesiger/Free-Proxies/master/proxies/socks4.txt",
    _GH + "saschazesiger/Free-Proxies/master/proxies/socks5.txt",
    # متفرقات
    _GH + "a2u/free-proxy-list/master/free-proxy-list.txt",
    _GH + "opsxcq/proxy-list/master/list.txt",
    _GH + "UptimerBot/proxy-list/main/proxies/http.txt",
    _GH + "UptimerBot/proxy-list/main/proxies/socks4.txt",
    _GH + "UptimerBot/proxy-list/main/proxies/socks5.txt",
    _GH + "ALIILAPRO/Proxy/main/http.txt",
    _GH + "ALIILAPRO/Proxy/main/socks4.txt",
    _GH + "ALIILAPRO/Proxy/main/socks5.txt",
    _GH + "ObcbO/getproxy/master/file/http.txt",
    _GH + "ObcbO/getproxy/master/file/https.txt",
    _GH + "ObcbO/getproxy/master/file/socks4.txt",
    _GH + "ObcbO/getproxy/master/file/socks5.txt",
    _GH + "Volodichev/proxy-list/main/http.txt",
    _GH + "yemixzy/proxy-list/main/proxy-list/data.txt",
    _GH + "themiralay/Proxy-List-World/master/data.txt",
    _GH + "casals-ar/proxy-list/main/http",
    _GH + "casals-ar/proxy-list/main/socks4",
    _GH + "casals-ar/proxy-list/main/socks5",
    _GH + "caliphdev/Proxy-List/master/http.txt",
    _GH + "proxy4parsing/proxy-list/main/http.txt",
    _GH + "manuGMG/proxy-365/main/ALL.txt",
    _GH + "r00tee/Proxy-List/main/Https.txt",
    _GH + "r00tee/Proxy-List/main/Socks4.txt",
    _GH + "r00tee/Proxy-List/main/Socks5.txt",
    _GH + "TuanMinPay/live-proxy/master/http.txt",
    _GH + "TuanMinPay/live-proxy/master/socks4.txt",
    _GH + "TuanMinPay/live-proxy/master/socks5.txt",
    _GH + "Tsprnay/Proxy-lists/master/proxies/http.txt",
    _GH + "Tsprnay/Proxy-lists/master/proxies/https.txt",
    _GH + "Tsprnay/Proxy-lists/master/proxies/socks4.txt",
    _GH + "Tsprnay/Proxy-lists/master/proxies/socks5.txt",
    _GH + "iplocate/free-proxy-list/main/all-proxies.txt",
    _GH + "iplocate/free-proxy-list/main/protocols/http.txt",
    _GH + "iplocate/free-proxy-list/main/protocols/socks4.txt",
    _GH + "iplocate/free-proxy-list/main/protocols/socks5.txt",
    _GH + "dpangestuw/Free-Proxy/main/All_proxies.txt",
    _GH + "dpangestuw/Free-Proxy/main/http_proxies.txt",
    _GH + "dpangestuw/Free-Proxy/main/socks4_proxies.txt",
    _GH + "dpangestuw/Free-Proxy/main/socks5_proxies.txt",
    _GH + "fyvri/fresh-proxy-list/archive/storage/classic/all.txt",
    _GH + "fyvri/fresh-proxy-list/archive/storage/classic/http.txt",
    _GH + "fyvri/fresh-proxy-list/archive/storage/classic/https.txt",
    _GH + "fyvri/fresh-proxy-list/archive/storage/classic/socks4.txt",
    _GH + "fyvri/fresh-proxy-list/archive/storage/classic/socks5.txt",
    _GH + "gfpcom/free-proxy-list/main/list/http.txt",
    _GH + "gfpcom/free-proxy-list/main/list/https.txt",
    _GH + "gfpcom/free-proxy-list/main/list/socks4.txt",
    _GH + "gfpcom/free-proxy-list/main/list/socks5.txt",
    _GH + "Vann-Dev/proxy-list/main/proxies/http.txt",
    _GH + "Vann-Dev/proxy-list/main/proxies/https.txt",
    _GH + "Firmfox/Proxify/main/proxies/http.txt",
    _GH + "Firmfox/Proxify/main/proxies/socks4.txt",
    _GH + "Firmfox/Proxify/main/proxies/socks5.txt",
    _GH + "claude89757/free_https_proxies/main/https_proxies.txt",
    _GH + "javadbazokar/PROXY-List/main/http.txt",
    _GH + "javadbazokar/PROXY-List/main/socks4.txt",
    _GH + "javadbazokar/PROXY-List/main/socks5.txt",
    _GH + "andigwandi/free-proxy/main/proxy_list.txt",
    _GH + "BreakingTechFr/Proxy_Free/main/proxies/http.txt",
    _GH + "BreakingTechFr/Proxy_Free/main/proxies/socks4.txt",
    _GH + "BreakingTechFr/Proxy_Free/main/proxies/socks5.txt",
    _GH + "hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
    _GH + "MrMarble/proxy-list/main/all.txt",
    _GH + "ProxyScraper/ProxyScraper/main/http.txt",
    _GH + "ProxyScraper/ProxyScraper/main/socks4.txt",
    _GH + "ProxyScraper/ProxyScraper/main/socks5.txt",
    _GH + "proxylist-to/proxy-list/main/http.txt",
    _GH + "zevtyardt/proxy-list/main/http.txt",
    _GH + "zevtyardt/proxy-list/main/socks4.txt",
    _GH + "zevtyardt/proxy-list/main/socks5.txt",
    _GH + "RX4096/proxy-list/main/online/all.txt",
    _GH + "RX4096/proxy-list/main/online/http.txt",
    _GH + "RX4096/proxy-list/main/online/socks4.txt",
    _GH + "RX4096/proxy-list/main/online/socks5.txt",
    _GH + "hanwayTech/free-proxy-list/main/http.txt",
    _GH + "hanwayTech/free-proxy-list/main/https.txt",
    _GH + "hanwayTech/free-proxy-list/main/socks4.txt",
    _GH + "hanwayTech/free-proxy-list/main/socks5.txt",
    _GH + "ClearProxy/checked-proxy-list/main/http/raw/all.txt",
    _GH + "ClearProxy/checked-proxy-list/main/socks4/raw/all.txt",
    _GH + "ClearProxy/checked-proxy-list/main/socks5/raw/all.txt",
    _GH + "berkay-digital/Proxy-Scraper/main/proxies.txt",
    _GH + "im-razvan/proxy_list/main/http.txt",
    _GH + "im-razvan/proxy_list/main/socks5.txt",
    _GH + "SevenworksDev/proxy-list/main/proxies/http.txt",
    _GH + "SevenworksDev/proxy-list/main/proxies/socks4.txt",
    _GH + "SevenworksDev/proxy-list/main/proxies/socks5.txt",
    # واجهات ومواقع
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=ipport&format=text",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://api.openproxylist.xyz/http.txt",
    "https://api.openproxylist.xyz/socks4.txt",
    "https://api.openproxylist.xyz/socks5.txt",
    "https://www.proxyscan.io/download?type=http",
    "https://www.proxyscan.io/download?type=socks4",
    "https://www.proxyscan.io/download?type=socks5",
    "https://spys.me/proxy.txt",
    "https://spys.me/socks.txt",
    "https://free-proxy-list.net/",
    "https://www.us-proxy.org/",
    "https://www.sslproxies.org/",
    "https://www.socks-proxy.net/",
    "https://free-proxy-list.net/uk-proxy.html",
    "https://proxyspace.pro/http.txt",
    "https://proxyspace.pro/https.txt",
    "https://proxyspace.pro/socks4.txt",
    "https://proxyspace.pro/socks5.txt",
    "https://multiproxy.org/txt_all/proxy.txt",
    "https://rootjazz.com/proxies/proxies.txt",
    "https://openproxy.space/list/http",
    "https://openproxy.space/list/socks4",
    "https://openproxy.space/list/socks5",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=4&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=5&sort_by=lastChecked&sort_type=desc",
]))

# ======================= الاستخراج =======================
PROXY_RE = re.compile(r"(?<![\d.])((?:\d{1,3}\.){3}\d{1,3}):(\d{2,5})(?!\d)")
JSON_RE = re.compile(
    r'"ip"\s*:\s*"((?:\d{1,3}\.){3}\d{1,3})"[^{}]{0,400}?"port"\s*:\s*"?(\d{2,5})"?'
)


def _add(found: set, ip: str, port: str):
    try:
        if all(int(x) <= 255 for x in ip.split(".")) and 1 <= int(port) <= 65535:
            found.add(f"{ip}:{port}")
    except ValueError:
        pass


def parse(text: str) -> set:
    found: set = set()
    for ip, port in PROXY_RE.findall(text):
        _add(found, ip, port)
    for ip, port in JSON_RE.findall(text):
        _add(found, ip, port)
    return found


async def fetch_one(session: aiohttp.ClientSession, sem: asyncio.Semaphore, url: str) -> set:
    async with sem:
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT)
            ) as r:
                if r.status != 200:
                    return set()
                text = await r.text(errors="ignore")
        except Exception:
            return set()
    return parse(text)


# ======================= دالة الإرسال عبر Raw TCP Socket =======================
async def send_proxies_to_target(proxies_list: list, target_ip: str, target_port: int):
    """إرسال البروكسيات دفعة واحدة مباشرة عبر Socket لإحداث ضغط وحمل حقيقي على السيرفر المستهدف"""
    def _send_sync():
        try:
            data_to_send = "\n".join(proxies_list).encode("utf-8") + b"\n"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((target_ip, target_port))
                s.sendall(data_to_send)
            print(f"[✓] تم إرسال {len(proxies_list)} بروكسي عبر TCP Socket إلى {target_ip}:{target_port}")
        except Exception as e:
            print(f"[×] خطأ أثناء إرسال البروكسيات عبر Socket: {e}")

    # تشغيل الاتصال المباشر في الخلفية حتى لا يتجمد البوت
    await asyncio.to_thread(_send_sync)


STATS = {"sources": len(SOURCES), "ok": 0, "failed": 0, "total": 0, "seconds": 0.0, "time": None}
_cache = {"ts": 0.0, "data": []}
_lock = asyncio.Lock()


async def get_proxies() -> list:
    async with _lock:
        if _cache["data"] and time.time() - _cache["ts"] < CACHE_TTL:
            return _cache["data"]
        t0 = time.time()
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        conn = aiohttp.TCPConnector(limit=0, ssl=False, ttl_dns_cache=300)
        async with aiohttp.ClientSession(
            connector=conn, headers={"User-Agent": "Mozilla/5.0"}
        ) as session:
            results = await asyncio.gather(*(fetch_one(session, sem, u) for u in SOURCES))
        allp: set = set()
        ok = 0
        for r in results:
            if r:
                ok += 1
                allp |= r
        data = list(allp)
        random.shuffle(data)
        _cache["ts"] = time.time()
        _cache["data"] = data
        STATS.update(
            ok=ok,
            failed=len(SOURCES) - ok,
            total=len(data),
            seconds=round(time.time() - t0, 1),
            time=time.strftime("%H:%M:%S"),
        )
        return data


# ======================= التخزين =======================
def load_start() -> str:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("start") or DEFAULT_START
    except Exception:
        return DEFAULT_START


def save_start(text: str):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"start": text}, f, ensure_ascii=False)


def persist_to_git():
    """يحفظ التغيير داخل المستودع حتى لا يضيع عند إعادة تشغيل الـ job."""
    if not os.getenv("GITHUB_ACTIONS"):
        return
    try:
        run = lambda *a: subprocess.run(a, check=True, capture_output=True)
        run("git", "config", "user.name", "proxy-bot")
        run("git", "config", "user.email", "proxy-bot@users.noreply.github.com")
        run("git", "add", DATA_FILE)
        run("git", "commit", "-m", "update start message")
        subprocess.run(["git", "pull", "--rebase"], capture_output=True)
        run("git", "push")
    except Exception:
        pass


# ======================= البوت =======================
router = Router()
WAIT_START: set = set()
WAIT_TARGET: set = set()  # لتتبع المستخدمين الذين يكتبون الآيبي والبورت


def menu_kb(uid: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="◈ استخراج بروكسيات", callback_data="ext")],
        [InlineKeyboardButton(text="◈ حالة المصادر", callback_data="stat")],
    ]
    if uid == OWNER_ID:
        rows.append([InlineKeyboardButton(text="◈ تغيير كليشة ستارت", callback_data="chg")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def safe_edit(msg: Message, text: str, kb=None):
    try:
        await msg.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        pass


@router.message(CommandStart())
async def cmd_start(m: Message):
    WAIT_START.discard(m.from_user.id)
    WAIT_TARGET.discard(m.from_user.id)
    await m.answer(load_start(), reply_markup=menu_kb(m.from_user.id))


@router.callback_query(F.data == "menu")
async def cb_menu(c: CallbackQuery):
    WAIT_START.discard(c.from_user.id)
    WAIT_TARGET.discard(c.from_user.id)
    await c.answer()
    await safe_edit(c.message, load_start(), menu_kb(c.from_user.id))


@router.callback_query(F.data == "ext")
async def cb_extract(c: CallbackQuery):
    WAIT_TARGET.add(c.from_user.id)
    await c.answer()
    await safe_edit(
        c.message,
        "<b>◈ أدخل الآيبي والبورت</b>\n\n"
        "▸ أرسل الآن الآيبي والبورت مفصولين بمسافة (مثال):\n"
        "<code>91.108.9.211 32000</code>\n\n"
        "▸ أو اكتب <b>إقاف</b> للرجوع للقائمة.",
        InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="◂ إلغاء", callback_data="menu")]]
        ),
    )


@router.message(F.text)
async def handle_user_text(m: Message):
    uid = m.from_user.id
    text = m.text.strip()

    # إذا كتب "إيقاف" أو "إلغاء"
    if text in ["إيقاف", "الغاء", "إلغاء"]:
        WAIT_START.discard(uid)
        WAIT_TARGET.discard(uid)
        await m.answer(
            "<b>◈ تم الإلغاء بنجاح.</b>",
            reply_markup=menu_kb(uid),
        )
        return

    # إذا كان بانتظار إدخال الآيبي والبورت
    if uid in WAIT_TARGET:
        WAIT_TARGET.discard(uid)
        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            await m.answer(
                "<b>[×] الصيغة غير صحيحة!</b> يرجى إرسال الآيبي والبورت بهذا الشكل حصراً:\n<code>91.108.9.211 32000</code>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="◂ القائمة", callback_data="menu")]]
                ),
            )
            return

        target_ip, target_port = parts[0], int(parts[1])
        processing_msg = await m.answer("<b>◈ جاري السحب من المصادر وإرسالها...</b>")

        proxies = await get_proxies()
        if not proxies:
            await processing_msg.edit_text(
                "<b>◈ لم يتم العثور على بروكسيات حاليا</b>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="◂ القائمة", callback_data="menu")]]
                ),
            )
            return

        # إرسال جميع البروكسيات دفعة واحدة عبر اتصال Socket المباشر
        await send_proxies_to_target(proxies, target_ip, target_port)

        await processing_msg.edit_text(
            f"<b>[✓] تم سحب وإرسال جميع البروكسيات بنجاح!</b>\n\n"
            f"❖ الإجمالي المرسل: <b>{len(proxies)}</b> بروكسي\n"
            f"❖ إلى الوجهة: <code>{target_ip}:{target_port}</code>",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="◂ القائمة", callback_data="menu")]]
            ),
        )
        return

    # إذا كان بانتظار تغيير كليشة ستارت (للمالك)
    if uid == OWNER_ID and uid in WAIT_START:
        WAIT_START.discard(uid)
        save_start(m.html_text)
        await asyncio.to_thread(persist_to_git)
        await m.answer(
            "<b>◈ تم حفظ الكليشة الجديدة</b>",
            reply_markup=menu_kb(uid),
        )
        return


@router.callback_query(F.data == "stat")
async def cb_stat(c: CallbackQuery):
    await c.answer()
    s = STATS
    text = (
        "<b>◈ حالة المصادر</b>\n\n"
        f"❖ عدد المصادر: {s['sources']}\n"
        f"❖ المصادر العاملة: {s['ok']}\n"
        f"❖ المصادر المتوقفة: {s['failed']}\n"
        f"❖ آخر عدد بروكسيات: {s['total']}\n"
        f"❖ مدة آخر سحب: {s['seconds']} ثانية\n"
        f"❖ وقت آخر سحب: {s['time'] or 'لم يتم بعد'}"
    )
    await safe_edit(
        c.message,
        text,
        InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="◂ القائمة", callback_data="menu")]]
        ),
    )


@router.callback_query(F.data == "chg")
async def cb_change(c: CallbackQuery):
    if c.from_user.id != OWNER_ID:
        await c.answer("للمالك فقط", show_alert=True)
        return
    WAIT_START.add(c.from_user.id)
    await c.answer()
    await safe_edit(
        c.message,
        "<b>◈ تغيير كليشة ستارت</b>\n\n"
        "▸ أرسل الآن الكليشة الجديدة\n"
        "▸ يدعم التنسيق (غامق، مائل، روابط)",
        InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="◂ إلغاء", callback_data="menu")]]
        ),
    )


async def main():
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
