import streamlit as st
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(page_title="ホワサバ敵襲着弾計算", layout="wide")
st.title("🛡️ ホワサバ 敵部隊 到達時刻計算（着弾順ソート版）")

# ====================================================================
# ステップ1: 敵の名前と到達時間（行軍時間）の入力
# ====================================================================
st.header("1. 敵プレイヤー名と到達時間（秒）の入力")
st.caption("名前と到達時間（秒）を入力してください。空欄の行は無視されます。")

# セッション状態の初期化
if "input_rows" not in st.session_state:
    st.session_state.input_rows = [
        {"name": "敵A", "time": 40},
        {"name": "敵B", "time": 20},
        {"name": "敵C", "time": 35},
        {"name": "敵D", "time": 50},
    ]

# チェックした順番を記録するためのリスト
if "click_order" not in st.session_state:
    st.session_state.click_order = []

# 行を追加するボタン
if st.button("➕ 入力欄を増やす"):
    st.session_state.input_rows.append({"name": "", "time": 0})

enemy_travel_times = {}
for i, row in enumerate(st.session_state.input_rows):
    col_name, col_sec = st.columns([3, 2])
    with col_name:
        name_val = st.text_input(f"敵の名前 {i+1}", value=row["name"], key=f"name_input_{i}")
    with col_sec:
        time_val = st.number_input(f"到達時間(秒) {i+1}", min_value=0, max_value=600, value=row["time"], key=f"time_input_{i}")
    
    if name_val.strip():
        enemy_travel_times[name_val.strip()] = time_val

if not enemy_travel_times:
    st.warning("敵の名前を1人以上入力してください。")
    st.stop()

# ====================================================================
# ステップ2: こちらに向かってきている敵を選択する（チェックボックス・順番記憶）
# ====================================================================
st.header("2. 進軍中の敵プレイヤーを選択 【⚠️集結が短い順にチェックしてください】")
st.caption("ここでチェックを入れた順番の、一番最初の人が自動的に「基準（一番集結が短い人）」になります。")

current_selected = []
cb_cols = st.columns(min(len(enemy_travel_times), 5))

for i, enemy_name in enumerate(enemy_travel_times.keys()):
    with cb_cols[i % 5]:
        # チェック状態を監視
        is_checked = st.checkbox(enemy_name, key=f"check_{enemy_name}")
        if is_checked:
            current_selected.append(enemy_name)

# チェックの追加・削除を検知してクリック順リストを更新
for name in current_selected:
    if name not in st.session_state.click_order:
        st.session_state.click_order.append(name)

# チェックが外された名前はクリック順から削除
st.session_state.click_order = [name for name in st.session_state.click_order if name in current_selected]

# 実際に有効な選択順
ordered_enemies = st.session_state.click_order

if not ordered_enemies:
    st.warning("敵を1人以上選択してください。")
    st.stop()

# 現在の選択順を分かりやすく画面に表示
st.info(f" 選択された順（＝集結が早い順）: {' ➔ '.join(ordered_enemies)}")

# 基準となる敵（一番最初にチェックを入れた人）
base_enemy = ordered_enemies[0]

# ====================================================================
# ステップ3: 基準に対して、他の敵がどのくらいズレているか
# ====================================================================
st.header(f"3. 時間差の入力（基準: {base_enemy}）")
st.caption(f"一番集結が早い 【{base_enemy}】 に対して、他の敵の集結残り時間が何秒遅れているかを入力してください。")

time_offsets = {}
time_offsets[base_enemy] = 0

for enemy_name in ordered_enemies[1:]:
    offset = st.number_input(
        f"⏱️ {enemy_name} の時間差 （{base_enemy} より何秒遅れて集結完了するか）",
        min_value=0,
        max_value=600,
        value=0,
        key=f"offset_{enemy_name}"
    )
    time_offsets[enemy_name] = offset

# ====================================================================
# ステップ4: 現在時刻と、基準の残り集結時間の入力
# ====================================================================
st.header(f"4. 現在時刻と 【{base_enemy}】 の残り集結時間")

col_time1, col_time2 = st.columns(2)

with col_time1:
    st.subheader("現在時刻")
    now_time = datetime.now()
    current_time_str = st.text_input("現在時刻 (HH:MM:SS)", value=now_time.strftime("%H:%M:%S"))
    try:
        parsed_current_time = datetime.strptime(current_time_str, "%H:%M:%S")
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
    st.subheader(f"【{base_enemy}】の残り集結時間")
    base_min = st.number_input(f"{base_enemy} の残り（分）", min_value=0, max_value=60, value=3)
    base_sec = st.number_input(f"{base_enemy} の残り（秒）", min_value=0, max_value=59, value=0)
    base_remaining_total_seconds = (base_min * 60) + base_sec

# ====================================================================
# ステップ5: 到達時間（着弾時刻）の計算とソート
# ====================================================================
calc_results = []

for enemy_name in ordered_enemies:
    travel = enemy_travel_times[enemy_name]
    offset = time_offsets[enemy_name]
    actual_remaining_seconds = base_remaining_total_seconds + offset
    departure_time = base_datetime + timedelta(seconds=actual_remaining_seconds)
    arrival_time = departure_time + timedelta(seconds=travel)
    
    calc_results.append({
        "name": enemy_name,
        "travel": travel,
        "departure": departure_time,
        "arrival": arrival_time,
        "remaining": actual_remaining_seconds
    })

# 💡【重要】実際にこちらに到達する時刻（arrival）が早い順に並び替える！
calc_results_sorted = sorted(calc_results, key=lambda x: x["arrival"])

# ====================================================================
# ステップ6: チャット用出力テキスト（到達が早い順）
# ====================================================================
st.markdown("---")
st.header("🎯 チャット用出力テキスト（到達時刻が速い順）")
st.caption("実際に自領地（目的地）に着弾するのが早い順に並んでいます。右上のアイコンからコピーしてください。")

# 到達が早い順にチャットテキストを組み立てる
chat_text = "【到達時間】\n"
for res in calc_results_sorted:
    chat_text += f"{res['name']} : {res['arrival'].strftime('%H時%M分%S秒')}\n"

st.text_area("コピペ用（着弾順）", value=chat_text, height=150)

# 詳細確認用テーブル
st.subheader("📊 詳細確認用データ（着弾順）")
result_table_data = []
for res in calc_results_sorted:
    result_table_data.append({
        "敵部隊": res["name"],
        "到達時間（行軍）": f"{res['travel']}秒",
        "🚀 出発（発射）予定": res["departure"].strftime("%H:%M:%S"),
        "🎯 こちらへの到達時刻": res["arrival"].strftime("%H:%M:%S")
    })
st.table(result_table_data)
