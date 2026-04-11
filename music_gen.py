#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import sys

API_KEY = "sk-cp-naHS-NsQJ5SPtcsk-CMMmTBAymM5rCG0g7ea7JrugzK1XfKUTRHDGL4DHuUn7mYe_E2PWcdWoqBpvNwc6XjeWrCMPJpk0knWNvRJHl4Uk1lu7JL_PON__mI"
URL = "https://api.minimax.io/v1/music_generation"

payload = {
    "model": "music-2.6",
    "prompt": "Classical Chinese music, traditional Chinese instruments like guqin and pipa, elegant and refined melody reminiscent of ancient Chinese palace music, gentle and lyrical, melodious",
    "lyrics": """[Intro]
青花瓷畔煙雨濛
墨染天青色

[Verse]
天青色等煙雨
而我在等你
炊煙裊裊升起
隔江千萬里

[Pre Chorus]
如傳世的青花瓷
自顧自美麗
釉色渲染的風景
如鏡中水的柔情

[Chorus]
你眼帶笑意
江南風情萬種雲淡風輕
一縷青絲千萬縷情
素胚勾勒筆鋒濃淡皆文章
瓶身描繪的牡丹
一如你初妝
冉冉清香在風中飄蕩

[Verse 2]
釉面晶瑩剔透
筆鋒婉轉纏綿
婉約動人的韻味
訴說著永恆的思念

[Chorus]
天青色等煙雨
而我在等你
月色被打撈起
暈開了結局
如傳世的青花瓷
在夜色中靜靜的飄逸

[Outro]
青花瓷上刻相思
繁華落盡總是情""",
    "instrumental": False,
    "output_format": "url"
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    URL,
    data=data,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(json.dumps(result, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
