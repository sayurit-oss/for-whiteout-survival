import streamlit as st
import pandas as pd
import json
import os

# --- ファイルパス設定 ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'

def load_excel_to_db(db):
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
            return db, "メインイベント一覧を読み込んだよ！✨"
        except Exception as e:
            return db, f"エクセル読み込みエラー💦: {e}"
    return db, "JSONデータを使用中😊"

def load_other_events():
    """「その他イベント一覧」から報酬型イベントをカテゴリー別に読み込む"""
    others = {}
    if os.path.exists(OTHER_EXCEL):
        try:
            df_others = pd.read_excel(OTHER_EXCEL)
            # 💡 列名の揺れを吸収
            df_others.columns = ['カテゴリー' if 'カテゴリ' in str(c) else c for c in df_others.columns]
            
            if 'カテゴリー' in df_others.columns and 'イベント名' in df_others.columns:
                df_others = df_others.dropna(subset=['カテゴリー', 'イベント名'])
                for cat in df_others['カテゴリー'].unique():
                    others[cat] = df_others[df_others['カテゴリー'] == cat]['イベント名'].tolist()
            else:
                st.error(f"列名が違います。現在の列名: {list(df_others.columns)}")
        except Exception as e:
            st.error(f"読み込み失敗: {e}")
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
st.set_page_config(page_title="スケジュールメーカー", page_icon="🛡️")
db, init_msg = load_db()

st.title("🛡️ スケジュールメーカー")
st.toast(init_msg)

mode = st.sidebar.radio("メニュー", ["スケジュールを自動で作る✨", "新イベントを教え込む📝"])

# --- モード選択の分岐 ---
if mode == "新イベントを教え込む📝":
    st.header("📝 期間限定イベントを覚えさせる")
    
    edit_tab1, edit_tab2 = st.tabs(["🏆 ランキング型（ポイント系）", "🎁 報酬型（リマインド系）"])
    
    with edit_tab1:
        st.info("※恒常イベントはエクセルを編集して保存するだけでOKだよ！😊")
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
                    st.success(f"『{new_name}』を保存したよ！案内文作成で選べるようになったよ〜🎶")
                else:
                    st.error("イベント名を入れてね💦")

    # 💡 修正箇所：このブロックをif mode == "新イベントを教え込む📝": の中に正しく字下げして配置
    with edit_tab2:
        st.subheader("🎁 報酬型イベントの追加")
        
        with st.form("add_other_event"):
            new_other_name = st.text_input("イベント名（例：兵器工場エントリー）")
            new_other_cat = st.selectbox("カテゴリー", ["高頻度", "要エントリー", "その他イベント"])
            
            if st.form_submit_button("報酬型リストに追加！🚀"):
                if new_other_name:
                    try:
                        if os.path.exists(OTHER_EXCEL):
                            df_o = pd.read_excel(OTHER_EXCEL)
                            df_o.columns = ['カテゴリー' if 'カテゴリ' in str(c) else c for c in df_o.columns]
                        else:
                            df_o = pd.DataFrame(columns=['カテゴリー', 'イベント名'])
                        
                        new_row = pd.DataFrame([{'カテゴリー': new_other_cat, 'イベント名': new_other_name}])
                        df_o = pd.concat([df_o, new_row], ignore_index=True)
                        
                        df_o.to_excel(OTHER_EXCEL, index=False)
                        st.success(f"『{new_other_name}』を「{new_other_cat}」に追加したよ！✨")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"保存中にエラーが発生しました: {e}")
                else:
                    st.error("イベント名を入力してください！")

# --- 自動生成モード ---
else:
    if not db:
        st.warning("メインイベントのデータが見つかりません。")
    else:
        col_today, col_future = st.columns(2)
        
        with col_today:
            st.subheader("📍 ランキングイベント")
            active_events = st.multiselect("イベントを選択", list(db.keys()), key="main_select")
            event_days = {}
            for ev in active_events:
                event_days[ev] = st.selectbox(f"【{ev}】は何日目？", list(db[ev]["スケジュール"].keys()), key=f"day_sel_{ev}")

        with col_future:
            st.subheader("🔮 4日後までの予定")
            future_events = []
            for i in range(1, 5):
                f = st.selectbox(f"{i}日後", ["特になし"] + list(db.keys()), key=f"future_{i}")
                future_events.append(f)

        st.divider()
        st.subheader("🎁 報酬型イベント")
        others_dict = load_other_events()
        selected_others = []

        if not others_dict:
            st.info("まだ報酬型イベントが登録されていません。「新イベントを教え込む📝」タブから追加してください。")
        else:
            cols = st.columns(len(others_dict))
            for i, (cat, items) in enumerate(others_dict.items()):
                with cols[i]:
                    picked = st.multiselect(cat, items, key=f"other_pick_{cat}")
                    selected_others.extend(picked)

        if st.button("案内文をポチッと生成！🚀"):
            today_points = []
            if active_events:
                for ev in active_events:
                    day = event_days.get(ev)
                    if day and ev in db:
                        today_points.extend(db[ev]["スケジュール"].get(day, []))
            
            doubled_points = list(set([x for x in today_points if today_points.count(x) > 1]))
            
            caution_msg = ""
            for i, f_ev in enumerate(future_events):
                if f_ev != "特になし" and f_ev in db:
                    f_points = db[f_ev]["スケジュール"].get("1日目", [])
                    matches = [p for p in f_points if p in today_points]
                    if matches:
                        caution_msg = f"\n⚠️温存推奨アイテム⚠️\n{', '.join(matches)}\n（{i+1}日後から {f_ev}）"
                        break

            output = "【今日のスケジュール】\n"
            idx = 1
            
            for ev in active_events:
                day = event_days.get(ev)
                if day:
                    output += f"{idx}．{ev}（{day}）\n"
                    idx += 1
            
            for o_ev in selected_others:
                output += f"{idx}．{o_ev}\n"
                idx += 1
            
            if doubled_points:
                output += f"\n🔥おすすめアイテム🔥\n{', '.join(doubled_points)}\n（イベント間で重複）\n"
            
            output += caution_msg
            
            st.divider()
            st.subheader("📋 生成された案内文")
            st.caption("右上のボタンをタップしてコピー！")
            st.code(output, language=None)
