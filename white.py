import streamlit as st
from datetime import datetime, timedelta

# スマホ向け設定
st.set_page_config(page_title="ホワサバSVS計算機", layout="centered")

st.title("🏹 SVS着弾合わせ・差し込み")
st.caption("全ての項目を入力後、一番下の「計算する」をタップしてください")

# --- 名簿設定 ---
with st.expander("👤 味方と敵の名簿を設定する", expanded=True):
    st.write("形式：名前[スペース]分:秒　※スペースは半角、全角どちらでも！") 
    ally_input = st.text_area("味方の行軍時間", height=120, placeholder="りんご 2:30\nみかん 1:45", key="ally_list")
    enemy_input = st.text_area("敵候補の行軍時間", height=120, placeholder="にく 1:20\nさかな 2:00", key="enemy_list")

# データ解析関数
def parse_input(text):
    data = {}
    if not text: return data
    for line in text.strip().split('\n'):
        try:
            parts = line.split()
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

    # --- ターゲット選択 ---
    st.subheader("🎯 敵を選択")
    target_enemy = st.selectbox("攻めてきている敵を選んでください", list(enemy_data.keys()))
    
    # ---時間入力エリア ---
    st.subheader("⏰ 時間の入力")
    
    if 'manual_time' not in st.session_state:
        st.session_state.manual_time = datetime.now().strftime("%H:%M:%S")

    col1, col2 = st.columns(2)
    with col1:
        current_time_input = st.text_input("現在時刻", value=st.session_state.manual_time)
    with col2:
        rally_remain_input = st.text_input("敵の集結残り", value="5:00")

    if st.button("現在時刻を「今」にリセット"):
        st.session_state.manual_time = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    st.write("")

    # --- 計算ボタン ---
    if st.button("🚀 計算する", use_container_width=True, type="primary"):
        try:
            base_time = datetime.strptime(current_time_input, "%H:%M:%S")
            rm, rs = map(int, rally_remain_input.split(':'))
            enemy_travel_time = enemy_data[target_enemy]
            
            # 敵の着弾時刻
            impact_time = base_time + timedelta(minutes=rm, seconds=rs) + timedelta(seconds=enemy_travel_time)
            
            # --- 結果作成 ---
            st.success(f"計算完了！ 敵（{target_enemy}）着弾予定：{impact_time.strftime('%H:%M:%S')}")
            
            result_text = f"【SVS差し込み指示：標的 {target_enemy}】\n"
            result_text += f"敵着弾予定時刻: {impact_time.strftime('%H:%M:%S')}\n"
            result_text += "------------------\n"
            
            for name, travel_sec in ally_data.items():
                departure_time = impact_time - timedelta(seconds=travel_sec)
                result_text += f"● {name}：{departure_time.strftime('%H:%M:%S')} スタート\n"
            
            result_text += "------------------\n"
            result_text += "※この時刻にボタンを押してください"

            # --- 結果の表示とコピー枠 ---
            st.write("▼ 以下の枠内をタップしてコピーしてください")
            # st.codeを使うと、枠の右上に標準のコピーボタンが表示されます
            st.code(result_text, language="text")
            
            st.info("↑ 枠の右上のアイコンをタップするとクリップボードにコピーされます。")
            
        except ValueError:
            st.error("入力形式（HH:mm:ss や 分:秒）が正しくありません。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
else:
    st.warning("まずは「名簿を設定する」を開いて、味方と敵の時間を入力してください。")
