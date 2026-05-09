import streamlit as st
import json
import os

# --- 1. データの読み書き設定（カスタム追加分） ---
CONFIG_FILE = 'manual_custom_data.json'

def load_custom_data():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"👥 メンバー管理": [], "🚩 領土・資源": [], "⚔️ イベント攻略": []}

def save_custom_data(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. マニュアル閲覧画面 ---
# --- 2. マニュアル閲覧画面 ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")
    
    # カスタムデータの読み込み
    custom_data = load_custom_data()
    
    tab1, tab2, tab3 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略"])

    # --- タブ1: メンバー管理 ---
    with tab1:
        # 1. 固定部分
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
            st.code("""よかったら、名前の後ろに「ʕ·ᴥ·ʔᴹᴹᶜ」をつけて、MMCの仲間だよってアピールいただけないでしょうか。\n\n【付け方】  \n左上アイコンタッチ\n⇒名前の変更  \n同盟ショップで、改名カードの割引があったら買ってから、おねがいします😊""", language=None)
            st.code("""ʕ·ᴥ·ʔᴹᴹᶜ""", language=None)

        with st.expander("3. 非アクティブ者の整理"):
            st.markdown("""同盟の枠を確保し、アクティブ率を維持するための運用です。  
            **【基本ルール】** 長期未ログインにより自動（または手動）で**R2に降格したメンバー**が対象。  
            **【退会処置の手順】** - 対象者のプロフィールから最終ログイン時間を確認。  
            - 個別メールを送信。    
            - メール送信後、同盟から追放（退会）処理。""")
            st.code("""お疲れ様です。長期未ログインのため、一旦同盟を離脱していただく形となります。\nまた戻られた際には、再度申請してくださいね～😊 歓迎します！""", language=None)

        with st.expander("4. 規律・コミュニケーション管理"):
            st.markdown("""イベント時などのトラブル対応指針です。  
            **【対象】**: イベントでのルール違反（例：攻撃禁止対象への攻撃等）を行った者。  
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

        # 🌟 管理画面から追加した項目を「並列」に表示（見出しや線を削除）
        for exp in custom_data["👥 メンバー管理"]:
            # タイトルに「✨」をつけて管理分だと分かるようにしていますが、不要なら削除してください
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

    # --- タブ2: 領土・資源 ---
    with tab2:
        with st.expander("1. ルート作成と旗建設"):
            st.markdown("""領土は「最短距離」かつ「最大効率」で広げるのが基本です。  
            **【基本ルートの考え方】**:  
            - マップ上の同盟資源地を目指して、最短ルートで旗を伸ばします。  
            - イベント対象となる施設（ステーション、砦等）に隣接させるようにルートを設計します。  
            **【効率化のテクニック】**:  
            - 山や川などの通行不能エリアを避け、旗の消費数を最小限に抑えます。  
            - 外交上のNAP（不戦条約）に基づき、他同盟も旗を跨げるように、ジグザグにルートを引きます。""")

        with st.expander("2. パズル進行用「兵1旗」"):
            st.markdown("""同盟パズルの「旗建設」タスクを効率よく回すための特殊運用です。  
            **【建設設定】**:  
            - 旗の建設を開始する際、必ず「兵士1名・英雄なし」の部隊1隊のみで建設を開始します。  
            - 目的は「あえて建設時間を長くし、多くのメンバーが支援（ヘルプ）やパズル進行に関与できるようにすること」です。  
            **【監視とアナウンス】**:  
            - 建設中の旗を確認し、「兵士1名以外」または「英雄入り」の部隊を送っているメンバーがいた場合、同盟チャットでアナウンス。  
            **【再設置ループ】**:  
            - 旗の建設が完了（100%）してしまったら、その旗を即座に解体（破壊）し、再建設のループを継続させます。""")
            st.code("""パズル用の旗なので、兵士1・英雄なしでお願いします😊\n一旦送還しますね。""", language=None)

        with st.expander("3. 同盟安全採集ポイントの設置"):
            st.markdown("""何人でも駐屯できる12時間の採集ポイントです。  
            **【作業】**:  
            - 前と同じ場所をタップ⇒建設⇒同盟領地⇒特殊建築 ⇒ 同盟安全採集ポイント ⇒ 座標共有""")

        # 🌟 管理画面から追加した項目を並列に表示
        for exp in custom_data["🚩 領土・資源"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)

    # --- タブ3: イベント攻略 ---
    with tab3:
        # (固定の expander 1〜8 はそのまま)
        with st.expander("1. 熊狩り"):
            st.markdown("""クマで参加者全員のポイントを伸ばすための考え方です。  
            - 基本的には罠の近くに集結主がいた方がいいです。  
            - 罠強化を忘れないようにアナウンスしましょう。""")
            st.code("""🐻今日は熊狩り🐻\n【時間】くま2 21:00〜 / くま1 22:00〜\n🚩 集結主：最強英雄で！\n🚩 乗る人：左ジェシー等。弓多め🏹""", language=None)

        # ... (中略：他のイベント expander) ...

        # 🌟 管理画面から追加した項目を並列に表示
        for exp in custom_data["⚔️ イベント攻略"]:
            with st.expander(exp['title']):
                for block in exp.get('blocks', []):
                    if block['type'] == 'text': st.markdown(block['content'])
                    else: st.code(block['content'], language=None)
# --- 3. 管理者画面 ---
def admin_page():
    st.title("🛠️ マニュアル構造の編集")
    data = load_custom_data()
    category = st.selectbox("編集するカテゴリ", list(data.keys()))
    expanders = data[category]
    
    for e_idx, exp in enumerate(expanders):
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                exp['title'] = st.text_input("折り畳みのタイトル", value=exp['title'], key=f"title_{category}_{e_idx}")
            with col2:
                if st.button("🗑️ 削除", key=f"del_exp_{category}_{e_idx}"):
                    expanders.pop(e_idx)
                    save_custom_data(data)
                    st.rerun()
            for b_idx, block in enumerate(exp.get('blocks', [])):
                c1, c2, c3 = st.columns([1, 4, 0.5])
                with c1:
                    block['type'] = st.selectbox("種類", ["text", "code"], index=0 if block['type'] == 'text' else 1, key=f"type_{category}_{e_idx}_{b_idx}")
                with c2:
                    block['content'] = st.text_area("内容", value=block['content'], key=f"content_{category}_{e_idx}_{b_idx}", height=100)
                with c3:
                    if st.button("❌", key=f"del_block_{category}_{e_idx}_{b_idx}"):
                        exp['blocks'].pop(b_idx)
                        save_custom_data(data)
                        st.rerun()
            if st.button("➕ パーツを追加 (text/code)", key=f"add_block_{category}_{e_idx}"):
                exp['blocks'].append({"type": "text", "content": ""})
                save_custom_data(data)
                st.rerun()

    st.divider()
    if st.button("✨ 新しい折り畳み(expander)を追加"):
        expanders.append({"title": "新規見出し", "blocks": [{"type": "text", "content": ""}]})
        save_custom_data(data)
        st.rerun()

    if st.button("💾 保存してバックアップを表示"):
        save_custom_data(data)
        st.success("一時保存完了！")
        with st.expander("📥 GitHub保存用データ"):
            st.code(json.dumps(data, ensure_ascii=False, indent=4), language="json")

# --- メインメニュー ---
st.sidebar.title("ʕ·ᴥ·ʔ MMC Menu")
menu = st.sidebar.radio("メニュー", ["マニュアル閲覧📜", "管理者設定🛠️"])

if menu == "マニュアル閲覧📜":
    manual_view_page()
else:
    admin_page()
