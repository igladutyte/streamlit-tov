# quick_check.py
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)  # ensure .env overrides shell
k = os.getenv("OPENAI_API_KEY", "")
print("len:", len(k), "head:", k[:7], "tail:", repr(k[-12:]))
print("invalid chars at end:", [ord(c) for c in k[-12:]])

assert re.match(r"^sk-[a-z]+-[A-Za-z0-9_-]{20,}$", k), "Key format looks wrong"

client = OpenAI()  # uses env var
r = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "ping"}],
    max_tokens=5,
)
print("OK:", bool(r.choices[0].message.content))
