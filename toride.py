import streamlit as st
import pandas as pd
import json
import os
import re
from PIL import Image
import numpy as np
import easyocr

# --- 設定・ファイルパス ---
DB_FILE = 'event_database.json'
EXCEL_FILE = 'イベント一覧.xlsx'
OTHER_EXCEL = 'その他イベント一覧.xlsx'
CONFIG_FILE = 'manual_custom_data.json'

# --- OCRリーダーの初期化 (キャッシュして高速化) ---
@st.cache_resource
def get_ocr_reader():
    # 日本語と英語に対応
    return easyocr.Reader(['ja', 'en'])

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

# --- クレジョイ用 テキストクレンジング関数 ---
def clean_member_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    
    cleaned = raw_name.strip()
    
    # UIの定型文や戦力などのノイズ文字をスキップ
    ignore_patterns = [r"投票メンバー", r"項目を選択", r"以下", r"M$", r"K$"]
    for p in ignore_patterns:
        if re.search(p, cleaned):
            return ""

    # ① 「ʕ」または「·」が含まれている場合、最初に出てきた位置から後ろをすべて削除
    match = re.search(r'[ʕ·]', cleaned)
    if match:
        cleaned = cleaned[:match.start()]
    
    # ② 残ったテキストから特殊記号を除去 (ひらがな、カタカナ、漢字、英数字、「。」を残す)
    cleaned = re.sub(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF。]', '', cleaned)
    
    # ③ 末尾に残った同盟タグ (M2C, MMC, MC) を除去
    cleaned = re.sub(r'(M2C|MMC|MC)$', '', cleaned, flags=re.IGNORECASE)
    
    # 短すぎるノイズ（1文字以下）や「R5」「R4」などのランク表記を除去
    if len(cleaned) <= 1 or re.match(r'^R[1-5]$', cleaned):
        return ""
    
    return cleaned.strip()

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
    ["スケジュールを自動で作る✨", "クレジョイ案内をつくる 🛡️", "新イベントを教え込む📝", "運営マニュアル 📜", "マニュアルを編集する ⚙️"],
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

        if st.button("案内文をポチッと生成！🚀"):
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

    col_main, _ = st.columns([10, 1])
    
    with col_main:
        st.subheader("① 画像をアップロード")
        uploaded_file = st.file_uploader("投票メンバーのスクショを選択", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            with st.expander("🖼️ アップロードした画像を確認"):
                st.image(image, use_container_width=True)
            
            # --- 実際のOCR読み取り処理 ---
            if "last_uploaded" not in st.session_state or st.session_state["last_uploaded"] != uploaded_file.name:
                with st.spinner("画像を解析中...少々お待ちください"):
                    reader = get_ocr_reader()
                    img_np = np.array(image)
                    ocr_results = reader.readtext(img_np, detail=0)
                    
                    # 抽出した文字列をクレンジング
                    parsed_members = []
                    for text in ocr_results:
                        c_name = clean_member_name(text)
                        if c_name and c_name not in parsed_members:
                            parsed_members.append(c_name)
                    
                    st.session_state["parsed_members"] = parsed_members
                    st.session_state["last_uploaded"] = uploaded_file.name

            # --- STEP 2: 読み取り結果の確認・修正 ---
            st.subheader("② メンバーの確認・修正")
            current_text = "\n".join(st.session_state.get("parsed_members", []))
            members_text = st.text_area(
                "読み取ったメンバー名 (1行に1人 / 誤字・不足があれば直接編集可)",
                value=current_text,
                height=180
            )
            member_list = [m.strip() for m in members_text.split("\n") if m.strip()]
            st.caption(f"現在の認識人数: **{len(member_list)} 名**")

            if not member_list:
                st.warning("メンバー名が認識できませんでした。上の入力欄に手動で入力してください。")
            else:
                st.divider()

                # --- STEP 3: 条件設定 ---
                st.subheader("③ 条件の設定")
                
                leader_name = st.selectbox("駐屯リーダーを選択", options=member_list)
                
                col_cap, col_own = st.columns(2)
                max_capacity = col_cap.number_input("リーダーの駐屯容量", min_value=0, value=1500000, step=50000)
                leader_troops = col_own.number_input("リーダー出陣兵数", min_value=0, value=250000, step=10000)

                ratio_option = st.radio(
                    "兵種比率 (盾 : 槍 : 弓)",
                    ["7 : 3 : 0", "6 : 4 : 0", "カスタム"],
                    horizontal=True
                )

                if ratio_option == "7 : 3 : 0":
                    shield_r, spear_r, bow_r = 7, 3, 0
                elif ratio_option == "6 : 4 : 0":
                    shield_r, spear_r, bow_r = 6, 4, 0
                else:
                    c1, c2, c3 = st.columns(3)
                    shield_r = c1.number_input("盾", 0, 10, 7)
                    spear_r = c2.number_input("槍", 0, 10, 3)
                    bow_r = c3.number_input("弓", 0, 10, 0)

                st.divider()

                # --- STEP 4: 計算＆出力 ---
                if st.button("🧮 兵士数を計算する", type="primary", use_container_width=True):
                    other_members = [m for m in member_list if m != leader_name]
                    num_others = len(other_members)
                    
                    if num_others == 0:
                        st.error("メンバーがリーダー1名しかいません。")
                    else:
                        remaining_space = max_capacity - leader_troops
                        per_person_total = remaining_space // num_others
                        
                        total_ratio = shield_r + spear_r + bow_r
                        shield_count = int(per_person_total * (shield_r / total_ratio))
                        spear_count = int(per_person_total * (spear_r / total_ratio))
                        bow_count = int(per_person_total * (bow_r / total_ratio)) if bow_r > 0 else 0

                        members_str = "、".join(other_members)

                        copy_text = f"【クレジョイ10&20駐屯】\n"
                        copy_text += f"👑駐屯リーダー: {leader_name}\n\n"
                        copy_text += f"🛡️ 1人あたりの派遣数\n"
                        copy_text += f"⭐ 左英雄: ジェシー\n"
                        copy_text += f"合計: {per_person_total:,}\n"
                        
                        if bow_r == 0:
                            copy_text += f"├ 盾兵: {shield_count:,} ({shield_r})\n"
                            copy_text += f"└ 槍兵: {spear_count:,} ({spear_r})\n\n"
                        else:
                            copy_text += f"├ 盾兵: {shield_count:,} ({shield_r})\n"
                            copy_text += f"├ 槍兵: {spear_count:,} ({spear_r})\n"
                            copy_text += f"└ 弓兵: {bow_count:,} ({bow_r})\n\n"
                            
                        copy_text += f"📋 対象メンバー ({num_others}名)\n"
                        copy_text += f"{members_str}"
                        
                        st.success("計算完了！枠内を長押し・タップでコピーできます")
                        st.code(copy_text, language="text")

# ==========================================
# 3. イベント追加画面
# ==========================================
elif app_mode == "新イベントを教え込む📝":
    st.title("📝 期間限定イベントを覚えさせる")
    tab1, tab2 = st.tabs(["🏆 ランキング型", "🎁 報酬型"])
    with tab1:
        st.info("※恒常イベントはエクセルを編集して保存するだけでOKだよ！")
        input_days = st.slider("開催日数", 1, 7, 3, key="ranking_days_slider")
        with st.form("add_event_form"):
            new_name = st.text_input("イベント名")
            all_items = ["火晶建築", "領主装備", "領主宝石", "訓練昇格", "英雄欠片", "各種加速", "採集", "ペット", "ダイヤ", "専門家", "専装エナ", "ミスリル", "ルーレット", "鍵", "獣"]
            new_sched = {f"{d}日目": st.multiselect(f"{d}日目", all_items, key=f"new_d_input_{d}") for d in range(1, input_days + 1)}
            if st.form_submit_button("サーバーに保存！✨"):
                if new_name:
                    db[new_name] = {"スケジュール": new_sched}
                    save_db(db)
                    st.success(f"『{new_name}』を保存しました！")
                    st.rerun()
                else: st.error("名前を入れてね！")
    with tab2:
        st.subheader("🎁 報酬型イベントの追加")
        with st.form("add_other_event_form"):
            name = st.text_input("イベント名")
            cat = st.selectbox("カテゴリー", ["高頻度", "要エントリーイベント", "その他イベント"])
            if st.form_submit_button("報酬型リストに追加！🚀"):
                if name:
                    try:
                        df_o = pd.read_excel(OTHER_EXCEL) if os.path.exists(OTHER_EXCEL) else pd.DataFrame(columns=['カテゴリー', 'イベント名'])
                        df_o.columns = ['カテゴリー' if 'カテゴリ' in str(c) else c for c in df_o.columns]
                        df_o = pd.concat([df_o, pd.DataFrame([{'カテゴリー': cat, 'イベント名': name}])], ignore_index=True).drop_duplicates()
                        df_o.to_excel(OTHER_EXCEL, index=False)
                        st.success(f"『{name}』を追加しました！")
                        st.rerun()
                    except Exception as e: st.error(f"保存エラー: {e}")
                else: st.error("イベント名を書いてね！")

# ==========================================
# 4. マニュアル閲覧画面
# ==========================================
elif app_mode == "運営マニュアル 📜":
    st.title("📜 MMC 運営マニュアル")
    custom_data = load_custom_data()
    tab1, tab2, tab3 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略"])

    with tab1:
        with st.expander("1. 新規加入の審査基準"):
            st.markdown("""申請一覧を確認し、以下の条件を**すべて**満たす場合のみ承認します。  
            - **炉レベル**: 25以上  
            - **総力**: 3000万以上  
            - **名前**: 初期ネーム以外  
            - **⚠️ IDチェック**: 74始まりに注意！スパイの可能性があるため、承認前に個別メッセージで挨拶を送り、意思疎通（日本語が通じるか等）ができるか慎重に確認する。""")

        with st.expander("2. 入会後のランクアップ（R1 ➡ R3）"):
            st.markdown("""新メンバーが入会したら、以下のステップをガイドし、完了を確認したらR3へ昇格させます。  
            - **フレンド登録**: 盟主（R5）へフレンド申請を送るよう指示する。  
            - **移転**: 同盟本部の周辺へ移転してもらう。  
            - **ランクアップ**: 上記2点が確認できたら、R1からR3へ手動で変更する。  
            - **同盟マークの案内**: 名前の後ろに同盟マークをつけてもらうようにうながす。""")
            st.code("""よかったら、名前の後ろに「ʕ·ᴥ·ʔᴹᴹᶜ」をつけて、MMCの仲間だよってアピールいただけないでしょうか。

【付け方】  
左上アイコンタッチ
⇒名前の変更  
同盟ショップで、改名カードの割引があったら買ってから、おねがいします😊""", language=None)
            st.code("""ʕ·ᴥ·ʔᴹᴹᶜ""", language=None)

        with st.expander("3. 非アクティブ者の整理"):
            st.markdown("""同盟の枠を確保し、アクティブ率を維持するための運用です。  
            **【基本ルール】**  
            長期未ログインにより自動（または手動）で**R2に降格したメンバー**が対象。  
            **【退会処置の手順】**  
            - 対象者のプロフィールから最終ログイン時間を確認。  
            - 個別メールを送信。   
            - メール送信後、同盟から追放（退会）処理。""")
            st.code("""お疲れ様です。長期未ログインのため、一旦同盟を離脱していただく形となります。
また戻られた際には、再度申請してくださいね～😊 歓迎します！""", language=None)

        with st.expander("4. 規律・コミュニケーション管理"):
            st.markdown("""イベント時などのトラブル対応指針です。  
            **【対象】**:  
            イベントでのルール違反（例：攻撃禁止対象への攻撃等）を行った者。  
            **【対応フロー】**:  
            - 同盟チャットまたは個別チャット（DM）で状況を確認し、注意を促す。  
            - **応答がない（意思疎通が取れない）場合**: 速やかに**R1に降格**させる。   
            - その後も改善や連絡がない場合は、盟主に報告し、追放を検討する。""")
            
        with st.expander("5. ホワイトリストの管理（※盟主専用業務）"):
            st.markdown("""この操作はシステムの仕様上、**盟主（R5）のみ**が行います。  
            R4以下は、変更が必要な事案が発生した場合、速やかに詳細（理由と対象）を盟主へ報告してください。  
            **【事例】**:  
            - MMCおよびmmc間、その他同盟支援で他同盟に移動する可能性がある者。  
            - SVS等で他同盟との集結主を兼ねる者。""")

        for exp in custom_data["👥 メンバー管理"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

    with tab2:
        with st.expander("1. ルート作成と旗建設"):
            st.markdown("""領土は「最短距離」かつ「最大効率」で広げるのが基本です。  
            **【基本ルートの考え方】**:  
            - マップ上の同盟資源地を目指して、最短ルートで旗を伸ばします。  
            - イベント対象となる施設（ステーション、砦等）に隣接させるようにルートを設計します。  
            **【効率化のテクニック】**:  
            - 山や川などの通行不能エリアを避け、旗の消費数を最小限に抑えます。  
            - 外交上のNAP（不戦条約）に基づき、他同盟も旗を跨げるように、ジグザグにルートを引きます。  
            """)
        
        with st.expander("2. パズル進行用「兵1旗」"):
            st.markdown("""同盟パズルの「旗建設」タスクを効率よく回すための特殊運用です。  
            **【建設設定】**:  
            - 旗の建設を開始する際、必ず「兵士1名・英雄なし」の部隊1隊のみで建設を開始します。  
            - 目的は「あえて建設時間を長くし、多くのメンバーが支援（ヘルプ）やパズル進行に関与できるようにすること」です。  
            **【監視とアナウンス】**:  
            - 建設中の旗を確認し、「兵士1名以外」または「英雄入り」の部隊を送っているメンバーがいた場合、同盟チャットで以下のようにアナウンスし、該当部隊を強制送還させます。  
            **【再設置ループ】**:  
            - 旗の建設が完了（100%）してしまったら、その旗を即座に解体（破壊）します。  
            - 解体後、再度同じ場所に「兵士1・英雄なし」で旗を建設し、ループを継続させます。  
            """)
            st.code("""パズル用の旗なので、兵士1・英雄なしでお願いします😊
一旦送還しますね。""", language=None)

        with st.expander("3. 同盟安全採集ポイントの設置"):
            st.markdown("""何人でも駐屯できる12時間の採集ポイントです。  
            **【作業】**:  
            - 前と同じ場所をマップ上でタップ  
            - ⇒建設  
            - ⇒同盟領地  
            - ⇒特殊建築  
            - ⇒同盟安全採集ポイント  
            - ⇒マップの座標を同盟チャットで共有  
            """)

        for exp in custom_data["🚩 領土・資源"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

    with tab3:
        with st.expander("1. 熊狩り"):
            st.markdown("""クマで参加者全員のポイントを伸ばすための考え方です。  
            - 基本的には罠の近くに集結主がいた方がいいです。  
            - 罠強化を忘れないようにアナウンスしましょう。  
            """)
            st.code("""🐻今日は熊狩り🐻
【時間】
くま2 21:00〜
くま1 22:00〜
【攻め方】 
🚩 集結を出す人：自分の1番強い英雄でお願いします！✨ 
🚩 集結に乗る人：左英雄はジェシー・ジャセル・ソユン・ジェロニモ・フレンダーを！強い人のところに乗っかるとダメージ伸びるよ💪 
兵士割合は「弓」を多めにするのがコツです（盾2槍2弓6、盾1槍2弓7など）🏹 
みんなでダメージ出していこー！楽しもー！🎶 """, language=None)

        with st.expander("2. 峡谷合戦 / 兵器工場争奪戦 （事前登録）"):
            st.markdown("""この業務の最大の敵は「忘れ」です。  
            **【時間枠の登録（R4以上）】**:  
            - **タイミング**: まずは「参加しやすい時間」のアンケート結果から、時間を設定します。  
            - **操作**: イベント画面から、候補となる時間枠（軍団1：23時、軍団2：21時など）を選択してポチります。  
            - **周知**: 登録完了後、メンバーに「参戦志願」をポチるよう促します。  
            **【参加者の選抜】**:  
            - **基準**: 「参戦志願」を押している人を選抜します。  
            - **欠員厳禁**: 「参戦志願した方は当日絶対参加」であることを改めて念押しします。  
            - **メンバー補充**: 15名に達しないとエントリーできません！軍団１（ガチな方）は候補時間枠の投票をしてくれた人の上位から順に補充し、軍団２は総力下位から順に補充します。 
            """)
            st.code("""🏹兵器工場争奪戦🏹
貴重な領主装備アイテムを手に入れる大チャンス✨ 絶対勝つよー！💪 
別マップで行われる60分のイベント
王国ルール適応外。都市攻撃されるし、やります🔥
ポチポチ回復出来ません、回復加速アイテム必須（同盟ショップ）

軍団2 21時
軍団1 23時

どちらか選んで、出撃管理→参戦志願を押して下さい（R4は自分でチェック）""", language=None)
            st.code("""🔥峡谷合戦🔥
3同盟間で争うイベント
軍団1 23:00-24:00
軍団2 21:00-22:00
・マップ内の各拠点（建物）を占領すると継続的にポイントが加算
・最終的にポイントが多い同盟が勝利
・氷封宮殿を最後に支配してたら5万ポイント追加
・ダイヤ加速、進軍加速アリ""", language=None)
            st.code("""〜燃料の使い方〜
燃料は時間経過で回復
・移動
→キョリによって燃料消費が変化・徴兵→戦闘後に部隊の回復で使用・即時回復→倒されて本部に戻った部隊を即時回復❌燃料の使いすぎには注意しよう！動きたい時には動けなくなります！

""", language=None)

        with st.expander("3. 同盟争覇戦"):
            st.markdown("""この業務の最大の敵は「忘れ」です。  
            **【ルートの設定】**:  
            - **タイミング**: エントリー〆切から数時間以内に、ルートを変更します。  
            - **操作**: 7:59までに全員に真ん中にエントリーするように促します。その後、ルート変更から、左右中央のルートに割り振ります。どのルートにどう割り振るかは戦略次第となるので、担当者は要確認です。  
            """)
            st.code("""⭕同盟争覇戦⭕
①英雄は、ジーナ抜きの最強。ジーナが最強の装備をしてる時は、付け替えてね
②兵士配分は基本613。足りない時は、それに近づけるように調整
③エントリーは、真ん中にお願いします。真ん中で固めると、弱い相手がマッチングされる？らしい。マッチングが終わってから、R4と私でコース分けます。
④受付ギリギリに再エントリー、最初にエントリーしてから、数日すると、英雄がレベルアップしたり、強い兵士が増えてたりします。なので【2/18 朝8時】までのギリギリの時間で再エントリーお願いします
⑤色々めんどくさいし、よく分からん！という方は、真ん中に最強でエントリーでOKです🎶
兵士配分については、盾兵-槍兵-弓兵を6-1-3の割合にしたり5-2-3の割合にすることが大事です

ただ、そうすると見習いとかのレベル低い兵士入っちゃう…と言う方は、紫兵とか青兵のレベル高い兵士入れた方が強いので、割合無視して強い兵士入れましょう💪
""", language=None)

        with st.expander("4. 城砦・要塞戦（作戦立案・配置）"):
            st.markdown("""「どこを」「誰が」攻めるかを明確に伝達し、無駄な衝突を避けます。  
            **【ターゲット選定】**:  
            - 王国ルール（1同盟1要塞2砦まで等）に基づき、狙う施設を決定します。  
            - あらかじめ、どの報酬を狙いに行くか、アンケートを立てましょう！。  
            - そして、盟主会にどの砦を狙いに行くか、宣言します。（要塞は非公開）  
            **【部隊配置（集結主の指名）】**:  
            - 参加意思の確認のため、当日、アンケートを実施します。  
            - 各施設に、同盟内で一番「ハコ（集結規模）」と「戦力」がある人を集結主として割り振ります。  
            - 同時間帯に２か所の砦戦がある場合は、事前にメンバーを割り振りましょう。
            - あらかじめ座標を同盟チャットに共有しておきます。  
            - 早押しが得意なメンバーと二人体制でもいいかもしれません！  
            **【報酬分配】**:  
            - 砦もしくは要塞の建物をタップすると、貢献ランキングが確認できます。  
            - ランキングに乗っている人に割り振ります。  
            - 同盟⇒拠点争奪⇒報酬
            - 23時に砦2か所重なっていた！となっていたら、別の砦を担当していた方にも割り振ってあげましょう。  
            """)
            st.code("""初手は「集結」のみです！ソロ突撃は禁止だよ〜🙅‍♀️ 
他の方は左ジェシーで乗ってくださいね！絶対勝つよー！💪✨
""", language=None)

        with st.expander("5. クレジョイ"):
            st.markdown("""参加意思の確認のため、当日、アンケートを実施します。  
            """)
            st.code("""🔥クレジョイ🔥
今日はクレジョイ！みんなで守りきるよー！🛡️✨
🚩〜17:00 参加確認投票中
🚩〜19:00 ラスト本部防衛メンバー発表
🚩〜21:00 ラストメンバーは部隊作成→保存
🚩 21:00〜 兵士交換スタート！同盟チャットに座標貼ってね！
🚩 21:30〜 クレジョイ開始！🔥""", language=None)
            st.code("""【ラスト本部防衛メンバーへ】 
100,000の「盾兵だけ」の部隊を保存しておいてください！弓は入れないでね🙅‍♀️ 
領主ファイル→部隊→部隊編成→好きな番号に保存""", language=None)
            st.code("""【オフライン参加】
オフライン参加の人も、事前に兵士を交換して「都市を空」にするのを忘れずに！😊 
投票に参加してなくても、参加可能です🎶
フェーズ7,14,17はオンラインの人のみ！7,14,17で不在の方はオフラインにしてくださいね🎵

【兵士の送り方】
同盟→メンバー→部隊援助

兵士を交換しない、都市を空にしない方は、見学となります""", language=None)

        with st.expander("6. キルイベ"):
            st.markdown("""ルールが複雑なイベントです。  
            - ルール違反を目撃した場合は、同盟チャット・個別チャット等で指摘をしましょう。  
            - 幹部チャットで報告し、盟主もしくは盟主代行が相手および相手盟主に謝罪に伺いましょう。※要事前確認  
            - 違反者に、何を間違えたか理解してもらいましょう。
            """)
            st.code("""🏹全軍参戦（キルイベ）🏹
明日9時からキルイベです！
サーバールール順守🔥""", language=None)
            st.code("""🏹9時以降は通常ルールです🏹
キルイベ終了後（9時以降）は通常ルールに戻ります🎵
【3917サーバー通常ルール(2/3改定)】
・都市攻撃（同盟未加入も）禁止
・誰に対しても偵察                 禁止
・資源採集者への攻撃             禁止       
・同盟の建物への攻撃             禁止
・ステーション戦への別同盟員の戦力貸し禁止
→ただし、留学中（付随文参照）の人は参加○
・旗立ては、他同盟が跨げるように配慮する
(連続して建てる場合他の旗で調整お願いします)
・旗のステ接続は2本まで(本部は2本分)
→多くの同盟が接続出来るように協力※即時報復禁止。先ずは盟主同士で話し合い。
""", language=None)

        with st.expander("7. 烈火と牙"):
            st.markdown("""案内文のみ。  
            """)
            st.code("""🔥烈火と牙イベント🔥
火晶がもらえるからぜひ参加してね🎵

イベントは月曜9:00（UTC基準）に開始し、3日間続きます。
日曜17:00と25:00の灯台をクリアするが報酬は受け取らず保留にする。
1日目（月曜）
9:00以降に保留分をまとめて受け取り、新規灯台処理。灼熱巨獣出現時は即討伐。
2日目
3回の更新を逃さず処理し、掃討機能があれば活用。
交換フェーズ
溜まった晶核をイベント画面で期限内に使い切る。

""", language=None)

        with st.expander("8. 採集案内"):
            st.markdown("""案内文のみ。  
            """)
            st.code("""🍖明日は採集ポイント🍖
採集バフ（ダイヤ）
マップに出て、自分の都市タッチ→都市強化→発展→採集速度
""", language=None)

        for exp in custom_data["⚔️ イベント攻略"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

# ==========================================
# 5. マニュアル編集画面
# ==========================================
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
                with c1: block['type'] = st.selectbox("種別", ["text", "code"], index=0 if block['type'] == 'text' else 1, key=f"ty_{category}_{e_idx}_{b_idx}")
                with c2: block['content'] = st.text_area("内容", block['content'], key=f"cn_{category}_{e_idx}_{b_idx}")
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
        st.success("マニュアルを更新しました！")
