import streamlit as st
from datetime import datetime, timedelta

# スマホ向け設定
st.set_page_config(page_title="ホワサバ同時攻撃計算機", layout="centered")

st.title("🔥 SVS同時着弾・集結計算機")
st.caption("参加する集結主をチェックし、基準の【集結開始】を選んでください")

# --- (1) 集結主の名簿設定 ---
with st.expander("👤 集結主リストの初期設定", expanded=True):
    st.write("形式：名前[スペース]分:秒 数字ところんは半角、スペースは半角・全角どちらでもOK！")
    all_members_input = st.text_area("集結主候補の全員分を入力", height=150, 
                                   placeholder="りんご 2:30\nみかん 1:45\nぶどう 3:10", key="member_list")

# データ解析関数（全角スペース対応版）
def parse_input(text):
    data = {}
    if not text: return data
    for line in text.strip().split('\n'):
        try:
            # 全角スペースを半角に置換して分割
            parts = line.replace('　', ' ').split()
            if len(parts) < 2: continue
            name = parts[0]
            m, s = map(int, parts[1].split(':'))
            data[name] = m * 60 + s
        except: continue
    return data

all_members_data = parse_input(all_members_input)

if all_members_data:
    st.divider()

    # --- (2) 今回の集結主を選択 ---
    st.subheader("⚔️ 今回の集結主を選択")
    selected_names = []
    cols = st.columns(2) 
    for i, name in enumerate(all_members_data.keys()):
        with cols[i % 2]:
            if st.checkbox(name, key=f"check_{name}"):
                selected_names.append(name)
    
    if selected_names:
        st.divider()
        # --- (3) 集結時間の設定 ---
        st.subheader("⏱️ 集結待ち時間")
        rally_wait_min = st.radio("待ち時間を選択", [1, 3, 5], horizontal=True)
        
        # --- (4) 基準時間の入力（プルダウン形式） ---
        st.subheader("📅 基準（集結開始）の入力")
        
        longest_name = max(selected_names, key=lambda x: all_members_data[x])
        st.info(f"💡 今回の基準（最長）：**{longest_name}**\n({all_members_data[longest_name]//60}分{all_members_data[longest_name]%60}秒)")
        
        st.write(f"**{longest_name}** が【集結開始ボタン】を押す時刻を選んでください。")
        
        # 時・分のプルダウン作成
        now = datetime.now()
        col_h, col_m = st.columns(2)
        with col_h:
