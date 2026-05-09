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
                        caution_msg = f"\n⚠️**温存推奨アイテム**⚠️\n{', '.join(matches)}\n（{i+1}日後から {f_ev}）"
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
                output += f"\n🔥**おすすめアイテム**🔥\n{', '.join(doubled)}\n（イベント間で重複）\n"
            output += caution_msg
            st.divider()
            st.subheader("📋 生成された案内文")
            st.caption("右上のボタンをタップしてコピー！")
            st.code(output, language=None)

# --- 2. イベント追加画面 ---
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

# --- 3. マニュアル閲覧画面 (固定コード組み込み版) ---
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
            - **⚠️ IDチェック**: 74始まりに注意！スパイの可能性があるため、承認前に個別メッセージで挨拶を送り、意思疎通ができるか慎重に確認する。""")
        with st.expander("2. 入会後のランクアップ（R1 ➡ R3）"):
            st.markdown("""新メンバーが入会したら、以下のステップをガイドし、完了を確認したらR3へ昇格させます。  
            - **フレンド登録**: 盟主（R5）へフレンド申請を送るよう指示する。  
            - **移転**: 同盟本部の周辺へ移転してもらう。  
            - **ランクアップ**: 上記2点が確認できたら、R1からR3へ手動で変更する。  
            - **同盟マークの案内**: 名前の後ろに同盟マークをつけてもらうようにうながす。""")
            st.code("""よかったら、名前の後ろに「ʕ·ᴥ·ʔᴹᴹᶜ」をつけて、MMCの仲間だよってアピールいただけないでしょうか。
【付け方】  
左上アイコンタッチ ⇒ 名前の変更  
同盟ショップで、改名カードの割引があったら買ってから、おねがいします😊""", language=None)
            st.code("""ʕ·ᴥ·ʔᴹᴹᶜ""", language=None)
        with st.expander("3. 非アクティブ者の整理"):
            st.markdown("""長期未ログインにより自動（または手動）で**R2に降格したメンバー**が対象。  
            **【退会処置の手順】** - 対象者のプロフィールから最終ログイン時間を確認。  
            - 個別メールを送信。  
            - メール送信後、同盟から追放（退会）処理。""")
            st.code("""お疲れ様です。長期未ログインのため、一旦同盟を離脱していただく形となります。
また戻られた際には、再度申請してくださいね～😊 歓迎します！""", language=None)
        with st.expander("4. 規律・コミュニケーション管理"):
            st.markdown("""**【対応フロー】**:  
            - 同盟チャットまたは個別チャット（DM）で状況を確認し、注意を促す。  
            - **応答がない場合**: 速やかに**R1に降格**させる。  
            - その後も改善がない場合は、盟主に報告し、追放を検討する。""")
        with st.expander("5. ホワイトリストの管理（※盟主専用業務）"):
            st.markdown("""この操作はシステムの仕様上、**盟主（R5）のみ**が行います。  
            R4以下は、変更が必要な事案が発生した場合、速やかに詳細（理由と対象）を盟主へ報告してください。""")
        
        # カスタム項目
        for exp in custom_data["👥 メンバー管理"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

    with tab2:
        with st.expander("1. ルート作成と旗建設"):
            st.markdown("""領土は「最短距離」かつ「最大効率」で広げるのが基本です。  
            - 同盟資源地を目指して最短ルートで旗を伸ばします。  
            - 旗の消費数を最小限に抑えるよう設計します。""")
        with st.expander("2. パズル進行用「兵1旗」"):
            st.markdown("""同盟パズルの「旗建設」タスクを効率よく回すための特殊運用です。  
            - 旗の建設を開始する際、必ず「兵士1名・英雄なし」で開始します。  
            - 建設が完了したら即座に解体し、再度同じ場所に建設してループさせます。""")
            st.code("""パズル用の旗なので、兵士1・英雄なしでお願いします😊 一旦送還しますね。""", language=None)
        with st.expander("3. 同盟安全採集ポイントの設置"):
            st.markdown("""特殊建築 ⇒ 同盟安全採集ポイント を設置し、座標をチャットで共有します。""")
        
        # カスタム項目
        for exp in custom_data["🚩 領土・資源"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

    with tab3:
        with st.expander("1. 熊狩り"):
            st.markdown("""罠の近くに集結主が集まり、罠強化をアナウンスします。""")
            st.code("""🐻今日は熊狩り🐻
🚩 集結を出す人：自分の1番強い英雄で！  
🚩 集結に乗る人：ジェシー・ジャセル・ソユン等を！強い人のところに乗るとダメージ伸びるよ💪  
弓兵多め（盾1槍2弓7など）🏹がコツです！""", language=None)
        with st.expander("2. 峡谷合戦 / 兵器工場争奪戦"):
            st.markdown("""アンケートに基づきR4が時間枠を登録。志願者を選抜し、欠員厳禁を念押しします。""")
            st.code("""🏹兵器工場争奪戦🏹 60分のイベント。回復加速アイテム必須！""", language=None)
        with st.expander("3. 同盟争覇戦"):
            st.markdown("""〆切後にルートを変更。「真ん中にエントリー」を推奨し、後で振り分けます。""")
            st.code("""⭕同盟争覇戦⭕ 兵士配分は基本613。真ん中に最強でエントリーでOKです🎶""", language=None)
        with st.expander("4. 城砦・要塞戦"):
            st.markdown("""ターゲットを盟主会で宣言。集結主を指名し、貢献者に報酬を分配します。""")
        with st.expander("5. クレジョイ"):
            st.code("""🔥クレジョイ🔥 21:00〜 兵士交換スタート！ 21:30〜 開始！🔥""", language=None)
        with st.expander("6. キルイベ"):
            st.markdown("""サーバールール順守。違反時は盟主同士で話し合い。""")
        with st.expander("7. 烈火と牙"):
            st.code("""🔥烈火と牙イベント🔥 火晶がもらえるから参加してね🎵""", language=None)
        with st.expander("8. 採集案内"):
            st.code("""🍖明日は採集ポイント🍖 採集バフを忘れずに！""", language=None)

        # カスタム項目
        for exp in custom_data["⚔️ イベント攻略"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

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
