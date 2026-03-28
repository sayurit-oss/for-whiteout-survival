import streamlit as st

# スマホ向け設定
st.set_page_config(page_title="ホワサバ秒読み差し込み", layout="centered")

st.title("🛡️ SVS秒読み差し込み（V2）")
st.caption("敵の残りカウントダウンに合わせて「あと〇秒でスタート」を表示します")

# --- (1) 味方 & (2) 敵の名簿設定 ---
with st.expander("👤 初期設定：味方と敵の行軍時間", expanded=True):
    st.write("形式：名前[スペース]分:秒 数字ところんは半角、スペースは半角・全角どちらでもOK！")
    ally_input = st.text_area("（1）味方の行軍時間", height=120, placeholder="りんご 2:30\nみかん 1:45")
    enemy_input = st.text_area("（2）敵候補の行軍時間", height=120, placeholder="にく 1:20\nさかな 2:00")

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

ally_data = parse_input(ally_input)
enemy_data = parse_input(enemy_input)

if ally_data and enemy_data:
    st.divider()

    # --- (3) ターゲット選択 ---
    st.subheader("🎯 敵の選択")
    target_enemy = st.selectbox("攻めてきている敵を選択", list(enemy_data.keys()))
    enemy_