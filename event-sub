import streamlit as st
import pandas as pd
import json
import os

# --- ファイルパス設定 ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'

def load_excel_to_db(db):
    """エクセルからデータを読み込んでDBを更新する"""
    if os.path.exists(EXCEL_FILE):
        try:
            xls = pd.ExcelFile(EXCEL_FILE)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                schedule = {}
                # 「日目」が含まれる列を対象にする
                day_cols = [c for c in df.columns if '日目' in str(c)]
                for col in day_cols:
                    # 〇, ◎, ○ が入っている項目を抽出
                    active_items = df[df[col].isin(['〇', '◎', '○'])]['項目名'].tolist()
                    schedule[str(col)] = active_items
                
                # エクセルのデータで上書き、または新規追加
                db[sheet_name] = {"スケジュール": schedule}
            return db, "エクセルから最新データを読み込んだよ！✨"
        except Exception as e:
            return db, f"エクセル読み込みでエラーが出ちゃった💦: {e}"
    return db, "エクセルファイルが見つからなかったよ。JSONデータを使うね。😊"

def load_db():
    db = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            db = json.load(f)
    # エクセルがあれば上書き/追加
    db, msg = load_excel_to_db(db)
    return db, msg

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- Streamlit UI ---
st.set_page_config(page_title="明太もちメーカー", page_icon="🛡️")
db, init_msg = load_db()

st.title("🛡️ 盟主業務サポート：明太もちメーカー")
st.toast(init_msg) # 起動時に読み込み状況を通知

# 1. 機能選択
mode = st.sidebar.radio("やりたいことを選んでね♪", ["案内文を自動で作る✨", "新イベントを教え込む📝"])

# --- モード1：新イベント登録（手動） ---
if mode == "新イベントを教え込む📝":
    st.header("📝 期間限定イベントを覚えさせる")
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

# --- モード2：自動生成 ---
else:
    st.header("✨ 今日の案内文を自動生成")
    
    if not db:
        st.warning("イベントデータが空っぽだよ。エクセルを置くか、新イベントを登録してね！")
    else:
        col1, col2 = st.columns(2)
        with col1:
            active_events = st.multiselect("今日のイベントを選択（複数OK）", list(db.keys()))
            event_days = {}
            for ev in active_events:
                event_days[ev] = st.selectbox(f"【{ev}】は何日目？", list(db[ev]["スケジュール"].keys()), key=f"select_{ev}")

        with col2:
            future_events = []
            for i in range(1, 5):
                f = st.selectbox(f"{i}日後の予定", ["特になし"] + list(db.keys()), key=f"f{i}")
                future_events.append(f)

        if st.button("案内文をポチッと生成！🚀"):
            # 案内文ロジック（重複判定・温存判定）は前回のコードと同様
            today_points = []
            for ev, day in event_days.items():
                today_points.extend(db[ev]["スケジュール"][day])
            
            doubled_points = list(set([x for x in today_points if today_points.count(x) > 1]))
            
            # 温存アドバイス
            caution_msg = ""
            for i, f_ev in enumerate(future_events):
                if f_ev != "特になし":
                    f_points = db[f_ev]["スケジュール"].get("1日目", [])
                    matches = [p for p in f_points if p in today_points]
                    if matches:
                        caution_msg = f"\n⚠️ **ちょっと待って！温存アドバイス** ⚠️\n{i+1}日後から **{f_ev}** が始まるよ！🔥\n「{', '.join(matches)}」が被ってるから、アイテム温存も検討してパワーを溜めておいてね！✨"
                        break

            # テキスト生成
            output = f"お疲れ様です〜♪ 明太もちです😊\n\n今日のスケジュールを整理したよ✨\n"
            for i, ev in enumerate(active_events):
                output += f"{i+1}. {ev}（{event_days[ev]}）\n"
            
            if doubled_points:
                output += f"\n💡 **明太もちの「ココがお得！」ポイント**\n今日は「{', '.join(doubled_points)}」が共通してポイントになるよ！💪\nまとめてクリアしてお得に進めよう〜🎶\n"
            
            output += caution_msg
            output += "\n今日も一日楽しもー！絶対勝つよー！💪🔥"
            
            st.text_area("案内文（コピー用）", output, height=300)
