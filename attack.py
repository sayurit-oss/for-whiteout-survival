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

# データ解析関数
def parse_input(text):
    data = {}
    if not text: return data
    for line in text.strip().split('\n'):
        try:
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
            h_list = [f"{i:02d}" for i in range(24)]
            selected_h = st.selectbox("時", h_list, index=now.hour)
        with col_m:
            m_list = [f"{i:02d}" for i in range(60)]
            default_m_idx = (now.minute + 5) % 60
            selected_m = st.selectbox("分", m_list, index=default_m_idx)

        # --- 計算ボタン ---
        if st.button("🚀 計算してコピー用を作成", use_container_width=True, type="primary"):
            try:
                base_rally_start_dt = datetime.now().replace(
                    hour=int(selected_h), minute=int(selected_m), second=0, microsecond=0
                )
                base_departure_dt = base_rally_start_dt + timedelta(minutes=rally_wait_min)
                target_impact_dt = base_departure_dt + timedelta(seconds=all_members_data[longest_name])
                
                # --- (5) 結果作成 ---
                st.success(f"目標着弾予定：{target_impact_dt.strftime('%H:%M:%S')}")
                
                result_text = f"【SVS同時着弾指示】\n"
                result_text += f"目標着弾: {target_impact_dt.strftime('%H:%M:%S')}\n"
                result_text += "--------------------------\n"
                
                sorted_selected = sorted(selected_names, key=lambda x: all_members_data[x], reverse=True)
                
                for name in sorted_selected:
                    travel_sec = all_members_data[name]
                    departure_dt = target_impact_dt - timedelta(seconds=travel_sec)
                    rally_start_dt = departure_dt - timedelta(minutes=rally_wait_min)
                    
                    m_s = f"{all_members_data[name]//60}:{all_members_data[name]%60:02d}"
                    result_text += f"●{name} ({m_s})\n"
                    result_text += f"
