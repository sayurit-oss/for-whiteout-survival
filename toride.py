import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="要塞・砦 行軍時間シミュレーター", layout="wide")

# ==========================================
# 1. 基礎データ・座標設定
# ==========================================
HQ_NAME = "本部"
HQ_COORD = (732, 418)

BASE_FORTRESS_NAME = "要塞1号"
BASE_FORTRESS_COORD = (597, 800)
BASE_SECONDS = 600.0  # 本部 -> 要塞1号 の所要時間 (600秒)

# 1座標あたりの所要秒数 (速度係数)
base_dist = math.sqrt((BASE_FORTRESS_COORD[0] - HQ_COORD[0])**2 + (BASE_FORTRESS_COORD[1] - HQ_COORD[1])**2)
SEC_PER_UNIT = BASE_SECONDS / base_dist

# 全拠点座標マスター
LOCATIONS = {
    "要塞1号": (597, 800),
    "要塞2号": (400, 597),
    "要塞3号": (597, 400),
    "要塞4号": (800, 597),
    "砦1号": (237, 828),
    "砦2号": (237, 606),
    "砦3号": (237, 348),
    "砦4号": (366, 237),
    "砦5号": (588, 237),
    "砦6号": (846, 237),
    "砦7号": (957, 348),
    "砦8号": (957, 606),
    "砦9号": (957, 828),
    "砦10号": (846, 957),
    "砦11号": (606, 957),
    "砦12号": (366, 957),
}

# 距離＆所要時間計算関数
def get_travel_time(p1_coord, p2_coord):
    dist = math.sqrt((p2_coord[0] - p1_coord[0])**2 + (p2_coord[1] - p1_coord[1])**2)
    sec = dist * SEC_PER_UNIT
    # 分単位で四捨五入（切り上げ/丸め）
    minutes = round(sec / 60)
    return minutes, sec

# ==========================================
# 2. UI 画面構成
# ==========================================
st.title("⚔️ 要塞・砦 攻略検討シミュレーター")
st.caption(f"基準速度: 本部 {HQ_COORD} → 要塞1号 {BASE_FORTRESS_COORD} = 10分00秒 (1単位あたり約{SEC_PER_UNIT:.2f}秒)")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("1. 確定枠（要塞1箇所 ＋ 砦1箇所）")
    
    # 確定要塞
    f_cols = st.columns([2, 2, 2])
    with f_cols[0]:
        selected_fortress = st.selectbox("確定要塞", ["要塞1号", "要塞2号", "要塞3号", "要塞4号"], index=2)
    with f_cols[1]:
        fortress_reward = st.text_input("要塞 報酬", value="ペット突破")
    with f_cols[2]:
        fortress_alliance = st.text_input("前回取得同盟(要塞)", value="KRr")
        
    # 確定砦
    t_cols = st.columns([2, 2, 2])
    all_forts = [f"砦{i}号" for i in range(1, 13)]
    with t_cols[0]:
        selected_fixed_fort = st.selectbox("確定砦（前回取得など）", all_forts, index=4)
    with t_cols[1]:
        fixed_fort_reward = st.text_input("砦 報酬", value="武器経験値")
    with t_cols[2]:
        fixed_fort_alliance = st.text_input("前回取得同盟(砦)", value="MMC")

    st.markdown("---")
    st.subheader("2. 検討枠（残り砦の候補 3箇所）")
    
    candidate_reward_theme = st.text_input("検討対象の報酬ジャンル", value="1h加速")
    
    # 候補砦3つの入力
    default_candidates = ["砦2号", "砦6号", "砦10号"]
    default_alliances = ["JFW", "wan", "Ris"]
    
    candidate_data = []
    for i in range(3):
        c_cols = st.columns([2, 2])
        with c_cols[0]:
            c_name = st.selectbox(f"候補砦 {i+1}", all_forts, index=all_forts.index(default_candidates[i]), key=f"c_name_{i}")
        with c_cols[1]:
            c_ally = st.text_input(f"前回取得同盟 ({c_name})", value=default_alliances[i], key=f"c_ally_{i}")
        candidate_data.append({"name": c_name, "alliance": c_ally})

# ==========================================
# 3. 計算と出力生成
# ==========================================
fortress_coord = LOCATIONS[selected_fortress]
fixed_fort_coord = LOCATIONS[selected_fixed_fort]

# テキスト生成
output_lines = []
output_lines.append("【確定】")
output_lines.append(f"{selected_fortress}：{fortress_reward}({fortress_alliance})")
output_lines.append(f"{selected_fixed_fort}：{fixed_fort_reward}({fixed_fort_alliance})")
output_lines.append("")
output_lines.append("【要検討】")
output_lines.append(candidate_reward_theme)

table_rows = []

for c in candidate_data:
    c_coord = LOCATIONS[c["name"]]
    
    # 時間計算 (分)
    t_hq, _ = get_travel_time(HQ_COORD, c_coord)
    t_fixed, _ = get_travel_time(fixed_fort_coord, c_coord)
    t_fortress, _ = get_travel_time(fortress_coord, c_coord)
    
    # 砦名表記（「号」または「砦X号」に合わせて整頓）
    c_label = c["name"].replace("砦", "") # "2号" などにする場合
    
    line = f"{c_label}({t_hq}分)({t_fixed}分)({t_fortress}分)({c['alliance']})"
    output_lines.append(line)
    
    table_rows.append({
        "候補": c["name"],
        f"本部から": f"{t_hq}分",
        f"{selected_fixed_fort}から": f"{t_fixed}分",
        f"{selected_fortress}から": f"{t_fortress}分",
        "前回取得同盟": c["alliance"]
    })

output_lines.append("")
output_lines.append("(本部からの時間)")
output_lines.append(f"({selected_fixed_fort}からの時間)")
output_lines.append(f"({selected_fortress}からの時間)")
output_lines.append("(前回取得同盟)")

final_text = "\n".join(output_lines)

with col_right:
    st.subheader("3. 比較テーブル")
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
    
    st.subheader("4. 共有用出力テキスト")
    st.text_area("そのままコピーしてチャットやDiscord等に貼り付けできます", value=final_text, height=330)
