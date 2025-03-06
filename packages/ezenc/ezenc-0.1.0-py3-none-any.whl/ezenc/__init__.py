# 簡易暗号化ツール [ezenc]

import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

# keyを256ビット (32バイト) に変換
def fix_key(k): return SHA256.new(k).digest()

# 暗号化
def enc(d, k):
	k = fix_key(k)
	iv = get_random_bytes(16)	# ランダムなinitial-vecにより、安全に毎回異なる暗号文を生成する
	return iv + AES.new(k, AES.MODE_CBC, iv).encrypt(pad(d, 16))

# 復号
def dec(d, k):
	k = fix_key(k)
	return unpad(AES.new(k, AES.MODE_CBC, d[:16]).decrypt(d[16:]), 16)
