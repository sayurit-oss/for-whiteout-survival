import streamlit as st
import pandas as pd
import json
import os

# --- 設定・ファイルパス ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'
CONFIG_FILE = 'manual_custom_data.json'

# --- データ読み書き関数 ---
def load_custom_data():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"👥 メンバー管理": [], "🚩 領土・資源": [], "⚔️ イベント攻略": []}

def save_custom_data(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
                # 既存のdb(JSON)を消さずに合体させる
                db[sheet_name] = {"スケジュール": schedule}
            return db, "最新データを読み込んだよ！✨"
        except Exception as e:
            return db, f"メインエクセル読み込みエラー💦: {e}"
    return db, "JSONデータを使用中😊"

def load_other_events():
    """報酬型イベントをカテゴリー別に読み込む（揺れに強く修正）"""
    others = {}
    if os.path.exists(OTHER_EXCEL):
        try:
            df_others = pd.read_excel(OTHER_EXCEL)
            # 💡 修正ポイント1: 列名の揺れを強制吸収
            df_others.columns = ['カテゴリー' if 'カテゴリ' in str(c) else c for c in df_others.columns]
            
            if 'カテゴリー' in df_others.columns and 'イベント名' in df_others.columns:
                df_others = df_others.dropna(subset=['カテゴリー', 'イベント名'])
                for cat in df_others['カテゴリー'].unique():
                    others[cat] = df_others[df_others['カテゴリー'] == cat]['イベント名'].tolist()
        except Exception as e:
            # エラーが出てもアプリを止めないよう、ログを出す程度に
            print(f"DEBUG: 報酬型読み込み失敗: {e}")
    return others

def load_db():
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                db = json.load(f)
        except:
            db = {}
    db, msg = load_excel_to_db(db)
    return db, msg

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- 共通の初期化 ---
st.set_page_config(page_title="MMC同盟管理ツール", page_icon="🛡️", layout="wide")
db, init_msg = load_db()

if "first_load" not in st.session_state:
    st.toast(init_msg)
    st.session_state["first_load"] = True

# --- サイドバーメニュー ---
st.sidebar.title("🛡️ MMC管理メニュー")
app_mode = st.sidebar.radio(
    "メニュー切り替え",
    ["スケジュールを自動で作る✨", "新イベントを教え込む📝", "運営マニュアル 📜", "マニュアルを編集する ⚙️"],
    index=0
)

# --- 1. スケジュール作成画面 ---
if app_mode == "スケジュールを自動で作る✨":
    st.title("🛡️ スケジュールメーカー")
    
    if not db:
        st.warning("メインイベントのデータが見つかりません。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📍 ランキングイベント")
            active_events = st.multiselect("イベントを選択", list(db.keys()))
            event_days = {ev: st.selectbox(f"【{ev}】は何日目？", list(db[ev]["スケジュール"].keys())) for ev in active_events}
        with col2:
            st.subheader("🔮 4日後までの予定")
            future_events = [st.selectbox(f"{i}日後", ["特になし"] + list(db.keys()), key=f"f_{i}") for i in range(1, 5)]

        st.divider()
        st.subheader("🎁 報酬型イベント")
        others_dict = load_other_events()
        selected_others = []
        if others_dict:
            cols = st.columns(len(others_dict))
            for i, (cat, items) in enumerate(others_dict.items()):
                with cols[i]:
                    selected_others.extend(st.multiselect(cat, items, key=f"p_{cat}"))

        if st.button("案内文をポチッと生成！🚀"):
            today_points = []
            for ev in active_events:
                today_points.extend(db[ev]["スケジュール"].get(event_days[ev], []))
            doubled = list(set([x for x in today_points if today_points.count(x) > 1]))
            
            caution_msg = ""
            for i, f_ev in enumerate(future_events):
                if f_ev != "特になし" and f_ev in db:
                    matches = [p for p in db[f_ev]["スケジュール"].get("1日目", []) if p in today_points]
                    if matches:
                        caution_msg = f"\n⚠️温存推奨アイテム⚠️\n{', '.join(matches)}\n（{i+1}日後から {f_ev}）"
                        break

            output = "【今日のスケジュール】\n"
            for i, ev in enumerate(active_events + selected_others, 1):
                suffix = f"（{event_days[ev]}）" if ev in active_events else ""
                output += f"{i}．{ev}{suffix}\n"
            if doubled: output += f"\n🔥おすすめアイテム🔥\n{', '.join(doubled)}\n（イベント間で重複）\n"
            output += caution_
