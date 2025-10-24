#!/usr/bin/env python3
"""
从 CookieCloud 获取微信读书 Cookie
"""
import os
from dotenv import load_dotenv
import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import base64

load_dotenv()

# CookieCloud 配置
HOST = "http://tencent.troyzx.live:8888"
UUID = "cxx2hB6fxYMZ6inktjfuoa"
PASSWORD = "onBKtd61Ak3ZGTmWR7st13"


def evp_bytes_to_key(password, salt, key_len, iv_len):
    """
    OpenSSL EVP_BytesToKey 实现
    参考: https://github.com/topaz/paste/blob/master/paste/deploy/converters.py
    """
    m = []
    i = 0
    while len(b"".join(m)) < (key_len + iv_len):
        md5 = hashlib.md5()
        data = password + salt
        if i > 0:
            data = m[i - 1] + password + salt
        md5.update(data)
        m.append(md5.digest())
        i += 1
    ms = b"".join(m)
    return ms[:key_len], ms[key_len : key_len + iv_len]


def decrypt_cookie_cloud():
    """从 CookieCloud 获取并解密 Cookie"""

    print("=== 从 CookieCloud 获取 Cookie ===\n")
    print(f"Host: {HOST}")
    print(f"UUID: {UUID}\n")

    try:
        # 1. 获取加密数据
        print("1. 正在获取加密数据...")
        url = f"{HOST}/get/{UUID}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"✗ 获取失败: HTTP {response.status_code}")
            return None

        data = response.json()
        print("✓ 获取成功\n")

        if not data.get("encrypted"):
            print("✗ 响应中没有 encrypted 字段")
            return None

        # 2. 解密
        print("2. 正在解密...")
        encrypted_data = data["encrypted"]

        # 生成密钥：MD5(uuid + '-' + password) 的前16个字符
        key_source = f"{UUID}-{PASSWORD}"
        md5_hash = hashlib.md5(key_source.encode()).hexdigest()
        key = md5_hash[:16]

        print(f"   密钥: {key}")

        # 解密
        # encrypted 是 base64 编码的数据，格式是 OpenSSL "Salted__" + salt + ciphertext
        encrypted_bytes = base64.b64decode(encrypted_data)

        # 检查 Salted__ 头
        if encrypted_bytes[:8] != b"Salted__":
            print("✗ 无效的加密格式（缺少 Salted__ 头）")
            return None

        salt = encrypted_bytes[8:16]
        ciphertext = encrypted_bytes[16:]

        # 使用 EVP_BytesToKey 推导密钥和 IV
        aes_key, iv = evp_bytes_to_key(key.encode(), salt, 32, 16)

        # 使用 AES CBC 模式解密
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

        decrypted_str = decrypted.decode("utf-8")
        result = json.loads(decrypted_str)
        
        print("✓ 解密成功\n")
        
        # 3. 提取微信读书的 Cookie
        print("3. 提取微信读书 Cookie...")
        cookie_data = result.get("cookie_data", {})
        
        if "weread.qq.com" in cookie_data:
            weread_cookies = cookie_data["weread.qq.com"]
            cookie_str = "; ".join(
                [f"{c['name']}={c['value']}" for c in weread_cookies]
            )
            
            print(f"✓ 找到 {len(weread_cookies)} 个 Cookie\n")
            
            print("=== 微信读书 Cookie ===")
            print(cookie_str)
            print("\n" + "="*50 + "\n")
            
            # 保存到 .env
            env_content = f"""NOTION_TOKEN={os.getenv('NOTION_TOKEN', '')}
NOTION_PAGE={os.getenv('NOTION_PAGE', '')}
WEREAD_COOKIE={cookie_str}
"""
            
            print("将以下内容添加到 .env 文件:\n")
            print(env_content)
            
            return cookie_str
        else:
            print("✗ 没有找到 weread.qq.com 的 Cookie")
            print(f"可用的域名: {list(cookie_data.keys())}")
            return None
        
    except Exception as e:
        print(f"✗ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    decrypt_cookie_cloud()
