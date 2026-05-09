import streamlit as st
import json
import os

# --- ファイル設定 ---
MANUAL_FILE = 'manual_structure.json'

def load_manual_data():
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 初期データ（ファイルがない時用）
    return {
        "👥 メンバー管理": [{"title": "1. 新規加入の審査基準", "content": "ここに内容を書く"}],
        "🚩 領土・資源": [{"title": "1. ルート作成", "content": "ここに内容を書く"}],
        "⚔️ イベント攻略": [{"title": "1. 熊狩り", "content": "ここに内容を書く"}]
    }

def save_manual_data(data):
    with open(MANUAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 1. マニュアル閲覧画面 ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    data = load_manual_data()

    # タブは固定
    tabs = st.tabs(list(data.keys()))

    for i, (category, items) in enumerate(data.items()):
        with tabs[i]:
            for item in items:
                # 登録されている数だけ自動でexpander（折り畳み）を作成
                with st.expander(item['title']):
                    # 内容が「コピペ用」っぽければ自動でst.codeにする判定も可能ですが、
                    # 基本はmarkdownで表示。コードを書きたい場合は管理画面で工夫。
                    st.markdown(item['content'])

# --- 2. 管理者画面（ここが重要！） ---
def admin_page():
    st.title("🛠️ マニュアル構造の編集")
    data = load_manual_data()

    category = st.selectbox("編集するカテゴリ", list(data.keys()))
    
    st.subheader(f"「{category}」内の折り畳み一覧")
    
    items = data[category]
    new_items = []

    # 既存の折り畳みをループで表示して編集
    for i, item in enumerate(items):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                t = st.text_input(f"タイトル {i+1}", value=item['title'], key=f"t_{category}_{i}")
                c = st.text_area(f"本文 {i+1}", value=item['content'], key=f"c_{category}_{i}", height=200)
            with col2:
                # 削除ボタン
                delete = st.checkbox("削除する", key=f"d_{category}_{i}")
            
            if not delete:
                new_items.append({"title": t, "content": c})

    # 新しい折り畳みの追加
    if st.button("➕ 新しい折り畳みを追加"):
        new_items.append({"title": "新しい見出し", "content": "ここに本文を入力"})
        data[category] = new_items
        save_manual_data(data)
        st.rerun()

    if st.button("💾 全ての変更を保存する"):
        data[category] = new_items
        save_manual_data(data)
        st.success("マニュアルを更新しました！")
        st.rerun()

# --- メイン制御 ---
menu = st.sidebar.radio("メニュー", ["マニュアル閲覧📜", "管理者設定🛠️"])
if menu == "マニュアル閲覧📜":
    manual_view_page()
else:
    admin_page()
