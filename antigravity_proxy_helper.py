# -*- coding: utf-8 -*-
import ctypes
import json
import os
import random
import re
import shutil
import socket
import string
import subprocess
import sys
import time
import winreg
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext, ttk
except ImportError:
    tk = None

APP_NAME = "AntigravityProxyHelper"
CONFIG_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

ENV_KEYS = ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY")
DEFAULT_NO_PROXY = ["localhost", "127.0.0.1", "::1"]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = "7897"

GROUP_NAME = "🤖 Antigravity"
COPY_SUFFIX = " (Antigravity)"
VERGE_GLOB = "io.github.clash-verge-rev.clash-verge-rev*"

ANTIGRAVITY_PROCESSES = [
    "Antigravity.exe",
    "Antigravity IDE.exe",
    "language_server.exe",
    "language_server_windows_x64.exe",
]

EXCLUDED_REGION = re.compile(
    r"香港|🇭🇰|\bHK\b|\bHKG\b|Hong\s?Kong|"
    r"中国|回国|大陆|🇨🇳|\bCN\b|\bCHN\b|China|"
    r"俄罗斯|俄国|🇷🇺|\bRU\b|\bRUS\b|Russia|"
    r"伊朗|🇮🇷|Iran|古巴|🇨🇺|Cuba|"
    r"朝鲜|🇰🇵|North\s?Korea|叙利亚|🇸🇾|Syria|"
    r"白俄罗斯|Belarus|阿富汗|🇦🇫|Afghanistan",
    re.I,
)

EXCLUDED_INFO = re.compile(
    r"剩余|到期|流量|重置|官网|订阅|客服|群组|购买|Expire|Traffic|Website|Subscribe|Renew",
    re.I,
)

MULTI_SUFFIXES = {
    "com.cn", "net.cn", "org.cn", "gov.cn", "edu.cn",
    "com.hk", "com.tw", "co.jp", "co.uk", "com.au", "com.sg",
}

STRINGS = {
    "app_title": {"zh": "🤖 Antigravity 代理助手", "en": "🤖 Antigravity Proxy Helper"},
    "frame_proxy": {"zh": "🌐 代理地址（Clash 混合端口）", "en": "🌐 Proxy address (Clash mixed port)"},
    "addr": {"zh": "地址:", "en": "Address:"},
    "port": {"zh": "端口:", "en": "Port:"},
    "test_conn": {"zh": "🔌 检测连通性", "en": "🔌 Test connection"},
    "port_ok": {"zh": "✅ 可连接", "en": "✅ Reachable"},
    "port_bad": {"zh": "⚠️ 未连通", "en": "⚠️ Unreachable"},
    "apply_btn": {"zh": "🚀 立即应用代理", "en": "🚀 Apply proxy now"},
    "restore_btn": {"zh": "🧹 还原代理设置", "en": "🧹 Restore proxy settings"},
    "onetime_btn": {"zh": "🎯 一次性配置（以后无需再运行）", "en": "🎯 One-time setup (run once, then forget)"},
    "frame_init": {
        "zh": "⚙️ Clash Verge 一键初始化（只需第一次运行；之后更新订阅可再点一次）",
        "en": "⚙️ Clash Verge setup (first run only; click again after subscription updates)",
    },
    "init_btn": {"zh": "🛠️ 初始化 Clash 配置", "en": "🛠️ Setup Clash profile"},
    "init_hint": {
        "zh": "只需配置一次，之后不用重复；Clash 运行中也可初始化",
        "en": "Configure once, no need to repeat; works while Clash is running",
    },
    "frame_launch": {
        "zh": "▶️ 启动应用（自动带上本次代理环境变量）",
        "en": "▶️ Launch apps (with proxy environment applied)",
    },
    "launch_ag": {"zh": "启动 Antigravity", "en": "Launch Antigravity"},
    "launch_ide": {"zh": "启动 Antigravity IDE", "en": "Launch Antigravity IDE"},
    "keep_env": {
        "zh": "关闭程序时还原代理设置（环境变量 + Antigravity 的 http.proxy）；取消勾选则永久保持",
        "en": "Restore proxy settings on exit (env vars + Antigravity http.proxy); uncheck to keep permanently",
    },
    "lang_label": {"zh": "语言 / Language:", "en": "Language / 语言:"},
    "addr_empty": {"zh": "代理地址不能为空", "en": "Proxy address cannot be empty"},
    "port_invalid": {"zh": "端口必须是 1-65535 的数字", "en": "Port must be a number between 1 and 65535"},
    "log_started": {"zh": "🤖 {} 已启动", "en": "🤖 {} started"},
    "log_pyyaml_missing": {
        "zh": "❌ 未安装 PyYAML，初始化功能不可用，请执行: pip install pyyaml",
        "en": "❌ PyYAML is missing, setup disabled. Run: pip install pyyaml",
    },
    "log_settings_found": {"zh": "🔎 检测到 {} 个 Antigravity 设置文件", "en": "🔎 Found {} Antigravity settings file(s)"},
    "log_verge_dir": {"zh": "🔎 Clash Verge 目录: {}", "en": "🔎 Clash Verge directory: {}"},
    "log_verge_none": {"zh": "未找到", "en": "not found"},
    "log_clash_ok": {"zh": "🔌 Clash 端口 {}:{} 可连接", "en": "🔌 Clash port {}:{} reachable"},
    "log_clash_bad": {
        "zh": "⚠️ 端口 {}:{} 无法连接，请确认 Clash Verge 已启动且端口正确",
        "en": "⚠️ Port {}:{} unreachable, make sure Clash Verge is running and the port is correct",
    },
    "log_env_set": {"zh": "🌐 已设置环境变量 HTTP_PROXY / HTTPS_PROXY = {}", "en": "🌐 Environment set: HTTP_PROXY / HTTPS_PROXY = {}"},
    "log_settings_written": {"zh": "📝 已写入 Antigravity 设置 http.proxy（{} 个文件）", "en": "📝 Wrote Antigravity http.proxy settings ({} file(s))"},
    "log_settings_missing": {
        "zh": "⚠️ 未找到 Antigravity 的 settings.json，可先启动一次 Antigravity",
        "en": "⚠️ No Antigravity settings.json found; start Antigravity once first",
    },
    "log_restart_app": {
        "zh": "💡 已运行的 Antigravity 需要重启才能读取新环境变量",
        "en": "💡 Running Antigravity must be restarted to pick up the new environment",
    },
    "log_restore_done": {"zh": "🧹 环境变量已还原为设置前的值", "en": "🧹 Environment variables restored"},
    "log_settings_removed": {"zh": "🧹 已移除 Antigravity 的 http.proxy 设置（{} 个文件）", "en": "🧹 Removed Antigravity http.proxy settings ({} file(s))"},
    "dlg_onetime_ask": {
        "zh": "将一次性永久完成以下配置（关闭本程序后依然生效）：\n① 设置代理环境变量 ② 写入 Antigravity 配置 ③ 初始化 Clash 配置\n\n确定继续吗？",
        "en": "This will permanently apply: (1) proxy env vars (2) Antigravity settings (3) Clash profile setup.\nIt stays effective after closing this app.\n\nContinue?",
    },
    "log_onetime_done": {
        "zh": "✅ 一次性配置完成！以后无需再运行本工具；如需撤销请点「还原代理设置」",
        "en": "✅ One-time setup complete! No need to run this tool again; use \"Restore proxy settings\" to undo.",
    },
    "log_onetime_cancelled": {"zh": "⏹️ 已取消一次性配置", "en": "⏹️ One-time setup cancelled"},
    "log_init_start": {"zh": "⚙️ 开始初始化: {}", "en": "⚙️ Setup started: {}"},
    "log_no_verge": {"zh": "❌ 未找到 Clash Verge 配置目录", "en": "❌ Clash Verge config directory not found"},
    "log_no_profile": {"zh": "❌ 未找到当前启用的订阅配置", "en": "❌ Current profile not found"},
    "log_no_file": {"zh": "❌ 订阅文件不存在: {}", "en": "❌ Profile file missing: {}"},
    "log_nodes": {"zh": "🔎 订阅节点 {} 个，可用地区节点 {} 个（已排除香港/中国/俄罗斯等）", "en": "🔎 {} nodes found, {} usable-region nodes (HK/CN/RU etc. excluded)"},
    "log_inject_fail": {"zh": "❌ 配置文件缺少 proxy-groups 或 rules 段，无法注入", "en": "❌ profile has no proxy-groups or rules section"},
    "log_new_profile": {"zh": "📄 已创建配置副本: {} → {}", "en": "📄 Created profile copy: {} -> {}"},
    "log_reuse_profile": {"zh": "♻️ 已更新已有配置副本: {}", "en": "♻️ Updated existing profile copy: {}"},
    "log_rules_added": {"zh": "✅ 已注入 {} 条前置规则（含 hosts 直连、Antigravity 进程/域名规则）", "en": "✅ Injected {} rules (hosts DIRECT + Antigravity process/domain)"},
    "log_group_added": {"zh": "✅ 已注入代理组 {}（{} 个节点 + DIRECT）", "en": "✅ Injected group {} ({} nodes + DIRECT)"},
    "log_switched": {"zh": "🔀 已把 Clash 当前配置切换为副本，重启 Clash Verge 生效", "en": "🔀 Switched Clash current profile to the copy; restart Clash Verge"},
    "log_backup": {"zh": "🗄️ 已备份 profiles.yaml", "en": "🗄️ profiles.yaml backed up"},
    "log_verify_ok": {"zh": "🔍 已校验配置清单，当前配置: {}", "en": "🔍 Profile list verified, current profile: {}"},
    "log_verify_fail": {"zh": "❌ 配置清单写入校验失败，可能被其他程序覆盖，请重试", "en": "❌ Profile list verification failed (may have been overwritten), please retry"},
    "dlg_restart_ask": {
        "zh": "Clash Verge 正在运行。\n初始化需要先临时关闭它（否则配置清单会被覆盖），完成后程序会自动重新打开它。\n\n是否继续？",
        "en": "Clash Verge is running.\nSetup needs to close it temporarily (otherwise the profile list would be overwritten) and will reopen it automatically afterwards.\n\nContinue?",
    },
    "log_init_cancelled": {"zh": "⏹️ 已取消初始化（Clash Verge 仍在运行）", "en": "⏹️ Setup cancelled (Clash Verge still running)"},
    "log_verge_stopping": {"zh": "🔄 正在关闭 Clash Verge 以便安全写入配置...", "en": "🔄 Closing Clash Verge to write the profile safely..."},
    "log_verge_relaunched": {"zh": "🚀 已自动重新打开 Clash Verge: {}", "en": "🚀 Clash Verge relaunched: {}"},
    "log_verge_exe_missing": {
        "zh": "⚠️ 未找到 Clash Verge 程序路径，请手动打开它",
        "en": "⚠️ Clash Verge executable not found, please open it manually",
    },
    "log_init_done": {"zh": "🎉 初始化完成", "en": "🎉 Setup complete"},
    "dlg_done_title": {"zh": "初始化完成", "en": "Setup complete"},
    "dlg_done_msg": {
        "zh": "已创建配置副本并切换为当前配置。\n请重启 Clash Verge 使其生效。",
        "en": "A profile copy was created and set as current.\nPlease restart Clash Verge to apply it.",
    },
    "dlg_err_title": {"zh": "初始化失败", "en": "Setup failed"},
    "dlg_fail_msg": {"zh": "初始化失败，请查看日志窗口中的原因", "en": "Setup failed, see the log window for details"},
    "log_launch_missing": {"zh": "⚠️ 未找到 {}，请手动启动", "en": "⚠️ {} not found, start it manually"},
    "log_launch_ok": {"zh": "▶️ 已启动 {}（带代理环境变量）", "en": "▶️ Launched {} (with proxy environment)"},
    "log_launch_fail": {"zh": "❌ 启动失败: {}", "en": "❌ Launch failed: {}"},
    "log_lang_changed": {"zh": "🌍 界面语言: 中文", "en": "🌍 UI language: English"},
}


def tr(lang, key, *args):
    entry = STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("zh") or key
    return text.format(*args) if args else text


def default_lang():
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "zh" if (lang_id & 0x3FF) == 0x04 else "en"
    except Exception:
        return "en"


def resource_path(name):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / name
    return Path(__file__).resolve().parent / name


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def apply_window_icon(root):
    icon = resource_path("icon.ico")
    try:
        if icon.exists():
            root.iconbitmap(default=str(icon))
    except Exception:
        pass
    try:
        png = resource_path("icon.png")
        if png.exists():
            photo = tk.PhotoImage(file=str(png))
            root.iconphoto(True, photo)
            root._icon_photo = photo
    except Exception:
        pass


def load_config():
    cfg = {
        "proxy_host": DEFAULT_HOST,
        "proxy_port": DEFAULT_PORT,
        "restore_env_on_exit": True,
        "env_applied": False,
        "env_snapshot": {},
        "lang": default_lang(),
    }
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update(data)
    except Exception:
        pass
    return cfg


def save_config(cfg):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def read_user_env(name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
    except OSError:
        return None


def write_user_env(name, value):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
        if value is None:
            try:
                winreg.DeleteValue(key, name)
            except FileNotFoundError:
                pass
        else:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))


def broadcast_env_change():
    try:
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, ctypes.c_wchar_p("Environment"), 0x0002, 3000, ctypes.byref(ctypes.c_ulong())
        )
    except Exception:
        pass


def proxy_url(host, port):
    return "http://{}:{}".format(host, port)


def apply_env(host, port, cfg):
    if not cfg.get("env_applied"):
        cfg["env_snapshot"] = {k: read_user_env(k) for k in ENV_KEYS}
        cfg["env_applied"] = True
    url = proxy_url(host, port)
    write_user_env("HTTP_PROXY", url)
    write_user_env("HTTPS_PROXY", url)
    existing = read_user_env("NO_PROXY") or ""
    parts = [p.strip() for p in existing.split(",") if p.strip()]
    for item in DEFAULT_NO_PROXY:
        if item not in parts:
            parts.append(item)
    write_user_env("NO_PROXY", ",".join(parts))
    os.environ["HTTP_PROXY"] = url
    os.environ["HTTPS_PROXY"] = url
    os.environ["NO_PROXY"] = ",".join(parts)
    broadcast_env_change()
    save_config(cfg)


def restore_env(cfg):
    if not cfg.get("env_applied"):
        return
    snapshot = cfg.get("env_snapshot") or {}
    for key in ENV_KEYS:
        write_user_env(key, snapshot.get(key))
    cfg["env_applied"] = False
    save_config(cfg)
    for key in ENV_KEYS:
        os.environ.pop(key, None)
    broadcast_env_change()


def port_open(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.6)
            return s.connect_ex((host, int(port))) == 0
    except Exception:
        return False


def find_antigravity_settings():
    appdata = Path(os.environ.get("APPDATA", ""))
    found = []
    if not appdata.exists():
        return found
    for d in appdata.iterdir():
        if not d.is_dir():
            continue
        low = d.name.lower()
        if "antigravity" not in low or low == APP_NAME.lower():
            continue
        user_dir = d / "User"
        settings = user_dir / "settings.json"
        if settings.exists():
            found.append(settings)
        elif user_dir.exists():
            found.append(settings)
    return found


def upsert_settings_file(path, updates):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("{}\n", encoding="utf-8")
    backup = path.with_suffix(".json.bak")
    if not backup.exists():
        try:
            shutil.copy2(path, backup)
        except Exception:
            pass
    text = path.read_text(encoding="utf-8-sig")
    data = None
    try:
        data = json.loads(text)
    except Exception:
        stripped = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        stripped = re.sub(r"(?m)^\s*//.*$", "", stripped)
        try:
            data = json.loads(stripped)
        except Exception:
            data = None
    if isinstance(data, dict):
        data.update(updates)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        return True
    new_text = text
    for key, value in updates.items():
        pattern = re.compile(r'("%s"\s*:\s*)("[^"]*"|\S+)' % re.escape(key))
        if pattern.search(new_text):
            new_text = pattern.sub(lambda m: m.group(1) + json.dumps(value, ensure_ascii=False), new_text, count=1)
        else:
            idx = new_text.rfind("}")
            if idx == -1:
                new_text = "{\n    %s: %s\n}\n" % (json.dumps(key), json.dumps(value, ensure_ascii=False))
            else:
                inner = new_text[:idx].rstrip()
                sep = ",\n    " if inner and not inner.endswith("{") else "\n    "
                new_text = inner + sep + '%s: %s\n' % (json.dumps(key), json.dumps(value, ensure_ascii=False)) + new_text[idx:]
    path.write_text(new_text, encoding="utf-8")
    return True


def write_antigravity_proxy(settings_paths, host, port):
    updates = {"http.proxy": proxy_url(host, port), "http.proxySupport": "on"}
    count = 0
    for path in settings_paths:
        try:
            upsert_settings_file(path, updates)
            count += 1
        except Exception:
            pass
    return count


def remove_antigravity_proxy(settings_paths, host, port):
    url = proxy_url(host, port)
    count = 0
    for path in settings_paths:
        try:
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict) or data.get("http.proxy") != url:
                continue
            data.pop("http.proxy", None)
            data.pop("http.proxySupport", None)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
            count += 1
        except Exception:
            pass
    return count


def base_domain(host):
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in MULTI_SUFFIXES:
        return ".".join(parts[-3:])
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def hosts_direct_rules():
    hosts_path = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "drivers" / "etc" / "hosts"
    domains = set()
    try:
        lines = hosts_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.replace("\t", " ").split()
        if len(parts) >= 2 and parts[0] in ("127.0.0.1", "::1", "0.0.0.0"):
            for h in parts[1:]:
                h = h.strip().lower()
                if h and h != "localhost" and "." in h:
                    domains.add(base_domain(h))
    return ["DOMAIN-SUFFIX,{},DIRECT".format(d) for d in sorted(domains)]


def antigravity_rule_strings():
    rules = ["PROCESS-NAME,{},{}".format(p, GROUP_NAME) for p in ANTIGRAVITY_PROCESSES]
    rules += [
        "DOMAIN-KEYWORD,antigravity,{}".format(GROUP_NAME),
        "DOMAIN-SUFFIX,antigravity.google,{}".format(GROUP_NAME),
        "DOMAIN-SUFFIX,run.app,{}".format(GROUP_NAME),
        "DOMAIN-SUFFIX,deepmind.google,{}".format(GROUP_NAME),
        "DOMAIN-SUFFIX,deepmind.com,{}".format(GROUP_NAME),
        "DOMAIN-KEYWORD,cloudcode-pa,{}".format(GROUP_NAME),
        "DOMAIN-SUFFIX,generativelanguage.googleapis.com,{}".format(GROUP_NAME),
        "DOMAIN-SUFFIX,google.dev,{}".format(GROUP_NAME),
        "DOMAIN-SUFFIX,aistudio.google.com,{}".format(GROUP_NAME),
    ]
    return rules


def generate_uid():
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(12))


def yaml_load(path):
    if yaml is None:
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8", errors="ignore"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def find_verge_dir():
    appdata = Path(os.environ.get("APPDATA", ""))
    for d in sorted(appdata.glob(VERGE_GLOB)):
        if (d / "profiles.yaml").exists():
            return d
    return None


def process_running(image):
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq {}".format(image), "/NH"],
            capture_output=True, text=True, errors="ignore", timeout=15,
        ).stdout.lower()
        return image.lower() in out
    except Exception:
        return False


def verge_running():
    return process_running("clash-verge.exe") or process_running("verge-mihomo.exe")


def stop_verge():
    for image in ("clash-verge.exe", "verge-mihomo.exe"):
        try:
            subprocess.run(["taskkill", "/IM", image, "/F"], capture_output=True, timeout=20)
        except Exception:
            pass


def find_verge_exe():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "$p = Get-Process -Name 'clash-verge' -ErrorAction SilentlyContinue | Select-Object -First 1; if ($p) { $p.Path }"],
            capture_output=True, text=True, errors="ignore", timeout=20,
        ).stdout.strip()
        if out and Path(out).exists():
            return Path(out)
    except Exception:
        pass
    candidates = [
        Path(r"C:\Program Files\Clash Verge\clash-verge.exe"),
        Path(r"C:\Program Files (x86)\Clash Verge\clash-verge.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Clash Verge" / "clash-verge.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Clash Verge" / "clash-verge.exe",
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    return None


def launch_verge(exe):
    try:
        subprocess.Popen([str(exe)], cwd=str(exe.parent))
        return True
    except Exception:
        return False


def extract_proxies_and_groups(profile_path):
    nodes, groups = [], []
    data = yaml_load(profile_path)
    for p in data.get("proxies") or []:
        if isinstance(p, dict) and p.get("name"):
            name = str(p["name"])
            if name not in nodes:
                nodes.append(name)
    for g in data.get("proxy-groups") or []:
        if isinstance(g, dict) and g.get("name"):
            name = str(g["name"])
            if name not in groups:
                groups.append(name)
    if nodes:
        return nodes, groups
    try:
        text = profile_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, groups
    for m in re.finditer(r"-\s*\{name:\s*([^,}]+),", text):
        name = m.group(1).strip().strip('"\'')
        if name and name not in nodes:
            nodes.append(name)
    for m in re.finditer(r"^\s*-\s*name:\s*(.+?)\s*$", text, re.M):
        name = m.group(1).strip().strip('"\'')
        if name and name not in groups:
            groups.append(name)
    return nodes, groups


def allowed_nodes(nodes):
    return [n for n in nodes if not EXCLUDED_REGION.search(n) and not EXCLUDED_INFO.search(n)]


def find_indent(lines, start):
    for line in lines[start:]:
        if line.strip():
            return re.match(r"^\s*", line).group(0)
    return ""


def format_group_block(indent, node_picks):
    group = {"name": GROUP_NAME, "type": "select", "proxies": list(node_picks)}
    dumped = yaml.safe_dump([group], allow_unicode=True, sort_keys=False, default_flow_style=False, width=4096)
    return [indent + line if line.strip() else line for line in dumped.rstrip("\n").splitlines()]


def inject_into_profile(text, node_picks, rule_lines):
    lines = text.splitlines()
    out = []
    rules_done = groups_done = False
    for idx, line in enumerate(lines):
        out.append(line)
        if not groups_done and re.match(r"^proxy-groups\s*:\s*$", line):
            out.extend(format_group_block(find_indent(lines, idx + 1), node_picks))
            groups_done = True
        elif not rules_done and re.match(r"^rules\s*:\s*$", line):
            indent = find_indent(lines, idx + 1)
            out.extend(indent + "- " + r for r in rule_lines)
            rules_done = True
    result = "\n".join(out)
    if text.endswith("\n"):
        result += "\n"
    return result, rules_done, groups_done


def append_profile_item(text, uid, name, filename):
    if not text.endswith("\n"):
        text += "\n"
    name_scalar = yaml.safe_dump(name, allow_unicode=True).strip().splitlines()[0]
    block = (
        "- uid: {}\n"
        "  type: local\n"
        "  name: {}\n"
        "  desc: ''\n"
        "  file: {}\n"
        "  updated: {}\n"
        "  option: {{}}\n"
    ).format(uid, name_scalar, filename, int(time.time()))
    return text + block


def normalize_profile_name(name):
    text = str(name or "").strip()
    if text.lower().endswith(".yaml"):
        text = text[:-5]
    return text.strip()


def is_injected_rule(stripped, hosts_set):
    if not stripped or stripped.startswith("#"):
        return False
    if GROUP_NAME in stripped or stripped in hosts_set:
        return True
    patterns = [
        r"^PROCESS-NAME,(Antigravity\.exe|Antigravity IDE\.exe|language_server\.exe|language_server_windows_x64\.exe),",
        r"^DOMAIN-KEYWORD,antigravity,",
        r"^DOMAIN-SUFFIX,antigravity\.google,",
        r"^DOMAIN-SUFFIX,run\.app,",
        r"^DOMAIN-SUFFIX,deepmind\.(google|com),",
        r"^DOMAIN-KEYWORD,cloudcode-pa,",
        r"^DOMAIN-SUFFIX,generativelanguage\.googleapis\.com,",
        r"^DOMAIN-SUFFIX,google\.dev,",
        r"^DOMAIN-SUFFIX,aistudio\.google\.com,",
    ]
    return any(re.match(p, stripped) for p in patterns)


def strip_injections(text, hosts_rules):
    lines = text.splitlines()
    out = []
    hosts_set = set(hosts_rules)
    in_groups = False
    skip_block = False
    block_indent = ""
    for line in lines:
        stripped = line.strip()
        if re.match(r"^proxy-groups\s*:\s*$", line):
            in_groups = True
            out.append(line)
            continue
        if in_groups and line and not line[0].isspace():
            in_groups = False
        if skip_block:
            if not stripped:
                continue
            indent = re.match(r"^\s*", line).group(0)
            if len(indent) <= len(block_indent):
                skip_block = False
            else:
                continue
        if in_groups and re.match(r"^\s*-\s*name:\s*[\"']?{}".format(re.escape(GROUP_NAME)), line):
            block_indent = re.match(r"^\s*", line).group(0)
            skip_block = True
            continue
        if is_injected_rule(stripped, hosts_set):
            continue
        out.append(line)
    result = "\n".join(out)
    if text.endswith("\n"):
        result += "\n"
    return result


def init_clash(verge, log, lang):
    if yaml is None:
        log(tr(lang, "log_pyyaml_missing"))
        return False
    profiles_path = verge / "profiles.yaml"
    data = yaml_load(profiles_path)
    current = data.get("current")
    items = data.get("items") or []
    profile = next((i for i in items if isinstance(i, dict) and i.get("uid") == current), None)
    if profile is None:
        log(tr(lang, "log_no_profile"))
        return False
    src_path = verge / "profiles" / str(profile.get("file", ""))
    if not src_path.exists():
        log(tr(lang, "log_no_file", src_path.name))
        return False

    base_name = normalize_profile_name(profile.get("name") or src_path.stem)
    if base_name.endswith(COPY_SUFFIX):
        orig_base = base_name[: -len(COPY_SUFFIX)]
        source = next(
            (
                i for i in items
                if isinstance(i, dict)
                and i.get("type") != "local"
                and (
                    normalize_profile_name(i.get("name")) == orig_base
                    or normalize_profile_name(i.get("file")) == orig_base
                )
            ),
            None,
        )
        if source is not None:
            src_path = verge / "profiles" / str(source.get("file", ""))
            base_name = orig_base
    new_name = base_name + COPY_SUFFIX

    nodes, _ = extract_proxies_and_groups(src_path)
    picks = allowed_nodes(nodes)
    if not picks:
        log(tr(lang, "log_inject_fail"))
        return False
    picks = picks + ["DIRECT"]
    log(tr(lang, "log_nodes", len(nodes), len(picks) - 1))

    rules = hosts_direct_rules() + antigravity_rule_strings()
    text = src_path.read_text(encoding="utf-8-sig", errors="ignore")
    text = strip_injections(text, rules)
    new_text, rules_ok, groups_ok = inject_into_profile(text, picks, rules)
    if not (rules_ok and groups_ok):
        log(tr(lang, "log_inject_fail"))
        return False

    existing = next(
        (i for i in items if isinstance(i, dict) and i.get("type") == "local" and str(i.get("name")) == new_name),
        None,
    )
    if existing is not None:
        uid = str(existing.get("uid"))
        filename = str(existing.get("file") or (uid + ".yaml"))
    else:
        uid = generate_uid()
        filename = uid + ".yaml"
    (verge / "profiles" / filename).write_text(new_text, encoding="utf-8")
    if existing is not None:
        log(tr(lang, "log_reuse_profile", filename))
    else:
        log(tr(lang, "log_new_profile", base_name, filename))
    log(tr(lang, "log_rules_added", len(rules)))
    log(tr(lang, "log_group_added", GROUP_NAME, len(picks) - 1))

    backup = profiles_path.with_name("profiles.yaml.antigravity.bak")
    if not backup.exists():
        shutil.copy2(profiles_path, backup)
        log(tr(lang, "log_backup"))
    ptext = profiles_path.read_text(encoding="utf-8", errors="ignore")
    if existing is None:
        ptext = append_profile_item(ptext, uid, new_name, filename)
    ptext = re.sub(r"(?m)^current:.*$", "current: {}".format(uid), ptext, count=1)
    profiles_path.write_text(ptext, encoding="utf-8")

    check = yaml_load(profiles_path)
    verified = check.get("current") == uid and any(
        isinstance(i, dict) and i.get("uid") == uid for i in (check.get("items") or [])
    )
    if not verified:
        log(tr(lang, "log_verify_fail"))
        return False
    log(tr(lang, "log_verify_ok", new_name))
    log(tr(lang, "log_switched"))
    log(tr(lang, "log_init_done"))
    return True


class ProxyHelperApp:
    def __init__(self, root):
        self.root = root
        self.cfg = load_config()
        self.lang = self.cfg.get("lang") if self.cfg.get("lang") in ("zh", "en") else default_lang()
        self.settings_paths = find_antigravity_settings()
        self.widgets = {}
        root.title(tr(self.lang, "app_title"))
        root.geometry("760x660")
        root.minsize(680, 580)
        apply_window_icon(root)
        self.build_ui()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(150, self.on_startup)

    def build_ui(self):
        pad = {"padx": 8, "pady": 4}
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Label(bar, text=tr(self.lang, "lang_label")).pack(side="left")
        self.var_lang = tk.StringVar(value="中文" if self.lang == "zh" else "English")
        combo = ttk.Combobox(bar, textvariable=self.var_lang, values=["中文", "English"], width=10, state="readonly")
        combo.pack(side="left", padx=6)
        combo.bind("<<ComboboxSelected>>", self.on_lang_change)

        frame_proxy = ttk.LabelFrame(self.root, text=tr(self.lang, "frame_proxy"))
        frame_proxy.pack(fill="x", **pad)
        self.widgets["frame_proxy"] = frame_proxy
        self.var_host = tk.StringVar(value=str(self.cfg.get("proxy_host", DEFAULT_HOST)))
        self.var_port = tk.StringVar(value=str(self.cfg.get("proxy_port", DEFAULT_PORT)))
        ttk.Label(frame_proxy, text=tr(self.lang, "addr")).grid(row=0, column=0, padx=6, pady=6)
        ttk.Entry(frame_proxy, textvariable=self.var_host, width=18).grid(row=0, column=1, pady=6)
        ttk.Label(frame_proxy, text=tr(self.lang, "port")).grid(row=0, column=2, padx=6, pady=6)
        ttk.Entry(frame_proxy, textvariable=self.var_port, width=10).grid(row=0, column=3, pady=6)
        self.btn_test = ttk.Button(frame_proxy, text=tr(self.lang, "test_conn"), command=self.check_port)
        self.btn_test.grid(row=0, column=4, padx=10)
        self.lbl_port = ttk.Label(frame_proxy, text="")
        self.lbl_port.grid(row=0, column=5, padx=4)

        frame_actions = ttk.Frame(self.root)
        frame_actions.pack(fill="x", **pad)
        self.btn_apply = ttk.Button(frame_actions, text=tr(self.lang, "apply_btn"), command=self.apply_proxy)
        self.btn_apply.pack(side="left", padx=4)
        self.btn_onetime = ttk.Button(frame_actions, text=tr(self.lang, "onetime_btn"), command=self.onetime_setup)
        self.btn_onetime.pack(side="left", padx=4)
        self.btn_restore = ttk.Button(frame_actions, text=tr(self.lang, "restore_btn"), command=self.restore_env_click)
        self.btn_restore.pack(side="left", padx=4)

        frame_init = ttk.LabelFrame(self.root, text=tr(self.lang, "frame_init"))
        frame_init.pack(fill="x", **pad)
        self.widgets["frame_init"] = frame_init
        self.btn_init = ttk.Button(frame_init, text=tr(self.lang, "init_btn"), command=self.init_clash_click)
        self.btn_init.pack(side="left", padx=6, pady=6)
        self.lbl_init_hint = ttk.Label(frame_init, text=tr(self.lang, "init_hint"), foreground="#666666")
        self.lbl_init_hint.pack(side="left", padx=4)

        frame_launch = ttk.LabelFrame(self.root, text=tr(self.lang, "frame_launch"))
        frame_launch.pack(fill="x", **pad)
        self.widgets["frame_launch"] = frame_launch
        self.apps = self.find_apps()
        self.btn_ag = ttk.Button(frame_launch, text=tr(self.lang, "launch_ag"), command=lambda: self.launch("Antigravity.exe"))
        self.btn_ag.pack(side="left", padx=6, pady=6)
        self.btn_ide = ttk.Button(frame_launch, text=tr(self.lang, "launch_ide"), command=lambda: self.launch("Antigravity IDE.exe"))
        self.btn_ide.pack(side="left", padx=6, pady=6)

        self.var_restore = tk.BooleanVar(value=bool(self.cfg.get("restore_env_on_exit", True)))
        self.chk_keep = ttk.Checkbutton(self.root, text=tr(self.lang, "keep_env"), variable=self.var_restore)
        self.chk_keep.pack(fill="x", padx=10, pady=2)

        self.log_box = scrolledtext.ScrolledText(
            self.root, height=15, state="disabled",
            font=("Microsoft YaHei UI", 9), spacing1=1, spacing3=1,
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=8)

    def retranslate(self):
        self.root.title(tr(self.lang, "app_title"))
        self.widgets["frame_proxy"].configure(text=tr(self.lang, "frame_proxy"))
        self.widgets["frame_init"].configure(text=tr(self.lang, "frame_init"))
        self.widgets["frame_launch"].configure(text=tr(self.lang, "frame_launch"))
        self.btn_test.configure(text=tr(self.lang, "test_conn"))
        self.btn_apply.configure(text=tr(self.lang, "apply_btn"))
        self.btn_onetime.configure(text=tr(self.lang, "onetime_btn"))
        self.btn_restore.configure(text=tr(self.lang, "restore_btn"))
        self.btn_init.configure(text=tr(self.lang, "init_btn"))
        self.lbl_init_hint.configure(text=tr(self.lang, "init_hint"))
        self.btn_ag.configure(text=tr(self.lang, "launch_ag"))
        self.btn_ide.configure(text=tr(self.lang, "launch_ide"))
        self.chk_keep.configure(text=tr(self.lang, "keep_env"))

    def on_lang_change(self, _event=None):
        self.lang = "zh" if self.var_lang.get() == "中文" else "en"
        self.cfg["lang"] = self.lang
        save_config(self.cfg)
        self.retranslate()
        self.log(tr(self.lang, "log_lang_changed"))

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", "[{}] {}\n".format(timestamp, message))
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def read_proxy(self):
        host = self.var_host.get().strip()
        port = self.var_port.get().strip()
        if not host:
            raise ValueError(tr(self.lang, "addr_empty"))
        if not port.isdigit() or not 1 <= int(port) <= 65535:
            raise ValueError(tr(self.lang, "port_invalid"))
        return host, port

    def check_port(self):
        try:
            host, port = self.read_proxy()
        except ValueError as e:
            self.lbl_port.configure(text="❌ " + str(e))
            return
        if port_open(host, port):
            self.lbl_port.configure(text=tr(self.lang, "port_ok"))
            self.log(tr(self.lang, "log_clash_ok", host, port))
        else:
            self.lbl_port.configure(text=tr(self.lang, "port_bad"))
            self.log(tr(self.lang, "log_clash_bad", host, port))

    def apply_proxy(self, silent=False):
        try:
            host, port = self.read_proxy()
        except ValueError as e:
            self.log("❌ " + str(e))
            return
        self.cfg["proxy_host"] = host
        self.cfg["proxy_port"] = port
        apply_env(host, port, self.cfg)
        self.log(tr(self.lang, "log_env_set", proxy_url(host, port)))
        self.settings_paths = find_antigravity_settings()
        count = write_antigravity_proxy(self.settings_paths, host, port)
        if count:
            self.log(tr(self.lang, "log_settings_written", count))
        else:
            self.log(tr(self.lang, "log_settings_missing"))
        if not port_open(host, port):
            self.log(tr(self.lang, "log_clash_bad", host, port))
        self.log(tr(self.lang, "log_restart_app"))

    def restore_env_click(self):
        try:
            host, port = self.read_proxy()
        except ValueError:
            host, port = DEFAULT_HOST, DEFAULT_PORT
        restore_env(self.cfg)
        removed = remove_antigravity_proxy(self.settings_paths, host, port)
        self.log(tr(self.lang, "log_restore_done"))
        if removed:
            self.log(tr(self.lang, "log_settings_removed", removed))

    def onetime_setup(self):
        if not messagebox.askyesno(tr(self.lang, "app_title"), tr(self.lang, "dlg_onetime_ask")):
            self.log(tr(self.lang, "log_onetime_cancelled"))
            return
        self.apply_proxy(silent=True)
        if not self.init_clash_click():
            return
        self.var_restore.set(False)
        self.cfg["restore_env_on_exit"] = False
        save_config(self.cfg)
        self.log(tr(self.lang, "log_onetime_done"))
        messagebox.showinfo(tr(self.lang, "dlg_done_title"), tr(self.lang, "log_onetime_done"))

    def init_clash_click(self):
        verge = find_verge_dir()
        if verge is None:
            self.log(tr(self.lang, "log_no_verge"))
            messagebox.showerror(tr(self.lang, "dlg_err_title"), tr(self.lang, "log_no_verge"))
            return False
        relaunch_exe = None
        if verge_running():
            if not messagebox.askyesno(tr(self.lang, "app_title"), tr(self.lang, "dlg_restart_ask")):
                self.log(tr(self.lang, "log_init_cancelled"))
                return False
            relaunch_exe = find_verge_exe()
            self.log(tr(self.lang, "log_verge_stopping"))
            stop_verge()
            time.sleep(1.2)
        self.log(tr(self.lang, "log_init_start", str(verge)))
        try:
            ok = init_clash(verge, self.log, self.lang)
        except Exception as e:
            self.log("❌ {}".format(e))
            ok = False
        if ok and relaunch_exe is not None:
            if launch_verge(relaunch_exe):
                self.log(tr(self.lang, "log_verge_relaunched", str(relaunch_exe)))
            else:
                self.log(tr(self.lang, "log_verge_exe_missing"))
        if not ok:
            messagebox.showerror(tr(self.lang, "dlg_err_title"), tr(self.lang, "dlg_fail_msg"))
            return False
        messagebox.showinfo(tr(self.lang, "dlg_done_title"), tr(self.lang, "dlg_done_msg"))
        return True

    def find_apps(self):
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs"
        result = []
        if not base.exists():
            return result
        for d in base.iterdir():
            if not d.is_dir() or not d.name.lower().startswith("antigravity"):
                continue
            for exe in d.glob("*.exe"):
                low = exe.name.lower()
                if low.startswith("antigravity") and "uninstall" not in low:
                    result.append(exe)
        return result

    def launch(self, exe_name):
        self.apply_proxy(silent=True)
        target = next((p for p in self.apps if p.name.lower() == exe_name.lower()), None)
        if target is None:
            self.log(tr(self.lang, "log_launch_missing", exe_name))
            return
        try:
            subprocess.Popen([str(target)], cwd=str(target.parent))
            self.log(tr(self.lang, "log_launch_ok", target.name))
        except Exception as e:
            self.log(tr(self.lang, "log_launch_fail", e))

    def on_startup(self):
        self.log(tr(self.lang, "log_started", tr(self.lang, "app_title")))
        if yaml is None:
            self.log(tr(self.lang, "log_pyyaml_missing"))
        self.log(tr(self.lang, "log_settings_found", len(self.settings_paths)))
        verge = find_verge_dir()
        self.log(tr(self.lang, "log_verge_dir", str(verge) if verge else tr(self.lang, "log_verge_none")))
        self.apply_proxy(silent=True)
        self.check_port()

    def on_close(self):
        self.cfg["restore_env_on_exit"] = bool(self.var_restore.get())
        self.cfg["proxy_host"] = self.var_host.get().strip() or DEFAULT_HOST
        self.cfg["proxy_port"] = self.var_port.get().strip() or DEFAULT_PORT
        self.cfg["lang"] = self.lang
        save_config(self.cfg)
        if self.var_restore.get():
            host = self.cfg["proxy_host"]
            port = self.cfg["proxy_port"]
            restore_env(self.cfg)
            remove_antigravity_proxy(self.settings_paths, host, port)
        self.root.destroy()


def main():
    if "--init-clash" in sys.argv:
        verge = find_verge_dir()
        if verge is None:
            print("Clash Verge config directory not found")
            return 1
        ok = init_clash(verge, lambda m: print(m), default_lang())
        return 0 if ok else 1
    if tk is None:
        print("tkinter is not available, please install the full Python package")
        return 1
    enable_dpi_awareness()
    root = tk.Tk()
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Acshoes.AntigravityProxyHelper")
    except Exception:
        pass
    try:
        dpi = root.winfo_fpixels("1i")
        root.call("tk", "scaling", max(1.0, dpi / 72.0))
    except Exception:
        pass
    ProxyHelperApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
