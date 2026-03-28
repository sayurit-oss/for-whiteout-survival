import streamlit as st
from datetime import datetime, timedelta

# スマホ向け設定
st.set_page_config(page_title="ホワサバ同時攻撃計算機", layout="centered")

st.title("🔥 SVS同時着弾・集結計算機")
st.caption("参加する集結主をチェックして、基準時間を入力してください")

# --- (1) 集結主の名簿設定 ---
with st.expander("👤 集結主リストの初期設定", expanded=True):
    st.write("形式：名前[スペース]分:秒 数字ところんは半角、スペースは半角・全角どちらでもOK！")
    all_members_input = st.text_area("集結主候補の全員分を入力", height=150, 
                                   placeholder="りんご 2:30\nみかん 1:45\nめろん 3:10", key="member_list")

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

all_members_data = parse_input(all_members_input)

if all_members_data:
    st.divider()

    # --- (2) 今回の集結主をチェックボックスで選択 ---
    st.subheader("⚔️ 今回の集結主を選択（タップで選択）")
    selected_names = []
    
    # 名簿にある人を横並びや縦並びでチェックボックスにする
    # スマホで見やすいよう、1行に2人ずつ並べるなどの工夫も可能です
    cols = st.columns(2) 
    for i, name in enumerate(all_members_data.keys()):
        with cols[i % 2]: # 2列に分けて表示
            if st.checkbox(name, key=f"check_{name}"):
                selected_names.append(name)
    
    if selected_names:
        st.divider()
        # --- (3) 集結時間の設定 ---
        st.subheader("⏱️ 集結待ち時間")
        rally_wait_min = st.radio("待ち時間を選択", [1, 3, 5], horizontal=True)
        
        # --- (4) 基準時間の入力 ---
        st.subheader("📅 基準時間の入力")
        
        # 一番時間がかかる人を自動特定
        longest_name = max(selected_names, key=lambda x: all_members_data[x])
        st.info(f"💡 今回の基準（最長）：**{longest_name}**\n({all_members_data[longest_name]//60}分{all_members_data[longest_name]%60}秒)")
        
        st.write(f"**{longest_name}** が何時何分に出発するか入力してください。")
        col1, col2 = st.columns(2)
        with col1:
            # デフォルトは現在の10分後などに設定しておくと便利
            default_time = (datetime.now() + timedelta(minutes=10)).strftime("%H:%M")
            base_hour_min = st.text_input("基準者の出発時刻 (時:分)", value=default_time)

        # --- 計算ボタン ---
        if st.button("🚀 計算してコピー用を作成", use_container_width=True, type="primary"):
            try:
                # 計算ロジック
                h, m = map(int, base_hour_min.split(':'))
                base_departure_dt = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
                
                # 共通の目標着弾時刻
                target_impact_dt = base_departure_dt + timedelta(seconds=all_members_data[longest_name])
                
                # --- (5) 結果作成 ---
                st.success(f"目標着弾予定：{target_impact_dt.strftime('%H:%M:%S')}")
                
                result_text = f"【SVS同時着弾指示】\n"
                result_text += f"目標着弾: {target_impact_dt.strftime('%H:%M:%S')}\n"
                result_text += "--------------------------\n"
                
                # 行軍時間が長い順に並べ替えて表示（そのほうが指示が見やすいため）
                sorted_selected = sorted(selected_names, key=lambda x: all_members_data[x], reverse=True)
                
                for name in sorted_selected:
                    travel_sec = all_members_data[name]
                    departure_dt = target_impact_dt - timedelta(seconds=travel_sec)
                    rally_start_dt = departure_dt - timedelta(minutes=rally_wait_min)
                    
                    m_s = f"{all_members_data[name]//60}:{all_members_data[name]%60:02d}"
                    result_text += f"●{name} ({m_s})\n"
                    result_text += f" ├ 集結：{rally_start_dt.strftime('%H:%M:%S')}\n"
                    result_text += f" └ スタート：{departure_dt.strftime('%H:%M:%S')}\n"
                
                result_text += "--------------------------\n"
                result_text += f"※集結{rally_wait_min}分設定"

                # 結果表示
                st.write("▼ 以下の枠内をコピー！")
                st.code(result_text, language="text")
                st.info("右上のアイコンをタップしてコピー完了")

            except Exception as e:
                st.error("入力形式を確認してください。")
    else:
        st.info("（2）で今回の参加者にチェックを入れてください。")
else:
    st.warning("まずは「集結主リスト」に全員分の名前と時間を入力してください。")
