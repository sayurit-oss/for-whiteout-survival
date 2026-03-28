import streamlit as st

# スマホ向け設定
st.set_page_config(page_title="ホワサバ秒読み差し込み", layout="centered")

st.title("🛡️ SVS秒読み差し込み（V2）")
st.caption("敵のカウントダウンに合わせて「あと〇秒でスタート」を表示します")

# --- (1) 味方 & (2) 敵の名簿設定 ---
with st.expander("👤 初期設定：味方と敵の行軍時間", expanded=True):
    st.write("形式：名前[スペース]分:秒 数字ところんは半角、スペースは半角・全角どちらでもOK！")
    ally_input = st.text_area("（1）味方の行軍時間", height=120, placeholder="りんご 2:30\nみかん 1:45", key="ally_list")
    enemy_input = st.text_area("（2）敵候補の行軍時間", height=120, placeholder="にく 1:20\nさかな 2:00", key="enemy_list")

# データ解析関数
def parse_input(text):
    data = {}
    if not text: return data
    for line in text.strip().split('\n'):
        try:
            # 全角スペースを半角に置換
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
    enemy_travel_sec = enemy_data[target_enemy]

    # --- (4) 敵の集結設定 ---
    st.subheader("⏱️ 敵の集結設定")
    enemy_rally_min = st.selectbox("敵が選んだ集結時間（分）", [1, 3, 5])

    # --- (5) 到着希望時間の調整 ---
    st.subheader("📐 到着タイミング調整")
    # -5秒(先着) ～ 0秒(同時) ～ 5秒(後着)
    offset = st.selectbox("敵の着弾に対していつ着きたい？", 
                          options=list(range(-5, 6)), 
                          index=6, # 1秒後着をデフォルトにする場合はindex=6
                          format_func=lambda x: f"{x}秒 ({'敵より先' if x<0 else '敵より後' if x>0 else '同時'})")

    st.divider()
    st.subheader("🚀 スタートタイミングの計算")
    
    if st.button("📊 カウントダウン指示を作成", use_container_width=True, type="primary"):
        try:
            result_text = f"【SVS差し込み指示：標的 {target_enemy}】\n"
            result_text += f"調整：敵着弾の {offset}秒後 目標\n"
            result_text += "--------------------------\n"
            result_text += "敵のカウントダウンが以下の時刻になったら【スタート】！\n\n"

            for name, ally_travel_sec in ally_data.items():
                # 味方がスタートすべき「敵の残り時間」を計算
                # 敵の残り時間 ＝ 自分の行軍時間 － 敵の行軍時間 － オフセット
                trigger_sec = ally_travel_sec - enemy_travel_sec - offset
                
                if trigger_sec >= 0:
                    # 集結残り時間で指示
                    m = trigger_sec // 60
                    s = trigger_sec % 60
                    time_str = f"{m}:{s:02d}" if m > 0 else f"{s}秒"
                    result_text += f"●{name}：集結残り【{time_str}】でスタート\n"
                else:
                    # 敵が出発した後の「行軍残り時間」で指示
                    run_trigger = enemy_travel_sec - (ally_travel_sec - offset)
                    m = run_trigger // 60
                    s = run_trigger % 60
                    time_str = f"{m}:{s:02d}" if m > 0 else f"{s}秒"
                    result_text += f"●{name}：敵の行軍残り【{time_str}】でスタート\n"

            result_text += "--------------------------\n"

            # 結果表示
            st.write("▼ 以下の枠内をコピー！")
            st.code(result_text, language="text")
            st.info("右上のアイコンをタップしてコピー完了")
        except Exception as e:
            st.error(f"計算中にエラーが発生しました: {e}")

else:
    st.warning("「初期設定」から味方と敵の情報を入力してください。")
