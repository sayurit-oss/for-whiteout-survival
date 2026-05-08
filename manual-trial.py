import streamlit as st
import json
import os

# --- データの読み込み関数 ---
def load_manual():
    if os.path.exists('manual_data.json'):
        with open('manual_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    # データがない場合の初期値
    return {
        "👥 メンバー管理": "初期テキストを入れてね♪",
        "🚩 領土・資源": "初期テキストを入れてね♪",
        "⚔️ イベント攻略": "初期テキストを入れてね♪"
    }

# --- 1. マニュアル閲覧画面（タブ表示） ---
def manual_view_page():
    st.title("📜 MMC同盟 運営バイブル")
    st.info("「親しみやすさ × メリハリ」楽しく、正しく、勝つ！")
    
    manual_data = load_manual()

    # ここにご希望のタブ設定を書き加えます
    tab1, tab2, tab3 = st.tabs(["👥 メンバー管理", "🚩 領土・資源", "⚔️ イベント攻略"])

    with tab1:
        # 管理画面で保存した内容を、セクションごとに展開します
        st.markdown(manual_data.get("👥 メンバー管理", ""))
        # 特定の重要ルールなどは個別にExpanderで固定表示にしてもOKです
        with st.expander("💡 ランクアップ等の固定ルール（早見表）"):
            st.markdown("- **炉レベル**: 25以上\n- **総力**: 3000万以上\n- **IDチェック**: 74始まりに注意！")

    with tab2:
        st.markdown(manual_data.get("🚩 領土・資源", ""))
        with st.expander("🚩 パズル用「兵1旗」の運用（案内文）"):
            st.code("パズル用の旗なので、兵士1・英雄なしでお願いします！一旦送還しますね。")

    with tab3:
        st.markdown(manual_data.get("⚔️ イベント攻略", ""))
        with st.expander("🛡️ キルイベ / 王国ルール（コピペ用）"):
            st.code("都市攻撃は「同盟未加入」を3回確認してから！")

# --- 2. 管理者設定画面（編集機能） ---
def admin_manual_edit():
    st.header("🛠️ マニュアルの加筆修正")
    manual_data = load_manual()

    # 修正したいタブ（セクション）を選択
    section = st.selectbox("編集するセクション", list(manual_data.keys()))

    # テキストエリアで中身を編集
    new_content = st.text_area(f"「{section}」の本文を編集（Markdown形式）", 
                               value=manual_data[section], 
                               height=400)

    if st.button("マニュアルを保存する✨"):
        manual_data[section] = new_content
        # 保存処理（バックアップ関数などは前回提示のものと組み合わせてください）
        with open('manual_data.json', 'w', encoding='utf-8') as f:
            json.dump(manual_data, f, ensure_ascii=False, indent=4)
        st.success(f"{section} の内容を更新したよ！😊")
        st.rerun()
