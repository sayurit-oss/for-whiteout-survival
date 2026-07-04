import streamlit as st
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(page_title="ホワサバ敵襲着弾計算", layout="wide")
st.title("🛡️ ホワサバ 敵部隊 到達時刻計算（チャットコピペ対応）")

# ====================================================================
# ステップ1: 敵の名前と到達時間（行軍時間）の入力
# ====================================================================
st.header("1. 敵プレイヤー名と到達時間（秒）の入力")
st.caption("名前と到達時間（秒）を入力してください。空欄の行は無視されます。")

# 入力行を動的に管理するための初期データ（例として4行用意、足りなければ増やせます）
if "input_rows" not in st.session_state:
    st.session_state.input_rows = [
        {"name": "敵A", "time": 40},
        {"name": "敵B", "time": 20},
        {"name": "敵C", "time": 35},
        {"name": "敵D", "time": 50},
    ]

# 行を追加するボタン
if st.button("➕ 入力欄を増やす"):
    st.session_state.input_rows.append({"name": "", "time": 0})

# テキストボックスの並びを生成
enemy_travel_times = {}
for i, row in enumerate(st.session_state.input_rows):
    col_name, col_sec = st.columns([3, 2])
    with col_name:
        name_val = st.text_input(f"敵の名前 {i+1}", value=row["name"], key=f"name_input_{i}")
    with col_sec:
        time_val = st.number_input(f"到達時間(秒) {i+1}", min_value=0, max_value=600, value=row["time"], key=f"time_input_{i}")
    
    # 名前が入力されている場合のみ有効なデータとして扱う
    if name_val.strip():
        enemy_travel_times[name_val.strip()] = time_val

if not enemy_travel_times:
    st.warning("敵の名前を1人以上入力してください。")
    st.stop()

# ====================================================================
# ステップ2: こちらに向かってきている敵を選択する（チェックボックス）
# ====================================================================
st.header("2. 進軍中の敵プレイヤーを選択")
selected_enemies = []
st.write("今回こちらに向かってきている敵にチェックを入れてください：")

cb_cols = st.columns(min(len(enemy_travel_times), 5)) # 最大5列で並べる
for i, enemy_name in enumerate(enemy_travel_times.keys()):
    with cb_cols[i % 5]:
        # デフォルトで入力されているものはチェックを入れておく
        if st.checkbox(enemy_name, value=True, key=f"check_{enemy_name}"):
            selected_enemies.append(enemy_name)

if not selected_enemies:
    st.warning("敵を1人以上選択してください。")
    st.stop()

# ====================================================================
# ステップ3: 集結時間の残り少ない（早い）順に並び替えるスペース
# ====================================================================
st.header("3. 集結残り時間の短い順に並び替え")
st.caption("集結残り時間が短い順（＝早く出発する順）に、上からカチカチと並び替えてください。")

ordered_enemies = st.multiselect(
    "選択した敵を【集結が早い順】に指定してください（例：敵D ➔ 敵A ➔ 敵B）",
    options=selected_enemies,
    default=selected_enemies # 初期状態では選択された順
)

if len(ordered_enemies) != len(selected_enemies):
    st.info("⚠️ 選択した敵がすべて並び替えリストに含まれるように選択してください。")
    st.stop()

# 基準となる敵（一番集結残り時間が短い人＝リストの先頭）
base_enemy = ordered_enemies[0]

# ====================================================================
# ステップ4: 基準に対して、他の敵がどのくらいズレているか
# ====================================================================
st.header(f"4. 時間差の入力（基準: {base_enemy}）")
st.caption(f"一番集結が早い 【{base_enemy}】 に対して、他の敵の集結残り時間が何秒遅れているかを入力してください。")

time_offsets = {}
time_offsets[base_enemy] = 0  # 基準は0秒

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
# ステップ5: 現在時刻と、基準の残り集結時間の入力
# ====================================================================
st.header(f"5. 現在時刻と 【{base_enemy}】 の残り集結時間")

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
# ステップ6: 到達時間（着弾時刻）出力
# ====================================================================
st.markdown("---")
st.header("🎯 チャット用出力テキスト")
st.caption("下の枠内のテキストをコピーして、ゲーム内チャットやDiscordに貼り付けてください。")

# チャット用テキストの生成
chat_text = "【到達時間】\n"

for enemy_name in ordered_enemies:
    travel = enemy_travel_times[enemy_name]
    offset = time_offsets[enemy_name]
    actual_remaining_seconds = base_remaining_total_seconds + offset
    departure_time = base_datetime + timedelta(seconds=actual_remaining_seconds)
    arrival_time = departure_time + timedelta(seconds=travel)
    
    # テキスト行を追加
    chat_text += f"{enemy_name} : {arrival_time.strftime('%H時%M分%S秒')}\n"

# Streamlitのテキストエリア（ここから直接コピーできる）
st.text_area("コピペ用（右上のアイコンから一発コピーできます）", value=chat_text, height=150)

# 念のため、視認性の高いテーブルも下に残しておきます
st.subheader("📊 詳細確認用データ")
result_data = []
for enemy_name in ordered_enemies:
    travel = enemy_travel_times[enemy_name]
    offset = time_offsets[enemy_name]
    actual_remaining_seconds = base_remaining_total_seconds + offset
    departure_time = base_datetime + timedelta(seconds=actual_remaining_seconds)
    arrival_time = departure_time + timedelta(seconds=travel)
    
    result_data.append({
        "敵部隊": enemy_name,
        "到達時間（行軍）": f"{travel}秒",
        "🚀 出発（発射）予定": departure_time.strftime("%H:%M:%S"),
        "🎯 こちらへの到達時刻": arrival_time.strftime("%H:%M:%S")
    })
st.table(result_data)
