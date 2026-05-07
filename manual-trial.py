import streamlit as st
import pandas as pd
import json
import os
import shutil
import glob
from datetime import datetime, timedelta

# --- 設定 ---
DB_FILE = 'event_database.json'
BACKUP_DIR = 'backups'
os.makedirs(BACKUP_DIR, exist_ok=True)

# --- データベース操作 ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    # バックアップ作成
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(DB_FILE, os.path.join(BACKUP_DIR, f"event_db_{ts}.json"))

# --- UIコンポーネント ---
def manual_section():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略", "📢 定型文集"])

    with tab1:
        st.header("新規加入・整理マニュアル")
        with st.expander("1. 新規加入の審査基準", expanded=True):
            st.markdown("""
            - **炉レベル**: 25以上
            - **総力**: 3000万以上
            - **名前**: 初期ネーム以外
            - **⚠️ IDチェック**: ID「74」始まりはスパイ警戒！個別メッセージで意思疎通を確認。
            """)
        with st.expander("2. R3への昇格ステップ"):
            st.markdown("""
            1. 盟主にフレンド申請
            2. 本部周辺へ移転
            3. 名前を「ʕ·ᴥ·ʔᴹᴹᶜ」に変更（ショップで割引カード推奨）
            """)
        with st.expander("3. 非アクティブ整理（退会処置）"):
            st.warning("対象：長期未ログインで自動的にR2へ降格したメンバー")
            st.code("お疲れ様です。長期未ログインのため、一旦同盟を離脱していただく形となります。また戻られた際には、再度申請してくださいね～(*^^*) 歓迎します！")

    with tab2:
        st.header("領土・フラッグ運用")
        st.subheader("1. 効率的なルート作成")
        st.markdown("- **最短距離**: 資源地・重要施設へ一直線\n- **外交配慮**: 他同盟領土とは1マス以上空ける")
        
        st.subheader("2. パズル用「兵1旗」ループ")
        st.info("目的：建設時間を稼ぎ、全員がパズルタスクをこなせるようにする")
        st.markdown("""
        - **設置**: 本ルートに影響しない端っこ
        - **ルール**: 「兵士1名・英雄なし」で建設開始
        - **ループ**: 完了(100%)したら即解体 → 再設置
        """)
        st.code("パズル用の旗なので、兵士1・英雄なしでお願いします！一旦送還しますね。")

    with tab3:
        st.header("主要イベント攻略")
        with st.expander("兵器工場 / 峡谷合戦"):
            st.markdown("- **事前登録**: アンケート結果に基づき時間設定（軍団1：23時、軍団2：21時）\n- **選抜**: 志願者を優先。軍団1はガチ勢、軍団2は総力下位から補充。")
        with st.expander("砦・要塞戦"):
            st.markdown("""
            - **ルール**: 1同盟1要塞2砦まで
            - **初手**: 必ず「集結」のみ。ソロ突撃禁止！
            - **加速**: 初回パエトーンは集結のみ（加速不可にするため）
            """)

    with tab4:
        st.header("コピペ用：イベント案内テンプレート")
        
        st.subheader("🐻 熊狩り")
        st.code("""🐻今日は熊狩り🐻
【時間】くま2 21:00 / くま1 22:00
🚩集結主：一番強い英雄で！
🚩乗る人：左英雄ジェシー・ジャセル・ソユン等
兵士割合は弓多め（盾2槍2弓6など）でダメージ出そう！💪""")

        st.subheader("🛡️ キルイベ案内（通常ルール含む）")
        st.code("""🛡全軍参戦（キルイベ）🛡
明日9時から！サーバールール順守🔥
⭕都市攻撃は同盟未加入3回確認後
⭕タイキルは相手領地外を3回確認
よく分からない方はシールド推奨です😊""")

def tool_section(db):
    st.title("✨ 案内文自動生成ツール")
    # (以前作成した生成ロジックをここに配置)
    st.write("今日のイベントを選択して、案内文をポチッと作ろう！")
    # ... 中略（前回の生成コードが入る）

def admin_section():
    st.title("🛠️ 管理者・履歴設定")
    # (以前作成したバックアップ・復元・編集ロジック)
    pass

# --- メインルーチン ---
st.sidebar.title("ʕ·ᴥ·ʔ MMC Menu")
menu = st.sidebar.radio("メニュー", ["ツール起動✨", "運営マニュアル📜", "管理者設定🛠️"])

db = load_db()

if menu == "ツール起動✨":
    tool_section(db)
elif menu == "運営マニュアル📜":
    manual_section()
elif menu == "管理者設定🛠️":
    admin_section()
