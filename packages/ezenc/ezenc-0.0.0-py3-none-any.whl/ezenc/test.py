
# 簡易暗号化ツール [ezenc]
# 【動作確認 / 使用例】

import sys
import ezpip
ezenc = ezpip.load_develop("ezenc", "../", develop_flag = True)

# 暗号化
ezenc.enc()
