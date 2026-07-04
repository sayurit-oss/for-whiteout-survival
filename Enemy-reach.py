import streamlit as st
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(page_title="ホワサバ敵襲アラート", layout="wide")
st.title("🛡️ ホワサバ 敵部隊 到達時刻 計算ツール")

# 1. 敵プレイヤーのマスタデータ（自領地までの固定行軍時間）
# ※普段からマークしている敵や、大体の距離に応じた秒数を登録しておきます。
ENEMY_MASTER = {
    "敵プレイヤーA": 40,
    "敵プレイヤーB": 55,
    "敵プレイヤーC": 30,
    "敵プレイヤーD": 70,
    "敵プレイヤーE": 45,
}

st.sidebar.header("⚙️ 敵の行軍時間マスタ（固定値）")
st.sidebar.write("※敵領地からこちらまでの片道時間")
for name, duration in ENEMY_MASTER.items():
    st.sidebar.text(f"{name}: {duration}秒")

# 2. 進軍してきた敵の選択
st.header("1. 進軍中の敵プレイヤーを選択")
selected_enemies = st.multiselect(
    "こちらに向かってきている敵を選んでください",
    options=list(ENEMY_MASTER.keys()),
    default=list(ENEMY_MASTER.keys())[:3]
)

if not selected_enemies:
    st.warning("敵プレイヤーを1人以上選択してください。")
    st.stop()

# 選択された敵のデータを抽出
active_enemies = []
for name in selected_enemies:
    active_enemies.append({
        "name": name,
        "travel_time": ENEMY_MASTER[name]
    })

# 💡 行軍時間が「短い（近い）順」に並び替える
# 到達が早い敵をベースにした方が、時間差（〇秒後に次の敵が来る、など）を把握しやすいため
active_enemies = sorted(active_enemies, key=lambda x: x["travel_time"])

# 3. 集結残り時間（進軍時間）の入力
st.header("2. 敵の進軍・集結時間の入力")

# 基準となる「一番近い敵」
base_enemy = active_enemies[0]
st.subheader(f"👑 基準となる敵: {base_enemy['name']}")

col1, col2 = st.columns(2)
with col1:
    base_min = st.number_input(f"{base_enemy['name']} の画面上の残り時間（分）", min_value=0, max_value=60, value=5)
with col2:
    base_sec = st.number_input(f"{base_enemy['name']} の画面上の残り時間（秒）", min_value=0, max_value=59, value=0)

base_total_seconds = (base_min * 60) + base_sec

# 他の敵との「時間差」入力スペース
st.markdown("#### 💡 他の敵との時間差（集結・出発のズレ）")
st.caption(f"一番早い {base_enemy['name']} の画面表示を基準として、他の敵のカウントダウンが何秒【遅れているか（猶予があるか）】を入力してください。")

time_offsets = {}
time_offsets[base_enemy['name']] = 0  # 基準は0秒

for enemy in active_enemies[1:]:
    # 基準の敵より、画面上の残り時間が何秒長い（遅れている）かを入力
    offset = st.number_input(
        f"⏱️ {enemy['name']} の時間差 （{base_enemy['name']} より何秒遅れて動いているか）",
        min_value=-600,
        max_value=600,
        value=10,  # デフォルトで10秒差として仮置き
        key=f"offset_{enemy['name']}"
    )
    time_offsets[enemy['name']] = offset

# 4. 到達時刻の計算と表示
st.header("3. 敵部隊の確定 到達時刻一覧")

now = datetime.now()
st.write(f"現在時刻: **{now.strftime('%H:%M:%S')}**")

result_data = []

for enemy in active_enemies:
    name = enemy["name"]
    travel = enemy["travel_time"]
    offset = time_offsets[name]
    
    # この敵の、現時点からの実際の残り時間（画面上の残り時間 ＋ 時間差）
    # ※時間差（offset）を足すことで、全員分の残り時間をリアルタイムに手入力したのと同じ状態を作ります
    actual_remaining_seconds = base_total_seconds + offset
    
    # 敵がこちらに衝突・到達する時刻
    arrival_time = now + timedelta(seconds=actual_remaining_seconds)
    
    result_data.append({
        "敵プレイヤー": name,
        "固定行軍時間": f"{travel}秒",
        "現在の残り時間（画面表示）": f"{actual_remaining_seconds // 60}分 {actual_remaining_seconds % 60}秒",
        "🎯 こちらへの到達時刻": arrival_time.strftime("%H:%M:%S")
    })

# 結果をテーブルで表示
st.table(result_data)

st.error("⚠️ 到達時刻に合わせて、増援の受入れやバリア（平和の盾）の準備を行ってください！")
