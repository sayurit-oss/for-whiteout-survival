import streamlit as st
import pandas as pd
import json
import os

# --- ファイルパス設定 ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'  # 追記

def load_excel_to_db(db):
    """エクセルからデータを読み込んでDBを更新する"""
    if os.path.exists(EXCEL_FILE):
        try:
            xls = pd.ExcelFile(EXCEL_FILE)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                schedule = {}
                day_cols = [c for c in df.columns if '日目' in str(c)]
                for col in day_cols:
                    active_items = df[df[col].isin(['〇', '◎', '○'])]['項目名'].tolist()
                    schedule[str(col)] = active_items
                db[sheet_name] = {"スケジュール": schedule}
            return db, "エクセルから最新データを読み込んだよ！✨"
        except Exception as e:
            return db, f"エクセル読み込みでエラーが出ちゃった💦: {e}"
    return db, "エクセルファイルが見つからなかったよ。JSONデータを使うね。😊"

# --- 追記：報酬型イベントの読み込み関数 ---
def load_other_events():
    others = {}
    if os.path.exists(OTHER_EXCEL):
        try:
            df_others = pd.read_excel(OTHER_EXCEL)
            for cat in df_others['カテゴリー'].unique():
                others[cat] = df_others[df_others['カテゴリー'] == cat]['イベント名'].tolist()
        except:
            pass
    return others

def load_db():
    db = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            db = json.load(f)
    db, msg = load_excel_to_db(db)
    return db, msg

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- Streamlit UI ---
st.set_page_config(page_title="明太もちメーカー", page_icon="🛡️")
db, init_msg = load_db()

st.title("🛡️ 盟主業務サポート：明太もちメーカー")
st.toast(init_msg)

mode = st.sidebar.radio("やりたいことを選んでね♪", ["案内文を自動で作る✨", "新イベントを教え込む📝"])

if mode == "新イベントを教え込む📝":
    st.header("📝 期間限定イベントを覚えさせる")
    with st.form("add_event"):
        new_name = st.text_input("イベント名")
        days = st.slider("開催日数", 1, 7, 3)
        all_items = ["火晶建築", "領主装備", "領主宝石", "訓練昇格", "英雄欠片", "各種加速", "採集", "ペット", "ダイヤ", "専門家", "専装エナ", "ミスリル", "ルーレット", "鍵", "獣"]
        new_sched = {}
        for d in range(1, days + 1):
            selected = st.multiselect(f"{d}日目のポイント項目", all_items, key=f"day_{d}")
            new_sched[f"{d}日目"] = selected
        if st.form_submit_button("サーバーに保存！✨"):
            if new_name:
                db[new_name] = {"スケジュール": new_sched}
                save_db(db)
                st.success(f"『{new_name}』を保存したよ！")
            else:
                st.error("イベント名を入れてね💦")

else:
    st.header("✨ 今日の案内文を自動生成")
    if not db:
        st.warning("イベントデータが空っぽだよ。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            active_events = st.multiselect("今日のメインイベントを選択", list(db.keys()))
            event_days = {}
            for ev in active_events:
                event_days[ev] = st.selectbox(f"【{ev}】は何日目？", list(db[ev]["スケジュール"].keys()), key=f"select_{ev}")

        with col2:
            future_events = []
            for i in range(1, 3): # 温存アドバイス用に2日後まで確認
                f = st.selectbox(f"{i}日後の予定", ["特になし"] + list(db.keys()), key=f"f{i}")
                future_events.append(f)

        # --- 追記：報酬型イベント（その他）の選択UI ---
        st.divider()
        st.subheader("🎁 報酬型イベント（リマインド）")
        others_dict = load_other_events()
        selected_others = []
        if others_dict:
            cols = st.columns(len(others_dict))
            for i, (cat, items) in enumerate(others_dict.items()):
                with cols[i]:
                    picked = st.multiselect(cat, items, key=f"other_{cat}")
                    selected_others.extend(picked)

        # --- 案内文生成ボタン ---
        if st.button("案内文をポチッと生成！🚀"):
            today_points = []
            for ev, day in event_days.items():
                today_points.extend(db[ev]["スケジュール"][day])
            
            # 重複判定
            doubled_points = list(set([x for x in today_points if today_points.count(x) > 1]))
            
            # 温存判定
            caution_msg = ""
            for i, f_ev in enumerate(future_events):
                if f_ev != "特になし":
                    f_points = db[f_ev]["スケジュール"].get("1日目", [])
                    matches = [p for p in f_points if p in today_points]
                    if matches:
                        caution_msg = f"\n⚠️**温存推奨アイテム**⚠️\n{', '.join(matches)}\n（{i+1}日後から {f_ev}）"
                        break

            # --- 出力フォーマット（シンプル版） ---
            output = "【今日のスケジュール】\n"
            idx = 1
            # メインイベント
            for ev, day in event_days.items():
                output += f"{idx}．{ev}（{day}）\n"
                idx += 1
            # 報酬型イベント
            for o_ev in selected_others:
                output += f"{idx}．{o_ev}\n"
                idx += 1
            
            # おすすめアイテム
            if doubled_points:
                output += f"\n🔥**おすすめアイテム**🔥\n{', '.join(doubled_points)}\n（イベント間で重複）\n"
            
            # 温存アドバイス
            output += caution_msg
            
            st.text_area("案内文（コピー用）", output, height=300)
