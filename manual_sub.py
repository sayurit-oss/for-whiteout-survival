import streamlit as st
import json
import os

# --- 1. データの読み書き設定 ---
CONFIG_FILE = 'manual_custom_data.json'

def load_data():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"👥 メンバー管理": [], "🚩 領土・資源": [], "⚔️ イベント攻略": []}

def save_data(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. マニュアル閲覧画面 ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")
    
    data = load_data()
    tabs = st.tabs(list(data.keys()))

    for i, (category, expanders) in enumerate(data.items()):
        with tabs[i]:
            # 管理画面で追加したexpanderを順番に表示
            for exp in expanders:
                with st.expander(exp['title']):
                    for block in exp.get('blocks', []):
                        if block['type'] == 'text':
                            st.markdown(block['content'])
                        elif block['type'] == 'code':
                            st.code(block['content'], language=None)

# --- 3. 管理者画面 ---
def admin_page():
    st.title("🛠️ マニュアル構造の編集")
    data = load_data()

    category = st.selectbox("編集するカテゴリを選んでね", list(data.keys()))
    expanders = data[category]
    
    # 折り畳みの編集・追加
    for e_idx, exp in enumerate(expanders):
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                exp['title'] = st.text_input(f"折り畳みのタイトル", value=exp['title'], key=f"title_{category}_{e_idx}")
            with col2:
                if st.button("🗑️ 削除", key=f"del_exp_{category}_{e_idx}"):
                    expanders.pop(e_idx)
                    save_data(data)
                    st.rerun()

            # パーツ（text/code）の編集
            for b_idx, block in enumerate(exp.get('blocks', [])):
                c1, c2, c3 = st.columns([1, 4, 0.5])
                with c1:
                    block['type'] = st.selectbox("種類", ["text", "code"], 
                                                 index=0 if block['type'] == 'text' else 1,
                                                 key=f"type_{category}_{e_idx}_{b_idx}")
                with c2:
                    block['content'] = st.text_area("内容", value=block['content'], 
                                                    key=f"content_{category}_{e_idx}_{b_idx}", height=100)
                with c3:
                    if st.button("❌", key=f"del_block_{category}_{e_idx}_{b_idx}"):
                        exp['blocks'].pop(b_idx)
                        save_data(data)
                        st.rerun()
            
            if st.button("➕ パーツを追加 (text/code)", key=f"add_block_{category}_{e_idx}"):
                exp['blocks'].append({"type": "text", "content": ""})
                save_data(data)
                st.rerun()

    st.divider()
    if st.button("✨ 新しい折り畳み(expander)を追加"):
        expanders.append({"title": "新しい見出し", "blocks": [{"type": "text", "content": ""}]})
        save_data(data)
        st.rerun()

    if st.button("💾 すべて保存してバックアップを表示"):
        save_data(data)
        st.success("一時保存完了！")
        with st.expander("📥 GitHub保存用データ（ここをコピーしてファイルに保存してね）"):
            st.code(json.dumps(data, ensure_ascii=False, indent=4), language="json")

# --- メインメニュー ---
st.sidebar.title("ʕ·ᴥ·ʔ MMC Menu")
menu = st.sidebar.radio("メニュー", ["マニュアル閲覧📜", "管理者設定🛠️"])

if menu == "マニュアル閲覧📜":
    manual_view_page()
else:
    admin_page()
