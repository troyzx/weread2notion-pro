#!/usr/bin/env python3
"""
查看 CookieCloud 的完整响应数据结构
"""
import requests
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

HOST = "http://tencent.troyzx.live:8888"
UUID = "cxx2hB6fxYMZ6inktjfuoa"
PASSWORD = "onBKtd61Ak3ZGTmWR7st13"


def evp_bytes_to_key(password, salt, key_len, iv_len):
    """OpenSSL EVP_BytesToKey 实现"""
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
    return ms[:key_len], ms[key_len:key_len + iv_len]


def decrypt():
    """解密 CookieCloud 数据"""
    url = f"{HOST}/get/{UUID}"
    response = requests.get(url, timeout=10)
    data = response.json()
    
    encrypted_data = data["encrypted"]
    
    # 生成密钥
    key_source = f"{UUID}-{PASSWORD}"
    md5_hash = hashlib.md5(key_source.encode()).hexdigest()
    key = md5_hash[:16]
    
    # 解密
    encrypted_bytes = base64.b64decode(encrypted_data)
    salt = encrypted_bytes[8:16]
    ciphertext = encrypted_bytes[16:]
    
    aes_key, iv = evp_bytes_to_key(key.encode(), salt, 32, 16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    result = json.loads(decrypted.decode("utf-8"))
    
    return result


print("=" * 80)
print("CookieCloud 完整数据结构")
print("=" * 80)

result = decrypt()

# 查看结构
print("\n顶级键:")
for key in result.keys():
    print(f"  - {key}")

# 查看 cookie_data
print("\ncookie_data 域名列表:")
if "cookie_data" in result:
    for domain in result["cookie_data"].keys():
        print(f"  - {domain}")

# 详细查看 weread.qq.com 的 cookie
print("\nweread.qq.com 的 Cookie:")
if "cookie_data" in result and "weread.qq.com" in result["cookie_data"]:
    cookies = result["cookie_data"]["weread.qq.com"]
    print(f"  总数: {len(cookies)}")
    for cookie in cookies:
        print(f"\n    名称: {cookie.get('name')}")
        print(f"    值: {cookie.get('value')}")
        if cookie.get('domain'):
            print(f"    domain: {cookie.get('domain')}")
        if cookie.get('path'):
            print(f"    path: {cookie.get('path')}")
        if cookie.get('expirationDate'):
            print(f"    expirationDate: {cookie.get('expirationDate')}")
        if cookie.get('httpOnly'):
            print(f"    httpOnly: {cookie.get('httpOnly')}")
        if cookie.get('secure'):
            print(f"    secure: {cookie.get('secure')}")

# 查看 localStorage
print("\n\nlocalStorage 数据:")
if "local_storage" in result:
    for domain in result["local_storage"].keys():
        print(f"  {domain}:")
        storage = result["local_storage"][domain]
        for key, value in storage.items():
            print(f"    {key}: {value[:50]}..." if len(str(value)) > 50 else f"    {key}: {value}")
else:
    print("  (无 localStorage 数据)")

print("\n" + "=" * 80)
