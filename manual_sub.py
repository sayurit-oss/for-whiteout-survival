import streamlit as st
import json
import os

# --- 1. 管理画面から編集するデータの読み書き ---
MANUAL_EXT_FILE = 'manual_extra.json'

def load_extra():
    if os.path.exists(MANUAL_EXT_FILE):
        with open(MANUAL_EXT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"👥 メンバー管理": "", "🚩 領土・資源": "", "⚔️ イベント攻略": ""}

def save_extra(data):
    with open(MANUAL_EXT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. マニュアル閲覧画面（ご提示のコード ＋ 追加機能エリア） ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")
    
    # 追加情報の読み込み
    extra_data = load_extra()

    tab1, tab2, tab3 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略"])

    with tab1:
        # 🌟 管理画面から追加したテキストがここに出ます
        if extra_data.get("👥 メンバー管理"):
            st.warning(extra_data["👥 メンバー管理"])
            st.divider()

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
            **【基本ルール】** 長期未ログインにより自動（または手動）で**R2に降格したメンバー**が対象。  
            **【退会処置の手順】** - 対象者のプロフィールから最終ログイン時間を確認。  
            - 個別メールを送信。    
            - メール送信後、同盟から追放（退会）処理。""")
            st.code("""お疲れ様です。長期未ログインのため、一旦同盟を離脱していただく形となります。
また戻られた際には、再度申請してくださいね～😊 歓迎します！""", language=None)

        # (以下、規律管理やホワイトリストなどの expander を同様に配置)

    with tab2:
        # 🌟 領土・資源の追加情報エリア
        if extra_data.get("🚩 領土・資源"):
            st.info(extra_data["🚩 領土・資源"])
            st.divider()

        with st.expander("1. ルート作成と旗建設"):
            st.markdown("""領土は「最短距離」かつ「最大効率」で広げるのが基本です。  
            **【基本ルートの考え方】**:  
            - マップ上の同盟資源地を目指して、最短ルートで旗を伸ばします。  
            - イベント対象となる施設（ステーション、砦等）に隣接させるようにルートを設計します。  
            **【効率化のテクニック】**:  
            - 山や川などの通行不能エリアを避け、旗の消費数を最小限に抑えます。  
            - 外交上のNAP（不戦条約）に基づき、他同盟も旗を跨げるように、ジグザグにルートを引きます。""")
        
        # (以下、兵1旗や採集ポイントの expander を配置)

    with tab3:
        # 🌟 イベント攻略の追加情報エリア
        if extra_data.get("⚔️ イベント攻略"):
            st.success(extra_data["⚔️ イベント攻略"])
            st.divider()

        with st.expander("1. 熊狩り"):
            st.markdown("""クマで参加者全員のポイントを伸ばすための考え方です。  
            - 基本的には罠の近くに集結主がいた方がいいです。  
            - 罠強化を忘れないようにアナウンスしましょう。""")
            st.code("""🐻今日は熊狩り🐻 ... (略)""", language=None)

        # (以下、各種イベントの expander を配置)

# --- 3. 追加機能のための管理画面 ---
def admin_page():
    st.title("🛠️ マニュアル補足事項の編集")
    extra_data = load_extra()

    category = st.selectbox("編集するカテゴリ", list(extra_data.keys()))
    
    st.write(f"### 「{category}」の冒頭に表示するメッセージ")
    new_text = st.text_area("ここに入力した内容は、マニュアルの各タブの最初に表示されます。", 
                            value=extra_data[category], height=150)

    if st.button("💾 保存して反映"):
        extra_data[category] = new_text
        save_extra(extra_data)
        st.success("更新しました！マニュアル画面を確認してください。")
