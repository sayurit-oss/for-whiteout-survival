import streamlit as st
import json
import os
import shutil
from datetime import datetime

# --- 設定 ---
MANUAL_FILE = 'manual_data.json'
BACKUP_DIR = 'backups_manual'
os.makedirs(BACKUP_DIR, exist_ok=True)

# --- データの読み書き ---
def load_manual():
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 初期データ
    return {
        "👥 メンバー管理": "## 1. 新規加入者の審査・承認\n申請一覧を確認し、以下の条件を**すべて**満たす場合のみ承認します...",
        "🚩 領土・資源": "## 1. 効率的なルート作成\n領土は「最短距離」かつ「最大効率」で広げるのが基本です...",
        "⚔️ イベント攻略": "## 1. 【熊狩り】\n🐻今日は熊狩り🐻\n🚩 集結を出す人：自分の1番強い英雄でお願いします！..."
    }

def save_manual(data):
    # メイン保存
    with open(MANUAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # バックアップ
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(MANUAL_FILE, os.path.join(BACKUP_DIR, f"manual_v_{ts}.json"))

# --- UIセクション ---

def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    manual_data = load_manual()
    
    # すべて折りたたみ（Expander）で表示
    for title, content in manual_data.items():
        with st.expander(title):
            st.markdown(content)

def admin_page():
    st.title("🛠️ 管理者画面：マニュアルの加筆修正")
    manual_data = load_manual()

    # 1. 修正したいセクションを選択
    section = st.selectbox("修正する項目を選んでね", list(manual_data.keys()))

    # 2. テキストエリアで中身を編集
    # ※ heightを大きくすることで、ワードのような感覚で編集できます
    new_content = st.text_area(f"「{section}」の内容を編集", 
                               value=manual_data[section], 
                               height=400)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("保存する✨"):
            manual_data[section] = new_content
            save_manual(manual_data)
            st.success("マニュアルを更新したよ！😊")
            st.rerun()

    # 3. 履歴復元機能（マニュアル用）
    st.divider()
    st.subheader("🕒 過去のマニュアルに戻す")
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "*.json")), reverse=True)
    if backups:
        selected_backup = st.selectbox("バックアップを選択", backups)
        if st.button("この版を復元する"):
            with open(selected_backup, 'r', encoding='utf-8') as f:
                restored = json.load(f)
            save_manual(restored)
            st.success("マニュアルを過去の状態に戻したよ！")
            st.rerun()

# --- メインメニュー ---
menu = st.sidebar.radio("メニュー", ["マニュアル閲覧📜", "管理者設定🛠️"])

if menu == "マニュアル閲覧📜":
    manual_view_page()
elif menu == "管理者設定🛠️":
    admin_page()
