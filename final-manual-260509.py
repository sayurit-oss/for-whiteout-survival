import streamlit as st
import pandas as pd
import json
import os
import re
import math
from PIL import Image

# --- Google Gemini ライブラリの安全なインポート (新旧両対応) ---
GENAI_TYPE = None
try:
    from google import genai
    GENAI_TYPE = "new"
except ImportError:
    try:
        import google.generativeai as legacy_genai
        GENAI_TYPE = "legacy"
    except ImportError:
        GENAI_TYPE = None

# --- 設定・ファイルパス ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'
CONFIG_FILE = 'manual_custom_data.json'
MEMBER_ROSTER_FILE = 'alliance_members.json'

# --- 座標・行軍シミュレーター設定 ---
HQ_NAME = "本部"
HQ_COORD = (732, 418)
BASE_FORTRESS_COORD = (597, 800)
BASE_SECONDS = 600.0  # 本部 -> 要塞1号 (600秒)

# 1座標あたりの所要秒数 (速度係数)
base_dist = math.sqrt((BASE_FORTRESS_COORD[0] - HQ_COORD[0])**2 + (BASE_FORTRESS_COORD[1] - HQ_COORD[1])**2)
SEC_PER_UNIT = BASE_SECONDS / base_dist

LOCATIONS = {
    "要塞1号": (597, 800),
    "要塞2号": (400, 597),
    "要塞3号": (597, 400),
    "要塞4号": (800, 597),
    "砦1号": (237, 828),
    "砦2号": (237, 606),
    "砦3号": (237, 348),
    "砦4号": (366, 237),
    "砦5号": (588, 237),
    "砦6号": (846, 237),
    "砦7号": (957, 348),
    "砦8号": (957, 606),
    "砦9号": (957, 828),
    "砦10号": (846, 957),
    "砦11号": (606, 957),
    "砦12号": (366, 957),
}

def get_travel_time(p1_coord, p2_coord):
    dist = math.sqrt((p2_coord[0] - p1_coord[0])**2 + (p2_coord[1] - p1_coord[1])**2)
    sec = dist * SEC_PER_UNIT
    minutes = round(sec / 60)
    return minutes, sec

# --- 同盟メンバー初期名簿 ---
DEFAULT_ROSTER = [
    "わからん", "ringo", "harupon", "マンダラ", "LOSER", "ナーナ", "焼きりんご", "田中一郎", 
    "ハンギョ", "はんぎょどん", "toriaezu beer", "愛犬クル", "くま3", "ショーン伍長", "ベビっく", "いりる", "kara", "ちゃーーーん", "ちゃん②", 
    "mii", "mi mi", "わんこ", "すん", "れくさす", "アッシュ", "シュナ", "おもち", "こもち", "まごもち", "はむち", "まーぼー豆腐", "豆腐２丁目", "ちよ", 
    "KENT", "なはらた", "花ちゃん", "やらかす猫", "雪乃。", "non", "チョココロネ", "もっち", "Yotsuba", "ののか", "Sora", 
    "えんまめ", "えんまめこ", "さとし", "ジョイ", "ばりうけさん", "ばりさぶ", "ばりさぶさぶ", "ゆめゆめ", "ポメラニアンもち", "ケイヤン", "はむち", "Hazem Tr", 
    "なんし～", "黒潮丸", "ちかひさ", "non", "しるす", "Lilia", "ぶどう", "かなはなむ", "山岡家", "SGT", "マンダーラ", "まるみ"
]

def load_member_roster():
    if os.path.exists(MEMBER_ROSTER_FILE):
        try:
            with open(MEMBER_ROSTER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_ROSTER

def save_member_roster(roster_list):
    with open(MEMBER_ROSTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(roster_list, f, ensure_ascii=False, indent=4)

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
                db[sheet_name] = {"スケジュール": schedule}
            return db, "最新データを読み込んだよ！✨"
        except Exception as e:
            return db, f"メインエクセル読み込みエラー💦: {e}"
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
        except:
            pass
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

# --- 総力文字列（例: "300.5M", "1.2B"）を数値に変換するヘルパー ---
def parse_power_value(power_str: str) -> float:
    if not power_str:
        return 0.0
    s = str(power_str).upper().replace(",", "").strip()
    match = re.search(r'([\d.]+)\s*([BMK]?)', s)
    if not match:
        return 0.0
    val = float(match.group(1))
    unit = match.group(2)
    if unit == 'B':
        return val * 1_000_000_000
    elif unit == 'M':
        return val * 1_000_000
    elif unit == 'K':
        return val * 1_000
    return val

# --- Gemini API を使った画像認識関数 (左上の総力＋メンバー一覧を取得) ---
def extract_members_with_gemini(image: Image.Image, roster: list) -> tuple[float, list]:
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", "")).strip()
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY が見つかりません。Streamlitの `Secrets` に設定してください。")
        return 0.0, []
    
    if not GENAI_TYPE:
        st.error("⚠️ Geminiのライブラリがインストールされていません。requirements.txt を確認してください。")
        return 0.0, []

    roster_str = ", ".join(roster)
    prompt = f"""
あなたはゲーム「ホワイトアウト・サバイバル」の画像読み取りアシスタントです。
添付されたスクショ画像（投票メンバー一覧）から、以下の2つを抽出してください。

1. 【画像左上のメンバーの総力数値】（例: 300.5M、1.2B、850K など）
2. 【画像内に写っている全メンバーの名前】（上から順・左から順、最大12名）

【厳格なルール】
- 以下の【同盟メンバー名簿】の中から、画像内に写っているメンバーを特定して一致する名前を出力してください。
  名簿: [{roster_str}]
- 特殊記号（「ʕ·ᴥ·ʔ」など）や同盟タグ（「M2C」「MMC」「MC」「yfc」「肴」など）は完全に除去してください。
- 「とりあえずビール」は名簿にある「toriaezu beer」として扱ってください。「雪乃。」は「雪乃」として扱ってください。
- 出力フォーマットは必ず以下の形式のみとし、解説や挨拶、マークダウン装飾などは一切含めないでください。

TOP_POWER: 300.5M
メンバー1
メンバー2
メンバー3
"""

    model_candidates = ['gemini-3.6-flash', 'models/gemini-3.6-flash', 'gemini-flash-latest']
    raw_text = ""
    last_err = None

    if GENAI_TYPE == "new":
        client = genai.Client(api_key=api_key)
        for m in model_candidates:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=[prompt, image]
                )
                raw_text = response.text
                if raw_text:
                    break
            except Exception as e:
                last_err = e
                continue
    else:
        legacy_genai.configure(api_key=api_key)
        for m in model_candidates:
            try:
                clean_m = m.replace("models/", "")
                model = legacy_genai.GenerativeModel(clean_m)
                response = model.generate_content([prompt, image])
                raw_text = response.text
                if raw_text:
                    break
            except Exception as e:
                last_err = e
                continue

    if not raw_text:
        st.error(f"⚠️ AI読み取りエラー: {last_err}")
        return 0.0, []

    lines = raw_text.strip().split("\n")
    top_power = 0.0
    extracted = []
    
    for l in lines:
        line = l.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue
        if line.upper().startswith("TOP_POWER:"):
            power_part = line.split(":", 1)[1].strip()
            top_power = parse_power_value(power_part)
        else:
            clean_name = line.lstrip("・-1234567890. ")
            if clean_name:
                extracted.append(clean_name)

    return top_power, extracted

# --- 共通の初期化 ---
st.set_page_config(page_title="MMC同盟管理ツール", page_icon="🛡️", layout="wide")
db, init_msg = load_db()

if "first_load" not in st.session_state:
    st.toast(init_msg)
    st.session_state["first_load"] = True

# --- サイドバーメニュー ---
st.sidebar.title("🛡️ MMC管理メニュー")
MENU_SIMULATOR = "要塞・砦行軍を計算する ⚔️"

app_mode = st.sidebar.radio(
    "メニュー切り替え",
    [
        "スケジュールを自動で作る✨", 
        "クレジョイ案内をつくる 🛡️", 
        MENU_SIMULATOR, 
        "新イベントを教え込む📝", 
        "運営マニュアル 📜", 
        "マニュアルを編集する ⚙️"
    ],
    index=0
)

# ==========================================
# 1. スケジュール作成画面
# ==========================================
if app_mode == "スケジュールを自動で作る✨":
    st.title("📅 スケジュールメーカー")
    if not db:
        st.warning("メインイベントのデータが見つかりません。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📍 ランキングイベント")
            active_events = st.multiselect("イベントを選択", list(db.keys()))
            event_days = {}
            for ev in active_events:
                event_days[ev] = st.selectbox(f"【{ev}】は何日目？", list(db[ev]["スケジュール"].keys()), key=f"sel_{ev}")
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
        else:
            st.info("報酬型イベントがまだ登録されていません。")

        if st.button("案内文を生成！🚀"):
            today_points = []
            for ev in active_events:
                today_points.extend(db[ev]["スケジュール"].get(event_days[ev], []))
            doubled = list(set([x for x in today_points if today_points.count(x) > 1]))
            
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
                output += f"{idx}．{ev}（{day}）\n"
                idx += 1
            for o_ev in selected_others:
                output += f"{idx}．{o_ev}\n"
                idx += 1
            if doubled:
                output += f"\n🔥おすすめアイテム🔥\n{', '.join(doubled)}\n（イベント間で重複）\n"
            output += caution_msg
            st.divider()
            st.subheader("📋 生成された案内文")
            st.caption("右上のボタンをタップしてコピー！")
            st.code(output, language=None)

# ==========================================
# 2. クレジョイ案内をつくる画面
# ==========================================
elif app_mode == "クレジョイ案内をつくる 🛡️":
    st.title("🛡️ クレジョイ10&20駐屯")

    roster = load_member_roster()

    with st.expander(f"👥 同盟メンバー名簿の確認・編集（現在: {len(roster)} 名）"):
        st.caption("あらかじめ同盟メンバーの名前をここに登録しておくと、AIが画像を名簿と照合して手ブレなく読み取ります。")
        roster_text = st.text_area("登録メンバー一覧 (1行に1人):", value="\n".join(roster), height=160)
        if st.button("💾 名簿を保存する"):
            updated_roster = [r.strip() for r in roster_text.split("\n") if r.strip()]
            save_member_roster(updated_roster)
            st.success("メンバー名簿を保存しました！✨")
            st.rerun()

    st.divider()

    col_main, _ = st.columns([10, 1])
    
    with col_main:
        st.subheader("① 画像をアップロード（最大2枚まで選択可能）")
        uploaded_files = st.file_uploader("オンライン投票メンバーのスクショを選択（順番不問・総力順で自動整列します）", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        if uploaded_files:
            # 2枚超の場合は最初の2枚のみ使用
            target_files = uploaded_files[:2]
            if len(uploaded_files) > 2:
                st.info("※画像が3枚以上選択されています。最初の2枚のみを読み取ります。")

            # 新規アップロードチェック（ファイル名結合で判断）
            current_file_names = "_".join([f.name for f in target_files])
            
            if "last_uploaded_names" not in st.session_state or st.session_state["last_uploaded_names"] != current_file_names:
                parsed_results = []
                with st.spinner("AIが画像からメンバーと左上の総力を解析中..."):
                    for file in target_files:
                        raw_image = Image.open(file)
                        top_power, parsed = extract_members_with_gemini(raw_image, roster)
                        parsed_results.append({
                            "file": file,
                            "top_power": top_power,
                            "members": parsed
                        })
                
                # 左上メンバーの総力が高い順（降順）に画像を並び替え
                parsed_results.sort(key=lambda x: x["top_power"], reverse=True)
                
                all_extracted = []
                for res in parsed_results:
                    all_extracted.extend(res["members"])
                
                # 順序を保ちつつ重複を除去（順位・強さを維持するためdict.fromkeysを使用）
                unique_extracted = list(dict.fromkeys(all_extracted))
                st.session_state["parsed_members"] = unique_extracted
                st.session_state["sorted_files_info"] = [
                    {"file": r["file"], "top_power": r["top_power"]} for r in parsed_results
                ]
                st.session_state["last_uploaded_names"] = current_file_names

            # プレビュー表示（総力順に並び替えた後の順序で表示）
            with st.expander("🖼️ アップロードした画像を確認（総力順）"):
                sorted_info = st.session_state.get("sorted_files_info", [])
                if sorted_info:
                    cols = st.columns(len(sorted_info))
                    for i, info in enumerate(sorted_info):
                        with cols[i]:
                            p_val = info["top_power"]
                            p_label = f" / 左上総力: {p_val / 1_000_000:.1f}M" if p_val > 0 else ""
                            st.image(Image.open(info["file"]), caption=f"{i+1}枚目: {info['file'].name}{p_label}", use_container_width=True)

            # --- STEP 2: 読み取り結果の確認・修正 ---
            st.subheader("② メンバーの確認・修正")
            current_text = "\n".join(st.session_state.get("parsed_members", []))
            members_text = st.text_area(
                "抽出されたメンバー名 (手動で修正・順序の並び替え・追加も可能です)",
                value=current_text,
                height=220
            )
            member_list = [m.strip() for m in members_text.split("\n") if m.strip()]
            st.caption(f"現在の認識人数（重複除外後）: **{len(member_list)} 名**")

            if not member_list:
                st.warning("メンバー名が認識できませんでした。上の枠に直接入力してください。")
            else:
                st.divider()

                # --- STEP 3: 条件設定 ---
                st.subheader("③ 条件の設定")
                
                c_lead1, c_lead2 = st.columns(2)
                with c_lead1:
                    leader_lv10 = st.selectbox("👑 Lv10 駐屯リーダーを選択", options=member_list, index=0)
                with c_lead2:
                    default_lv20_idx = 1 if len(member_list) > 1 else 0
                    leader_lv20 = st.selectbox("👑 Lv20 駐屯リーダーを選択", options=member_list, index=default_lv20_idx)
                
                c_cap1, c_cap2 = st.columns(2)
                with c_cap1:
                    max_cap_input = st.number_input("🏰 本部駐屯容量（駐屯箱サイズ）", min_value=100000, value=1430000, step=10000)
                with c_cap2:
                    target_troops = st.number_input("🪖 1人あたりの派遣兵士数", min_value=1000, value=130000, step=10000)

                st.markdown("#### ⚔️ 兵種比率の設定")
                r_col1, r_col2 = st.columns(2)
                
                # --- Lv10 兵種比率 ---
                with r_col1:
                    st.caption("🛡️ **Lv10 兵種比率 (盾 : 槍 : 弓)**")
                    ratio_opt_lv10 = st.radio(
                        "Lv10 兵種選択",
                        ["10 : 0 : 0", "8 : 3 : 2", "6 : 4 : 0", "カスタム"],
                        index=0,
                        horizontal=True,
                        key="ratio_lv10"
                    )
                    if ratio_opt_lv10 == "10 : 0 : 0":
                        shield_r10, spear_r10, bow_r10 = 10.0, 0.0, 0.0
                    elif ratio_opt_lv10 == "8 : 3 : 2":
                        shield_r10, spear_r10, bow_r10 = 8.0, 3.0, 2.0
                    elif ratio_opt_lv10 == "6 : 4 : 0":
                        shield_r10, spear_r10, bow_r10 = 6.0, 4.0, 0.0
                    else:
                        c1, c2, c3 = st.columns(3)
                        shield_r10 = c1.number_input("Lv10 盾", min_value=0.0, max_value=100.0, value=8.5, step=0.1, format="%.1f", key="s10")
                        spear_r10 = c2.number_input("Lv10 槍", min_value=0.0, max_value=100.0, value=1.5, step=0.1, format="%.1f", key="p10")
                        bow_r10 = c3.number_input("Lv10 弓", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="b10")

                # --- Lv20 兵種比率 ---
                with r_col2:
                    st.caption("⚔️ **Lv20 兵種比率 (盾 : 槍 : 弓)**")
                    ratio_opt_lv20 = st.radio(
                        "Lv20 兵種選択",
                        ["10 : 0 : 0", "8 : 3 : 2", "6 : 4 : 0", "カスタム"],
                        index=0,
                        horizontal=True,
                        key="ratio_lv20"
                    )
                    if ratio_opt_lv20 == "10 : 0 : 0":
                        shield_r20, spear_r20, bow_r20 = 10.0, 0.0, 0.0
                    elif ratio_opt_lv20 == "8 : 3 : 2":
                        shield_r20, spear_r20, bow_r20 = 8.0
