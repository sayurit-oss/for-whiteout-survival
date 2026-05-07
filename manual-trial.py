import streamlit as st
import pandas as pd
import json
import os
import shutil
import glob
from datetime import datetime, timedelta

# --- 基本設定 ---
DB_FILE = 'event_database.json'
BACKUP_DIR = 'backups'
os.makedirs(BACKUP_DIR, exist_ok=True)

# --- データベース操作関数 ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(db):
    # メイン保存
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    # 保存時に自動バックアップを作成
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"event_db_{ts}.json")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    # 古いバックアップ（7日以上）を掃除
    clean_old_backups()

def clean_old_backups():
    now = datetime.now()
    for f in glob.glob(os.path.join(BACKUP_DIR, "event_db_*.json")):
        if now - datetime.fromtimestamp(os.path.getctime(f)) > timedelta(days=7):
            os.remove(f)

# --- マニュアル表示（すべて折りたたみ形式） ---
def manual_page():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")

    tab1, tab2, tab3 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略"])

    with tab1:
        with st.expander("1. 新規加入の審査基準"):
            st.markdown("""
            - **炉レベル**: 25以上 / **総力**: 3000万以上
            - **名前**: 初期ネーム以外
            - **⚠️ IDチェック**: **IDが「74」始まり**はスパイ警戒！個別メッセージで意思疎通を確認。
            """)
        with st.expander("2. R3への昇格ステップ"):
            st.markdown("1. 盟主にフレンド申請\n2. 本部周辺へ移転\n3. 名前を「ʕ·ᴥ·ʔᴹᴹᶜ」に変更")
        with st.expander("3. 非アクティブ整理（退会処置）"):
            st.code("お疲れ様です。長期未ログインのため、一旦同盟を離脱していただく形となります。また戻られた際には、再度申請してくださいね～(*^^*) 歓迎します！")

    with tab2:
        with st.expander("1. 効率的なルート作成と旗建設"):
            st.markdown("- **最短ルート**: 同盟資源地や重要施設（城砦・要塞）を目指す。\n- **他同盟との距離**: NAPに基づき、最低1マス以上空ける。")
        with st.expander("2. パズル用「兵1旗」の運用"):
            st.markdown("**目的**: 建設時間を長くし、全員がパズルタスクをクリアできるようにする。")
            st.code("パズル用の旗なので、兵士1・英雄なしでお願いします！一旦送還しますね。")
        with st.expander("3. 同盟安全採集ポイントの設置"):
            st.markdown("順番：養殖場 ⇒ 製材所 ⇒ コークス工場 ⇒ 製鉄所\n設置後は座標を同盟チャットで共有！")

    with tab3:
        with st.expander("1. 🐻 熊狩り"):
            st.code("🚩集結主：一番強い英雄で！\n🚩乗る人：左英雄ジェシー等。兵士割合は弓多め（盾2槍2弓6など）🏹")
        with st.expander("2. ⚔️ 兵器工場 / 峡谷合戦"):
            st.markdown("- **志願した方は当日絶対参加！**\n- 欠員が出るとみんなが苦労するので念押し。")
        with st.expander("3. 🛡️ キルイベ / 王国ルール"):
            st.markdown("- 都市攻撃は「同盟未加入」を3回確認してから。\n- シールド推奨（引きこもり）も一つの戦略！")

# --- 管理者画面（修正版） ---
def admin_page():
    st.header("🛠️ 管理者・履歴設定")
    db = load_db()

    # 1. 履歴管理
    with st.expander("🕒 過去のデータに復元"):
        backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "*.json")), reverse=True)
        if backups:
            selected = st.selectbox("戻したい日時を選択", backups, format_func=lambda x: os.path.basename(x))
            if st.button("選んだデータで復元する"):
                with open(selected, 'r', encoding='utf-8') as f:
                    restored_db = json.load(f)
                save_db(restored_db)
                st.success("復元完了！再読み込みしてね。")
                st.rerun()

    # 2. イベント編集
    with st.expander("📝 登録済みイベントの修正"):
        event_name = st.selectbox("修正するイベント", list(db.keys()))
        if event_name:
            sched = db[event_name].get("スケジュール", {})
            df = pd.DataFrame.from_dict(sched, orient='index').transpose()
            edited_df = st.data_editor(df, num_rows="dynamic")
            
            if st.button("この内容で保存"):
                # DataFrameからNoneを省いて辞書に戻す
                new_sched = {col: [v for v in edited_df[col].tolist() if pd.notna(v) and v != ""] for col in edited_df.columns}
                db[event_name]["スケジュール"] = new_sched
                save_db(db)
                st.success(f"{event_name} を更新したよ！✨")

# --- メインルーチン ---
st.sidebar.title("ʕ·ᴥ·ʔ MMC Menu")
menu = st.sidebar.radio("メニュー", ["ツール起動✨", "運営マニュアル📜", "管理者設定🛠️"])

if menu == "ツール起動✨":
    # (ここには以前の案内文生成ロジックを入れてください)
    st.title("✨ 案内文自動生成")
    st.write("イベントを選択して、案内文を作ろう！")
elif menu == "運営マニュアル📜":
    manual_page()
elif menu == "管理者設定🛠️":
    admin_page()
