# 簡易暗号化ツール [ezenc]
# 【動作確認 / 使用例】

import sys
import ezpip
ezenc = ezpip.load_develop("ezenc", "../", develop_flag = True)

# 暗号化
enc_res = ezenc.enc(b"hello!", b"test-key")
print(enc_res)

# 復号
dec_res = ezenc.dec(enc_res, b"test-key")
print(dec_res)
