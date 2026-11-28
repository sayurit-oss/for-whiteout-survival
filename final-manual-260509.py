import streamlit as st
import pandas as pd
import json
import os
import re
import math
from PIL import Image

# --- Google Gemini ライブラリの安全なインポート (新旧両対応) ---
GENAI_TYPE = None
try:
    from google import genai
    GENAI_TYPE = "new"
except ImportError:
    try:
        import google.generativeai as legacy_genai
        GENAI_TYPE = "legacy"
    except ImportError:
        GENAI_TYPE = None

# --- 設定・ファイルパス ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'
CONFIG_FILE = 'manual_custom_data.json'
MEMBER_ROSTER_FILE = 'alliance_members.json'

# --- 座標・行軍シミュレーター設定 ---
HQ_NAME = "本部"
HQ_COORD = (732, 418)
BASE_FORTRESS_COORD = (597, 800)
BASE_SECONDS = 600.0  # 本部 -> 要塞1号 (600秒)

# 1座標あたりの所要秒数 (速度係数)
base_dist = math.sqrt((BASE_FORTRESS_COORD[0] - HQ_COORD[0])**2 + (BASE_FORTRESS_COORD[1] - HQ_COORD[1])**2)
SEC_PER_UNIT = BASE_SECONDS / base_dist

LOCATIONS = {
    "要塞1号": (597, 800),
    "要塞2号": (400, 597),
    "要塞3号": (597, 400),
    "要塞4号": (800, 597),
    "砦1号": (237, 828),
    "砦2号": (237, 606),
    "砦3号": (237, 348),
    "砦4号": (366, 237),
    "砦5号": (588, 237),
    "砦6号": (846, 237),
    "砦7号": (957, 348),
    "砦8号": (957, 606),
    "砦9号": (957, 828),
    "砦10号": (846, 957),
    "砦11号": (606, 957),
    "砦12号": (366, 957),
}

def get_travel_time(p1_coord, p2_coord):
    dist = math.sqrt((p2_coord[0] - p1_coord[0])**2 + (p2_coord[1] - p1_coord[1])**2)
    sec = dist * SEC_PER_UNIT
    minutes = round(sec / 60)
    return minutes, sec

# --- 同盟メンバー初期名簿 ---
DEFAULT_ROSTER = [
    "わからん", "ringo", "harupon", "マンダラ", "LOSER", "ナーナ", "焼きりんご", "田中一郎", 
    "ハンギョ", "はんぎょどん", "toriaezu beer", "愛犬クル", "くま3", "ショーン伍長", "ベビっく", "いりる", "kara", "ちゃーーーん", "ちゃん②", 
    "mii", "mi mi", "わんこ", "すん", "れくさす", "アッシュ",
