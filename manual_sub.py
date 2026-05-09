import streamlit as st
import json
import os

# --- ファイル設定 ---
MANUAL_FILE = 'manual_flexible_structure.json'

def load_manual_data():
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 初期データ構造
    return {
        "👥 メンバー管理": [],
        "🚩 領土・資源": [],
        "⚔️ イベント攻略": []
    }

def save_manual_data(data):
    with open(MANUAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 1. マニュアル閲覧画面 ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    data = load_manual_data()

    tabs = st.tabs(list(data.keys()))

    for i, (category, expanders) in enumerate(data.items()):
        with tabs[i]:
            for exp in expanders:
                with st.expander(exp['title']):
                    # 折り畳みの中にある各ブロックを順番に表示
                    for block in exp.get('blocks', []):
                        if block['type'] == 'text':
                            st.markdown(block['content'])
                        elif block['type'] == 'code':
                            st.code(block['content'], language=None)

# --- 2. 管理者画面 ---
def admin_page():
    st.title("🛠️ マニュアル高度編集モード")
    data = load_manual_data()

    category = st.selectbox("編集するカテゴリ", list(data.keys()))
    
    # 1. 折り畳み（Expander）自体の管理
    expanders = data[category]
    
    for e_idx, exp in enumerate(expanders):
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                exp['title'] = st.text_input(f"折り畳みのタイトル", value=exp['title'], key=f"et_{category}_{e_idx}")
            with col2:
                if st.button("🗑️ この折り畳みごと削除", key=f"edel_{category}_{e_idx}"):
                    expanders.pop(e_idx)
                    save_manual_data(data)
                    st.rerun()

            # --- 折り畳みの中身（ブロック）の編集 ---
            st.write("📖 中身の構成パーツ")
            for b_idx, block in enumerate(exp.get('blocks', [])):
                col_type, col_content, col_btn = st.columns([1, 4, 1])
                with col_type:
                    block['type'] = st.selectbox("種類", ["text", "code"], 
                                                 index=0 if block['type'] == 'text' else 1,
                                                 key=f"bt_{category}_{e_idx}_{b_idx}")
                with col_content:
                    label = "文章を入力" if block['type'] == 'text' else "コピペ用文章を入力"
                    block['content'] = st.text_area(label, value=block['content'], 
                                                    key=f"bc_{category}_{e_idx}_{b_idx}", height=100)
                with col_btn:
                    if st.button("❌", key=f"bdel_{category}_{e_idx}_{b_idx}"):
                        exp['blocks'].pop(b_idx)
                        save_manual_data(data)
                        st.rerun()
            
            if st.button("➕ パーツを追加（文章 or コピペ）", key=f"badd_{category}_{e_idx}"):
                if 'blocks' not in exp: exp['blocks'] = []
                exp['blocks'].append({"type": "text", "content": ""})
                save_manual_data(data)
                st.rerun()

    st.divider()
    if st.button("✨ 新しい折り畳みを追加"):
        expanders.append({"title": "新規見出し", "blocks": [{"type": "text", "content": ""}]})
        save_manual_data(data)
        st.rerun()

    if st.button("💾 すべてを保存して反映"):
        save_manual_data(data)
        st.success("最新の状態に更新しました！")

# --- メインメニュー ---
menu = st.sidebar.radio("メニュー", ["マニュアル閲覧📜", "管理者設定🛠️"])
if menu == "マニュアル閲覧📜":
    manual_view_page()
else:
    admin_page()
