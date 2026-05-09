import streamlit as st
import json
import os

# --- 1. データの読み書き設定 ---
MANUAL_EXT_FILE = 'manual_extra.json'

def load_extra():
    """管理画面から入力した補足情報を読み込む"""
    try:
        if os.path.exists(MANUAL_EXT_FILE):
            with open(MANUAL_EXT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    # ファイルがない、または読み込めない時の初期値
    return {"👥 メンバー管理": "", "🚩 領土・資源": "", "⚔️ イベント攻略": ""}

def save_extra(data):
    """管理画面から入力した補足情報を保存する"""
    with open(MANUAL_EXT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. マニュアル閲覧画面 ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")
    
    extra_data = load_extra()
    tab1, tab2, tab3 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略"])

    # --- タブ1: メンバー管理 ---
    with tab1:
        if extra_data.get("👥 メンバー管理"):
            st.warning(extra_data["👥 メンバー管理"])
            st.divider()

        with st.expander("1. 新規加入の審査基準"):
            st.markdown("""
            申請一覧を確認し、以下の条件を**すべて**満たす場合のみ承認します。  
            - **炉レベル**: 25以上  
            - **総力**: 3000万以上  
            - **名前**: 初期ネーム以外  
            - **⚠️ IDチェック**: 74始まりに注意！スパイの可能性があるため、承認前に個別メッセージで挨拶を送り、意思疎通ができるか慎重に確認する。
            """)

        with st.expander("2. 入会後のランクアップ（R1 ➡ R3）"):
            st.markdown("""
            新メンバーが入会したら、以下のステップをガイドし、完了を確認したらR3へ昇格させます。  
            - **フレンド登録**: 盟主（R5）へフレンド申請を送る。  
            - **移転**: 同盟本部の周辺へ移転してもらう。  
            - **ランクアップ**: 確認後、R1からR3へ手動で変更。
            """)
            st.code("""よかったら、名前の後ろに「ʕ·ᴥ·ʔᴹᴹᶜ」をつけて、MMCの仲間だよってアピールいただけないでしょうか。
【付け方】
左上アイコンタッチ ⇒ 名前の変更
同盟ショップで、改名カードの割引があったら買ってから、おねがいします😊""", language=None)
            st.code("ʕ·ᴥ·ʔᴹᴹᶜ", language=None)

        with st.expander("3. 非アクティブ者の整理"):
            st.markdown("""
            長期未ログインにより自動（または手動）で**R2に降格したメンバー**が対象。  
            1. 最終ログイン時間を確認。
            2. 個別メールを送信後、退会処理。
            """)
            st.code("""お疲れ様です。長期未ログインのため、一旦同盟を離脱していただく形となります。
また戻られた際には、再度申請してくださいね～😊 歓迎します！""", language=None)

        with st.expander("4. 規律・コミュニケーション管理"):
            st.markdown("""
            - ルール違反者にはチャットやDMで注意。
            - **応答がない場合**: 速やかに**R1に降格**。改善がなければ盟主に報告し追放検討。
            """)

        with st.expander("5. ホワイトリストの管理（※盟主専用）"):
            st.markdown("""
            システムの仕様上、**盟主（R5）のみ**が行います。
            R4以下は、変更が必要な事案が発生した場合、盟主へ報告してください。
            """)

    # --- タブ2: 領土・資源 ---
    with tab2:
        if extra_data.get("🚩 領土・資源"):
            st.success(extra_data["🚩 領土・資源"])
            st.divider()

        with st.expander("1. ルート作成と旗建設"):
            st.markdown("""
            - **最短ルート**: 資源地やステーション、砦に隣接させるように設計。
            - **効率化**: 山や川を避け、他同盟も旗を跨げるようにジグザグに引く等の配慮。
            """)

        with st.expander("2. パズル進行用「兵1旗」"):
            st.markdown("""
            - 旗の開始は必ず「兵士1名・英雄なし」。
            - 完了(
