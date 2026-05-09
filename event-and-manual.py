import streamlit as st
import pandas as pd
import json
import os

# --- 設定・ファイルパス ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'
CONFIG_FILE = 'manual_custom_data.json'

# --- データ読み書き関数 (略さず統合) ---
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
                db[sheet_name] = {"スケジュール": schedule}
            return db, "最新データを読み込んだよ！✨"
        except Exception as e:
            return db, f"エラー💦: {e}"
    return db, "JSONデータを使用中😊"

def load_other_events():
    others = {}
    if os.path.exists(OTHER_EXCEL):
        try:
            df_others = pd.read_excel(OTHER_EXCEL)
            df_others.columns = ['カテゴリー' if 'カテゴリ' in str(c) else c for c in df_others.columns]
            if 'カテゴリー' in df_others.columns and 'イベント名' in df_others.columns:
                df_others = df_others.dropna(subset=['カテゴリー', 'イベント名'])
                for cat in df_others['カテゴリー'].unique():
                    others[cat] = df_others[df_others['カテゴリー'] == cat]['イベント名'].tolist()
        except Exception as e:
            st.error(f"報酬型読み込み失敗: {e}")
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

# --- 共通の初期化 ---
st.set_page_config(page_title="MMC同盟管理ツール", page_icon="🛡️", layout="wide")
db, init_msg = load_db()

# --- 💡 修正箇所：初回だけトーストを表示する ---
if "first_load" not in st.session_state:
    st.toast(init_msg)
    st.session_state["first_load"] = True # 「表示済み」のフラグを立てる

# --- サイドバーメニュー (ここをラジオボタンに変更) ---
st.sidebar.title("🛡️ MMC管理メニュー")
# プルダウンをやめて、直接並べる形式に
app_mode = st.sidebar.radio(
    "メニュー切り替え",
    [
        "スケジュールを自動で作る✨", 
        "新イベントを教え込む📝", 
        "運営マニュアル 📜", 
        "マニュアルを編集する ⚙️"
    ],
    index=0  # 初期選択をスケジュール作成に設定
)

# --- 1. スケジュール作成画面 ---
if app_mode == "スケジュールを自動で作る✨":
    st.title("🛡️ スケジュールメーカー")
    st.toast(init_msg)
    
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
            output += caution_msg
            st.code(output, language=None)

# --- 2. イベント追加画面 ---
elif app_mode == "新イベントを教え込む📝":
    st.title("📝 期間限定イベントを覚えさせる")
    tab1, tab2 = st.tabs(["🏆 ランキング型", "🎁 報酬型"])
    with tab1:
        with st.form("add_event"):
            new_name = st.text_input("イベント名")
            days = st.slider("開催日数", 1, 7, 3)
            all_items = ["火晶建築", "領主装備", "領主宝石", "訓練昇格", "英雄欠片", "各種加速", "採集", "ペット", "ダイヤ", "専門家", "専装エナ", "ミスリル", "ルーレット", "鍵", "獣"]
            new_sched = {f"{d}日目": st.multiselect(f"{d}日目", all_items, key=f"new_d_{d}") for d in range(1, days + 1)}
            if st.form_submit_button("サーバーに保存！✨"):
                if new_name:
                    db[new_name] = {"スケジュール": new_sched}
                    save_db(db)
                    st.success("保存完了！")
                    st.rerun()
    with tab2:
        with st.form("add_other_event"):
            name = st.text_input("イベント名")
            cat = st.selectbox("カテゴリー", ["高頻度", "要エントリー", "その他イベント"])
            if st.form_submit_button("報酬型リストに追加！🚀"):
                df_o = pd.read_excel(OTHER_EXCEL) if os.path.exists(OTHER_EXCEL) else pd.DataFrame(columns=['カテゴリー', 'イベント名'])
                df_o = pd.concat([df_o, pd.DataFrame([{'カテゴリー': cat, 'イベント名': name}])], ignore_index=True)
                df_o.to_excel(OTHER_EXCEL, index=False)
                st.success("追加完了！")
                st.rerun()

# --- 3. マニュアル閲覧画面 ---
elif app_mode == "運営マニュアル 📜":
    st.title("📜 MMC 運営マニュアル")
    data = load_custom_data()
    tabs = st.tabs(list(data.keys()))
    for i, category in enumerate(data.keys()):
        with tabs[i]:
            for exp in data[category]:
                with st.expander(exp['title']):
                    for block in exp['blocks']:
                        if block['type'] == 'text': st.write(block['content'])
                        else: st.code(block['content'])

# --- 4. マニュアル編集画面 ---
elif app_mode == "マニュアルを編集する ⚙️":
    st.title("⚙️ マニュアル編集モード")
    data = load_custom_data()
    category = st.selectbox("編集するカテゴリ", list(data.keys()))
    expanders = data[category]
    
    for e_idx, exp in enumerate(expanders):
        with st.container(border=True):
            exp['title'] = st.text_input(f"見出し {e_idx}", exp['title'], key=f"edit_t_{category}_{e_idx}")
            for b_idx, block in enumerate(exp['blocks']):
                c1, c2, c3 = st.columns([1, 4, 0.5])
                with c1:
                    block['type'] = st.selectbox("種別", ["text", "code"], index=0 if block['type'] == 'text' else 1, key=f"ty_{category}_{e_idx}_{b_idx}")
                with c2:
                    block['content'] = st.text_area("内容", block['content'], key=f"cn_{category}_{e_idx}_{b_idx}")
                with c3:
                    if st.button("❌", key=f"del_{category}_{e_idx}_{b_idx}"):
                        exp['blocks'].pop(b_idx)
                        save_custom_data(data)
                        st.rerun()
            if st.button("➕ パーツ追加", key=f"add_p_{category}_{e_idx}"):
                exp['blocks'].append({"type": "text", "content": ""})
                save_custom_data(data)
                st.rerun()
    
    st.divider()
    if st.button("✨ 新しい項目を追加"):
        expanders.append({"title": "新規項目", "blocks": [{"type": "text", "content": ""}]})
        save_custom_data(data)
        st.rerun()
    if st.button("💾 すべての変更を確定保存"):
        save_custom_data(data)
        st.success("マニュアルを更新したよ！")
