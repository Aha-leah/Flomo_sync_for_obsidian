import os
import time
import json
import asyncio
import subprocess
import argparse
import re
from playwright.async_api import async_playwright
from datetime import datetime

# ================= 配置区 (Configuration) =================

# 1. 你的 Flomo 账号和密码 (用于自动登录)
# 如果留空，脚本运行时会弹窗让你扫码登录
FLOMO_ACCOUNT = ""  # e.g. "13800000000"
FLOMO_PASSWORD = "" # e.g. "password123"

# 2. 笔记保存路径
# 默认保存在脚本所在目录下的 "Flomo" 文件夹中
# 如果你在 Obsidian 中使用，建议修改为你 Vault 中的某个绝对路径
# 例如: "/Users/username/Documents/Obsidian/MyVault/Flomo"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "Flomo")

# =======================================================

FLOMO_LOGIN_URL = "https://v.flomoapp.com/login"
FLOMO_HOME_URL = "https://v.flomoapp.com/"

# 登录状态保存文件 (免去每次扫码)
STATE_FILE = os.path.join(SCRIPT_DIR, "flomo_state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "flomo_sync.log")

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("--default-tag", help="Default tag to append to memos", default="")
parser.add_argument("--output-dir", help="Directory to save memos", default=DEFAULT_OUTPUT_DIR)
args, unknown = parser.parse_known_args()

DEFAULT_TAG = args.default_tag
OBSIDIAN_VAULT_PATH = args.output_dir

def log(msg):
    """记录日志到文件，方便排查错误"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except:
        pass 

def extract_tags(content):
    """从内容中提取标签 (#Tag)"""
    tags = set()
    matches = re.findall(r"(?:^|\s)#([a-zA-Z0-9_\u4e00-\u9fa5/\-]+)", content)
    for t in matches:
        tags.add(t)
    return list(tags)

def send_notification(title, message):
    """发送 macOS 通知"""
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])
    except Exception as e:
        print(f"⚠️ 通知发送失败: {e}")

async def save_markdown(memo_data):
    """把抓取到的数据保存为 Markdown"""
    if not os.path.exists(OBSIDIAN_VAULT_PATH):
        os.makedirs(OBSIDIAN_VAULT_PATH)
        
    content = memo_data.get('content', '')
    created_at = memo_data.get('created_at', '')
    tags = memo_data.get('tags', [])
    files = memo_data.get('files', [])
    memo_id = memo_data.get('memo_id')
    
    extracted_tags = extract_tags(content)
    all_tags = sorted(list(set(tags + extracted_tags)))

    try:
        dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        date_folder = dt.strftime("%Y-%m-%d")
    except:
        dt = datetime.now()
        date_folder = dt.strftime("%Y-%m-%d") 
        
    if DEFAULT_TAG:
        content += f" {DEFAULT_TAG}"
        if DEFAULT_TAG not in all_tags:
            all_tags.append(DEFAULT_TAG)

    images_str = ""
    for file_url in files:
        images_str += f"\n![]({file_url})\n"
        
    tags_line = " ".join([f"#{t}" for t in all_tags])
    url_line = f"https://v.flomoapp.com/mine?memo_id={memo_id}" if memo_id else ""
    update_time = created_at

    md_content = f"""---
created: {created_at}
tags: [{', '.join(all_tags)}]
---

{content}
{images_str}

{created_at}
---------
{tags_line}
{update_time}
{url_line}
"""
    
    target_dir = os.path.join(OBSIDIAN_VAULT_PATH, date_folder)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    safe_content = re.sub(r'[\\/:*?"<>|#]', '', content).strip()
    safe_content = safe_content.replace('\n', ' ')
    
    if len(safe_content) > 30:
        filename_base = safe_content[:30]
    elif safe_content:
        filename_base = safe_content
    else:
        filename_base = f"Memo_{dt.strftime('%H%M%S')}"
        
    file_name = f"{filename_base}.md"
    file_path = os.path.join(target_dir, file_name)
    
    counter = 1
    while os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_file_content = f.read()
            norm_new = "".join(content.split())
            norm_existing = "".join(existing_file_content.split())
            
            if norm_new in norm_existing:
                 return False
        except:
            pass
            
        file_path = os.path.join(target_dir, f"{filename_base}_{counter}.md")
        counter += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"✅ 已保存: {os.path.basename(file_path)}")
    return True

async def run():
    log("🚀 脚本启动...")
    print("🚀 正在启动 Flomo 同步机器人...")
    async with async_playwright() as p:
        use_headless = bool(FLOMO_ACCOUNT and FLOMO_PASSWORD)
        
        browser = await p.chromium.launch(headless=use_headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        if os.path.exists(STATE_FILE):
            print("📥 加载登录状态...")
            try:
                await context.add_cookies(json.load(open(STATE_FILE, 'r')))
            except:
                print("⚠️ Cookie 文件损坏，将重新登录")
            
        page = await context.new_page()
        
        print("🔗 正在打开 Flomo...")
        await page.goto(FLOMO_HOME_URL)
        
        if "login" in page.url:
            print("⚠️ 未检测到有效登录状态")
            
            if FLOMO_ACCOUNT and FLOMO_PASSWORD:
                print("🔑 正在尝试账号密码自动登录...")
                try:
                    if not await page.is_visible("input[type='password']"):
                        await page.get_by_text("账号登录").click()
                        await asyncio.sleep(1)
                    
                    print("✍️ 输入账号密码...")
                    await page.fill("input[type='text']", FLOMO_ACCOUNT)
                    await page.fill("input[type='password']", FLOMO_PASSWORD)
                    await page.get_by_role("button", name="登录").click()
                    await page.wait_for_url("**/mine**", timeout=10000)
                    print("🎉 自动登录成功！")
                except Exception as e:
                    print(f"❌ 自动登录失败: {str(e)}")
                    print("⚠️ 降级处理：请手动扫码/登录...")
            
            if "login" in page.url:
                if use_headless:
                    print("❌ 静默模式下登录失败，请检查账号密码或先关闭静默模式手动登录一次。")
                    await browser.close()
                    return

                print("⚠️ 请在弹出的浏览器中扫码登录！")
                print("⏳ 等待你完成登录 (限时 60 秒)...")
            
                try:
                    await page.wait_for_url("**/mine**", timeout=60000)
                    print("🎉 登录成功！")
                except Exception as e:
                    print("❌ 登录超时或失败，请重试。")
                    await browser.close()
                    return

            cookies = await context.cookies()
            with open(STATE_FILE, 'w') as f:
                json.dump(cookies, f)
            print("💾 登录状态已保存")
        else:
            print("✅ 已自动登录")

        print("🔍 正在扫描最新笔记...")
        await page.wait_for_selector(".memo", timeout=10000)
        
        memos = await page.query_selector_all(".memo")
        print(f"📊 页面上可见笔记数: {len(memos)}")
        
        new_count = 0
        for memo in memos:
            time_el = await memo.query_selector(".time")
            created_at = await time_el.inner_text() if time_el else "Unknown"
            
            content_el = await memo.query_selector(".content")
            content = await content_el.inner_text() if content_el else ""

            memo_id = await memo.get_attribute("data-slug")
            
            files = []
            imgs = await memo.query_selector_all(".files img")
            for img in imgs:
                src = await img.get_attribute("src")
                if src:
                    files.append(src)
            
            is_new = await save_markdown({
                "content": content,
                "created_at": created_at,
                "tags": [],
                "files": files,
                "memo_id": memo_id
            })
            
            if is_new:
                new_count += 1
            
        print("🎉 同步完成！")
        
        if new_count > 0:
            print(f"✨ 发现并同步了 {new_count} 条新笔记")
            send_notification("Flomo 同步助手", f"成功同步了 {new_count} 条新笔记到 Obsidian")
        
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        error_msg = f"❌ 脚本执行发生致命错误: {str(e)}"
        print(error_msg)
        log(error_msg)
        send_notification("Flomo 同步失败", str(e))
        raise e
