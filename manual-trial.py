import streamlit as st
import json
import os
import shutil
from datetime import datetime
import glob

# --- ファイル設定 ---
MANUAL_FILE = 'manual_data.json'
BACKUP_DIR = 'backups_manual'
os.makedirs(BACKUP_DIR, exist_ok=True)

# --- データの読み書き関数 ---
def load_manual():
    # ファイルがない場合は初期構造を作成して保存
    if not os.path.exists(MANUAL_FILE):
        initial_data = {
            "👥 メンバー管理": ,
            "🚩 領土・資源": "## 領土運用の基本\nここに文章を入力してください。",
            "⚔️ イベント攻略": "## 各種イベントのコツ\nここに文章を入力してください。"
        }
        with open(MANUAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        return initial_data
    
    with open(MANUAL_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_manual(data):
    with open(MANUAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # バックアップ作成
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(MANUAL_FILE, os.path.join(BACKUP_DIR, f"manual_v_{ts}.json"))

# --- 1. マニュアル閲覧画面（タブ × 折りたたみ） ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")
    
    manual_data = load_manual()

    tab1, tab2, tab3 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略"])

    with tab1:
        # 管理画面で編集した本文
        st.markdown(manual_data.get("👥 メンバー管理", ""))
        
        # 枠組みとして残しておきたい「折りたたみ」
        with st.expander("1. 新規加入の審査基準"):
            st.markdown("""申請一覧を確認し、以下の条件を**すべて**満たす場合のみ承認します。  
            - **炉レベル**: 25以上  
            - **総力**: 3000万以上  
            - **名前**: 初期ネーム以外  
            - **⚠️ IDチェック**: 74始まりに注意！スパイの可能性があるため、承認前に個別メッセージで挨拶を送り、意思疎通（日本語が通じるか等）ができるか慎重に確認する。""")
        with st.expander("2. R3への昇格ステップ"):
            st.markdown("1. 盟主にフレンド申請\n2. 本部周辺へ移転\n3. 名前を「ʕ·ᴥ·ʔᴹᴹᶜ」に変更")

    with tab2:
        st.markdown(manual_data.get("🚩 領土・資源", ""))
        with st.expander("2. パズル用「兵1旗」の運用"):
            st.code("パズル用の旗なので、兵士1・英雄なしでお願いします！一旦送還しますね。")

    with tab3:
        st.markdown(manual_data.get("⚔️ イベント攻略", ""))
        with st.expander("🛡️ キルイベ / 王国ルール"):
            st.code("都市攻撃は「同盟未加入」を3回確認してから！")

# --- 2. 管理者画面 ---
def admin_page():
    st.title("🛠️ 管理者：マニュアル編集")
    manual_data = load_manual()

    # セクション選択
    section = st.selectbox("編集する項目", list(manual_data.keys()))
    
    # 編集エリア
    new_content = st.text_area("本文を編集（Markdown形式）", 
                               value=manual_data[section], 
                               height=400)

    if st.button("マニュアルを保存する✨"):
        manual_data[section] = new_content
        save_manual(manual_data)
        st.success("保存したよ！閲覧画面を確認してね😊")
        st.rerun()

    # 履歴復元
    st.divider()
    st.subheader("🕒 過去の状態に戻す")
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "*.json")), reverse=True)
    if backups:
        selected_backup = st.selectbox("バックアップ選択", backups)
        if st.button("この版を復元"):
            with open(selected_backup, 'r', encoding='utf-8') as f:
                restored = json.load(f)
            save_manual(restored)
            st.success("復元しました！")
            st.rerun()

# --- メインメニュー制御 ---
st.sidebar.title("ʕ·ᴥ·ʔ MMC Menu")
menu = st.sidebar.radio("メニュー", ["マニュアル閲覧📜", "管理者設定🛠️"])

if menu == "マニュアル閲覧📜":
    manual_view_page()
elif menu == "管理者設定🛠️":
    admin_page()
