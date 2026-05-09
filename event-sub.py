import streamlit as st
import pandas as pd
import json
import os

# --- ファイルパス設定 ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'

def load_excel_to_db(db):
    """エクセルからメインイベントデータを読み込んでDBを更新する"""
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
            # エクセル全体を読み込み、空行を削除
            df_others = pd.read_excel(OTHER_EXCEL).dropna(subset=['カテゴリ', 'イベント名'])
            # カテゴリごとにリスト化
            for cat in df_others['カテゴリ'].unique():
                others[cat] = df_others[df_others['カテゴリ'] == cat]['イベント名'].tolist()
        except Exception as e:
            st.error(f"報酬型イベントの読み込みに失敗しました: {e}")
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
                st.success(f"『{new_name}』を保存しました！")
            else:
                st.error("名前を入力してください")

else:
    st.header("✨ 今日の案内文を自動生成")
    if not db:
        st.warning("メインイベントのデータが見つかりません。")
    else:
        # --- レイアウト：左側（今日）と右側（未来） ---
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
            # ホワサバ仕様に合わせて4日後まで入力可能に
            for i in range(1, 5):
                f = st.selectbox(f"{i}日後", ["特になし"] + list(db.keys()), key=f"future_{i}")
                future_events.append(f)

        # --- 報酬型イベント（その他イベント一覧） ---
        st.divider()
        st.subheader("🎁 報酬型イベント")
        others_dict = load_other_events()
        selected_others = []

        if not others_dict:
            st.info("「その他イベント一覧.xlsx」を読み込むと、ここに選択肢が表示されます。")
        else:
            cols = st.columns(len(others_dict))
            for i, (cat, items) in enumerate(others_dict.items()):
                with cols[i]:
                    picked = st.multiselect(cat, items, key=f"other_pick_{cat}")
                    selected_others.extend(picked)

# --- 生成ボタン ---
        if st.button("案内文をポチッと生成！🚀"):
            # 1. 今日のポイント項目を収集（安全な取得方法に変更）
            today_points = []
            if active_events:
                for ev in active_events:
                    # event_daysにデータがあるか確認してから取得
                    day = event_days.get(ev)
                    if day and ev in db:
                        today_points.extend(db[ev]["スケジュール"].get(day, []))
            
            # 重複項目の抽出
            doubled_points = list(set([x for x in today_points if today_points.count(x) > 1]))
            
            # 2. 温存判定（4日後までスキャン）
            caution_msg = ""
            for i, f_ev in enumerate(future_events):
                if f_ev != "特になし" and f_ev in db:
                    # 未来のイベントの1日目のポイントと今日を比較
                    f_points = db[f_ev]["スケジュール"].get("1日目", [])
                    matches = [p for p in f_points if p in today_points]
                    if matches:
                        caution_msg = f"\n⚠️温存推奨アイテム⚠️\n{', '.join(matches)}\n（{i+1}日後から {f_ev}）"
                        break

            # 3. シンプル版フォーマットの構築
            output = "【今日のスケジュール】\n"
            idx = 1
            
            # メインイベントの表示
            for ev in active_events:
                day = event_days.get(ev)
                if day:
                    output += f"{idx}．{ev}（{day}）\n"
                    idx += 1
            
            # 報酬型イベントの表示
            for o_ev in selected_others:
                output += f"{idx}．{o_ev}\n"
                idx += 1
            
            # おすすめアイテム（重複）
            if doubled_points:
                output += f"\n🔥おすすめアイテム🔥\n{', '.join(doubled_points)}\n（イベント間で重複）\n"
            
            # 温存アドバイス
            output += caution_msg
            
            # 4. コピーボタン付き出力エリア
            st.divider()
            st.subheader("📋 生成された案内文")
            st.caption("右上のボタンをタップしてコピー！")
            # st.code を使うことで標準のコピーボタンが使えます
            st.code(output, language=None)
