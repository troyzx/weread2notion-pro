#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

cookie_str = os.getenv("WEREAD_COOKIE")
print("完整 Cookie 字符串:")
print(repr(cookie_str))
print("\nCookie 长度:", len(cookie_str))
