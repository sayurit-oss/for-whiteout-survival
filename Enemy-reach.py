import streamlit as st
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(page_title="ホワサバ敵襲着弾計算", layout="wide")
st.title("🛡️ ホワサバ 敵部隊 到達・着弾時刻計算ツール")

# ====================================================================
# ステップ1: 敵の到達時間（行軍時間）をその場で入力するスペース
# ====================================================================
st.header("1. 敵の到達時間（行軍時間）の入力")
st.caption("例）A: 40秒、B: 20秒、C: 35秒、D: 50秒 など、画面やレポートで確認した時間を入力してください。")

all_enemies = ["A", "B", "C", "D", "E"]
enemy_travel_times = {}

cols = st.columns(len(all_enemies))
for i, enemy_name in enumerate(all_enemies):
    with cols[i]:
        # 初期値としてご提示の例（A:40, B:20, C:35, D:50）をセット
        default_val = 40 if enemy_name == "A" else 20 if enemy_name == "B" else 35 if enemy_name == "C" else 50 if enemy_name == "D" else 30
        enemy_travel_times[enemy_name] = st.number_input(
            f"敵 {enemy_name} の到達時間 (秒)", 
            min_value=0, 
            max_value=600, 
            value=default_val,
            key=f"travel_{enemy_name}"
        )

# ====================================================================
# ステップ2: こちらに向かってきている敵を選択する（チェックボックス）
# ====================================================================
st.header("2. 進軍中の敵プレイヤーを選択")
selected_enemies = []
st.write("今回こちらに向かってきている敵にチェックを入れてください：")

cb_cols = st.columns(len(all_enemies))
for i, enemy_name in enumerate(all_enemies):
    with cb_cols[i]:
        # 初期値として A, B, D をオンにする
        default_check = enemy_name in ["A", "B", "D"]
        if st.checkbox(f"敵 {enemy_name}", value=default_check, key=f"check_{enemy_name}"):
            selected_enemies.append(enemy_name)

if not selected_enemies:
    st.warning("敵を1人以上選択してください。")
    st.stop()

# ====================================================================
# ステップ3: 集結時間の残り少ない（早い）順に並び替えるスペース
# ====================================================================
st.header("3. 集結残り時間の短い順に並び替え")
st.caption("集結残り時間が短い順（＝早く出発する順）に、上から並び替えてください。")

# 選択された敵を並び替えるための選択ボックス（複数指定）
# 初期値をご提示の「D, A, B」の順になるように調整
ordered_enemies = st.multiselect(
    "選択した敵を【集結が早い順（D ➔ A ➔ B など）】に指定してください",
    options=selected_enemies,
    default=[e for e in ["D", "A", "B"] if e in selected_enemies]
)

if len(ordered_enemies) != len(selected_enemies):
    st.info("⚠️ 選択した敵がすべて並び替えリストに含まれるように選択してください。")
    st.stop()

# 基準となる敵（一番集結残り時間が短い人＝リストの先頭）
base_enemy = ordered_enemies[0]

# ====================================================================
# ステップ4: 基準（D）に対して、他の敵（A, B）がどのくらいズレているか
# ====================================================================
st.header(f"4. 時間差の入力（基準: 敵 {base_enemy}）")
st.caption(f"一番集結が早い 敵 {base_enemy} に対して、他の敵の集結残り時間が【何秒長い（遅い）か】を入力してください。")

time_offsets = {}
time_offsets[base_enemy] = 0  # 基準は0秒

for enemy_name in ordered_enemies[1:]:
    # 初期値としてご提示の例（A:1秒、B:4秒）をセット
    default_offset = 1 if enemy_name == "A" else 4 if enemy_name == "B" else 0
    
    offset = st.number_input(
        f"⏱️ 敵 {enemy_name} の時間差 （敵 {base_enemy} より何秒遅れて集結完了するか）",
        min_value=0,
        max_value=600,
        value=default_offset,
        key=f"offset_{enemy_name}"
    )
    time_offsets[enemy_name] = offset

# ====================================================================
# ステップ5: 現在時刻と、基準（D）の残り集結時間の入力
# ====================================================================
st.header(f"5. 現在時刻と 敵 {base_enemy} の残り集結時間")

col_time1, col_time2 = st.columns(2)

with col_time1:
    st.subheader("現在時刻")
    # 入力しやすいように現在のリアルタイムを初期値にする
    now_time = datetime.now()
    current_time_str = st.text_input("現在時刻 (HH:MM:SS)", value=now_time.strftime("%H:%M:%S"))
    try:
        # 入力された文字列を時刻オブジェクトに変換
        parsed_current_time = datetime.strptime(current_time_str, "%H:%M:%S")
        # 日付は今日のものに合わせる
        base_datetime = datetime.now().replace(
            hour=parsed_current_time.hour, 
            minute=parsed_current_time.minute, 
            second=parsed_current_time.second, 
            microsecond=0
        )
    except ValueError:
        st.error("時刻の形式が正しくありません。半角で 13:40:10 のように入力してください。")
        st.stop()

with col_time2:
    st.subheader(f"敵 {base_enemy} の残り集結時間")
    base_min = st.number_input(f"敵 {base_enemy} の残り（分）", min_value=0, max_value=60, value=3)
    base_sec = st.number_input(f"敵 {base_enemy} の残り（秒）", min_value=0, max_value=59, value=0)
    base_remaining_total_seconds = (base_min * 60) + base_sec

# ====================================================================
# ステップ6: 到達時間（着弾時刻）出力
# ====================================================================
st.markdown("---")
st.header("🎯 最終出力：敵部隊 到達時刻一覧")

result_data = []

for enemy_name in ordered_enemies:
    # 1. 敵個別の到達時間（行軍時間）
    travel = enemy_travel_times[enemy_name]
    
    # 2. 基準からの集結のズレ
    offset = time_offsets[enemy_name]
    
    # 3. この敵の現在の集結残り時間 ＝ 基準の残り時間 ＋ ズレ
    actual_remaining_seconds = base_remaining_total_seconds + offset
    
    # 4. 出発時刻 ＝ 現在時刻 ＋ 実際の集結残り時間
    departure_time = base_datetime + timedelta(seconds=actual_remaining_seconds)
    
    # 5. 到達時刻 ＝ 出発時刻 ＋ 到達時間（行軍時間）
    arrival_time = departure_time + timedelta(seconds=travel)
    
    result_data.append({
        "敵部隊": f"敵 {enemy_name}",
        "到達時間（行軍）": f"{travel}秒",
        "集結残り時間": f"{actual_remaining_seconds // 60}分 {actual_remaining_seconds % 60}秒",
        "🚀 出発（発射）予定時刻": departure_time.strftime("%H:%M:%S"),
        "🎯 こちらへの到達時刻": arrival_time.strftime("%H:%M:%S")
    })

# 結果を表示
st.table(result_data)
