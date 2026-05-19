import streamlit as st
import json
import os

# --- 設定・ファイルパス ---
CONFIG_FILE = 'svs_manual_data.json'

# --- 初期データの定義（SVSマニュアルの素案をセット） ---
def get_default_manual_data():
    return {
        "🚨 マッチング前": [
            {
                "title": "チーム発足",
                "blocks": [
                    {"type": "text", "content": "* 執政官が、自同盟のメンバーと相談の上、指揮官を任命。\n\n* 関連するメンバーでチャットグループを作成、戦略チーム（SVS戦略チーム等）として発足する。\n\n* 以降は必要に応じてメンバーを追加する。"}
                ]
            },
            {
                "title": "温存の呼びかけ",
                "blocks": [
                    {"type": "text", "content": "* 戦略チーム内で「温存リスト（火晶、加速、エナジー石など）」や「準備フェーズで勝利する重要性」のアナウンス文を確認。\n\n* 情報漏洩防止のため、また世界チャットでは読まない人も現れるため、世界チャットではなく「盟主会」を通じて各同盟の盟主から同盟員へアナウンスを流してもらう。\n\n* 炉レベル30以上のプレイヤーへ、SVS準備フェーズ中の「副執政官」「教育部長」への積極的なエントリーを呼びかける。"},
                    {"type": "code", "content": "明日からの準備フェーズの\n王国ポイントに注意🚫\n\n熔鉱炉Lv21以下の方\nポイント50%しか反映されません。\n熔鉱炉Lv15以下の方は\n0の可能性もありますので気をつけてアイテムの使用を💡\n\n詳細はイベントページ\n最強王国のルールを\n確認してみてくださいm(_ _)m✨"},
                    {"type": "code", "content": "🐕svs準備フェーズ🐈\n　　　　月　火　水　木　金\n火晶🔥　◎｜〇｜－｜－｜〇｜ \n宝石　　◎｜－｜〇｜〇｜－｜ \n欠片🧩　－｜△｜〇｜－｜－｜ \nﾗｷﾙﾚ　　－｜◎｜〇｜－｜－｜ \n加速⏩　◎｜〇｜－｜－｜〇｜ \n専門📗　－｜◎｜〇｜－｜－｜ \nﾍﾟｯﾄ　　－｜－｜〇｜－｜◎｜ \n訓練　　－｜－｜－｜◎｜－｜ 領装　　－｜－｜－｜－｜◎｜ ｴﾅ石🪨　－｜－｜－｜〇｜◎｜ 専装　　－｜－｜－｜〇｜◎｜ ﾐｽﾘﾙ　　－｜－｜－｜〇｜◎｜ 獣狩　　－｜－｜◎｜－｜－｜  採集　　－｜◎｜－｜－｜－｜ ▷加速⏩…専門家含む ▷専門📗…印・本の使用 ⚠共通欠片・共通印は含まない"},
                    {"type": "code", "content": "【SVS準備フェーズ中の、\n                               役職申請について】\n\n●内政部長・・・盟主会全体チャットメンバー、KFC幹部（現状通り）\n\n●副執政官・・・炉30以上の方積極的にエントリー！\n\n●教育部長・・・炉30以上の方積極的にエントリー\n\nなお、SVSに参加しないサブ垢でも炉30なら対象とさせて頂きます。"},
                    {"type": "code", "content": "上記内容の補足として\n\n●副執政官　戦闘時に火力となる方の戦力を伸ばすため。\nまた、準備フェーズでポイントを稼げる方を対象とするため炉30も含んでます。\n\n●教育部長　兵士訓練のミッションがある日の前日24:00〜ミッション終了8:59まで。\n\n\n炉29以下の方は、申請してはいけないというわけではないですが\n出来れば30以上の方に『『積極的に』』エントリーして欲しいというご案内です😊"},
                    {"type": "code", "content": "準備フェーズに向けた温存のお願い\n\n温存資源リストです\n\n・火晶\n・領主装備宝石\n・英雄の欠片  専用武器\n・精錬エナジー石\n・建築、研究、訓練の加速\n・ミスリル\n・ペット突破＆洗練など・専門家の学識書、印、学習加速など　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　その他採集や討伐などがポイントになります"},
                    {"type": "code", "content": "【SVS対戦国決まるまで、リソース温存のお願い】\n●炉30の方は火晶にしない\n　火晶の方は4段目までは〇\n●英雄進化しない\n●武器レベルアップしない\n●精錬エナジー使用しない\n●加速アイテム使用しない\n●ペット育てない\n●領主装備レベルアップしない"},
                    {"type": "code", "content": "準備フェーズで負けられない理由\n\n準備フェーズ勝利\n→相手国で王城戦\n　→勝利→双方の役職を確保（前回）\n　→敗戦→自国の役職は確保\n準備フェーズで敗戦\n→自国で王城戦\n　→勝利→自国の役職は確保\n　→敗戦→役職を失う"}
                ]
            },
            {
                "title": "セキュリティ強化",
                "blocks": [
                    {"type": "text", "content": "各同盟の加入申請設定を「**鍵付き（承認制）**」に変更するよう通達。\n\n加入申請があった場合、必ず「誰のサブ垢か」を確認し、スパイの侵入を防ぐ。"}
                ]
            }
        ],
        "⚔️ フェーズ2：戦略と各同盟の役割決定": [
            {
                "title": "役割の決定（上位5同盟）",
                "blocks": [
                    {"type": "text", "content": "指揮官や補佐（連絡役）など、戦略チームの役職（4強）を決定。\n※4強については、準備フェーズで変更となる可能性もあるので要確認。"},
                    {"type": "code", "content": "【目標リスト】\n王城集結主：ぺーさん、わからん、harupon、kgm\nゴースト：わからん（移動）、セコム\n\n【上位5同盟の役割例】\n・主砲（KFC）\n・ゴースト・砲台（MMC）\n・ポイ活・砲台（rlx, MGA, wan）"}
                ]
            },
            {
                "title": "移転場所の確定",
                "blocks": [
                    {"type": "text", "content": "担当する砲台と、具体的な移転先（レッドゾーンのどの位置か）を各同盟に割り当てて確定させます。"},
                    {"type": "code", "content": "・北wan（北砲台側レッドゾーン）\n・王城KFC（北砲台右）\n・東rlx（東砲台上）\n・南MGA（東砲台下）\n・西MMC（南砲台右）"}
                ]
            },
            {
                "title": "戦術パターンの検討",
                "blocks": [
                    {"type": "text", "content": "相手の出方（連撃の強さやアクティブ人数など）を想定し、「最初からゴーストを立てるか」「差し込み（防衛の増援）で耐えて様子を見るか」などの戦術パターンを協議。\n\n暇な人が現れないよう、王城と砲台集結のバランスを事前に想定しておくこと。〇〇な状態であれば砲台集結をしてもらう、基本的にはソロで砲台攻撃してもらい、号令で集結に乗ってもらうようにする、など。\n\n連撃部隊、ゴースト部隊を作ると決定した場合は、その部隊を埋めるだけの移籍者を集めてくる必要があります。"}
                ]
            },
            {
                "title": "考え方の例（戦力差が大きく見える場合）",
                "blocks": [
                    {"type": "text", "content": "相手が準備フェーズで相当あげてくる、とかでなければ最初はゴースト出さずに様子見でもいいかなと思います。\n\n連撃が多くて取られる、という場合には\n1. **差し込みで耐える**\n2. **ゴーストをかける**\nのどちらかになるかと思います。"},
                    {"type": "text", "content": "差し込みの場合は駐屯同盟の方に差し込みのご協力のお願いをすることになります 💦"},
                    {"type": "text", "content": "実際やってみないと分かりませんが、もし相手がバフを隠していて、想定していたよりも集結主が強い…という場合にはゴーストが必須になるかと。"}
                ]
            }
        ],
        "🔄 フェーズ3：移籍メンバーの選定と受け入れ調整": [
            {
                "title": "相手執政官との交渉（執政官業務）",
                "blocks": [
                    {"type": "text", "content": "各同盟の加入申請設定を「**鍵付き（承認制）**」に変更するよう通達。\n\n加入申請があった場合、必ず「誰のサブ垢か」を確認し、スパイの侵入を防ぐ。"}
                ]
            },
            {
                "title": "戦力リストの作成と枠の確認",
                "blocks": [
                    {"type": "text", "content": "* 大溶鉱炉ランキング上位100位、同盟上位10位などから、移籍候補者をリストアップ。\n* 候補者の「火晶レベル（上位28名など）」「ジェシー・パトリックの有無」「スキルや兵舎レベル」をまとめたデータを作成。\n* 上位5同盟へ移籍受け入れの承諾を取り、各同盟の「受入可能人数（空き枠数）」を確認（例: KFCは31人、MMCは30人など）。"}
                ]
            },
            {
                "title": "メンバーの割り振り決定",
                "blocks": [
                    {"type": "text", "content": "作成したリストと空き枠を照らし合わせ、具体的に誰をどの同盟に移動させるか（エクセル等のリスト）を決定。\n\n**KFC（主砲）**へ火晶3のメンバーを優先して集めつつ、**MMC（ゴースト）**用にも火晶3メンバーを一定数（10〜15名程度）残すなど、戦力バランスを調整。なお、KFCに入りきらなかった残りの火晶2や火晶1のメンバーはMMCへ配置。"}
                ]
            },
            {
                "title": "スケジューリング・連絡手段の決定",
                "blocks": [
                    {"type": "text", "content": "「いつまでに」「誰が」「何を」案内するかという全体スケジュールを確定させます。\n移動するプレイヤーへの案内が遅れないよう、逆算して「**当日18時頃までには移動先と戦術を各個別に連絡する**」というスケジュール目標をここで合意しておきます。"},
                    {"type": "text", "content": "指示混線を防ぎ、迅速かつ正確な命令系統を維持するため、当日のボイスチャット（VC）の発言メンバーを決めておく。その他の戦略チーム・メンバーは「**聞き専（マイクミュート）**」を推奨し、発言者を極限まで絞ります。"}
                ]
            }
        ],
        "🏁 フェーズ4：当日に向けた最終調整・連絡": [
            {
                "title": "ゲーム内システム・インフラ確認",
                "blocks": [
                    {"type": "text", "content": "### 📋 ホワイトリストの登録\n決定した移籍メンバーのリストに基づき、各受け入れ先同盟（KFCやMMCなど）で対象者を盟主が「ホワイトリスト」に事前登録する。可能であれば移動が予想される人は登録しておく。\n\n### 🎖️ R4の登録\n当日、王城で集結主が予想される人は盟主が「R4」にしておく。メンバーのリフレッシュ等の作業があるため。\n\n### 📡 インフラ確認と最終連絡\n設定した「計3名のコマンダー体制」を軸に、Discordなどボイスチャットの通信環境と参加人数を最終確認。\n当日の18時頃までに、各プレイヤーに対して「どこの同盟へ移動するか」と「基本的な戦術（ポイ活徹するか、主砲に乗るか等）」を連絡する。\n\n準備フェーズでの相手のポイントの伸び方やバフの状況などを分析し、最終的な作戦（ゴースト発動の有無など）を決定・共有する。\n\nポイ活移籍は〇〇同盟に移籍してください、とアナウンスする。"}
                ]
            },
            {
                "title": "Discord アナウンスタイムライン",
                "blocks": [
                    {"type": "text", "content": "* 王城戦戦略チームの事前集合時間をアナウンスしておく（30分前集合等）。\n* 聞き専の人向けにも、盟主会を通じて、接続先をアナウンスする。\n* 15分前を目安に、聴講者向けにアナウンスをする。"},
                    {"type": "code", "content": "【アナウンス内容参考】\n・各同盟の役割の確認。\n・戦略の確認。（差し込み、連撃、ゴースト等）\n・情報連携方法の確認。\n・発言メンバーの特定、その他の戦略チーム・メンバーは「聞き専（マイクミュート）」を推奨。"}
                ]
            }
        ],
        "⚔️ フェーズ5：終了後": [
            {
                "title": "事後処理・叙勲者の決定",
                "blocks": [
                    {"type": "text", "content": "### 👑 執政官の確定\n通常は執政官が引継ぎとなる。\n\n### 🏅 叙勲の割り振り\n* **将軍**：2名\n* **士官**：10名\n* **兵士**：50名\n\n割り振りをどうするか、貢献ランキングを参考にするか、残りは同盟のランキングで割り振る等、自同盟メンバー等で相談して決定する。"}
                ]
            }
        ]
    }

# --- データ読み書き関数 ---
def load_manual_data():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return get_default_manual_data()

def save_manual_data(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- アプリ基本設定 ---
st.set_page_config(page_title="SVS作戦本部マニュアル", page_icon="👑", layout="wide")
data = load_manual_data()

# --- サイドバーメニュー ---
st.sidebar.title("👑 SVS作戦本部")
app_mode = st.sidebar.radio(
    "メニュー切り替え",
    ["運営マニュアル 📜", "マニュアルを編集する ⚙️"],
    index=0
)

# --- 1. マニュアル閲覧画面 ---
if app_mode == "運営マニュアル 📜":
    st.title("📜 SVS 運営マニュアル")
    st.caption("各フェーズのタブを切り替えて手順を確認してください。")
    
    categories = list(data.keys())
    if categories:
        tabs = st.tabs(categories)
        for i, category in enumerate(categories):
            with tabs[i]:
                if not data[category]:
                    st.info("このフェーズにはまだ項目が登録されていません。")
                for exp in data[category]:
                    with st.expander(exp['title'], expanded=False):
                        for block in exp['blocks']:
                            # 文字列内のエスケープされた改行文字を実際の改行に変換
                            content_processed = block['content'].replace("\\n", "\n")
                            
                            if block['type'] == 'text':
                                # st.markdown を使用してマークダウンと改行を完全に有効化
                                st.markdown(content_processed)
                            elif block['type'] == 'code':
                                st.code(content_processed, language=None)
    else:
        st.warning("マニュアルデータが空です。編集モードから追加してください。")

# --- 2. マニュアル編集画面 ---
elif app_mode == "マニュアルを編集する ⚙️":
    st.title("⚙️ SVS マニュアル編集モード")
    st.warning("ここで修正して「すべての変更を確定保存」を押すと、閲覧画面に即時反映されます。")
    st.info("💡 編集時のコツ：箇条書きは `* 項目名`、太字は `**文字**`、見出しは `### 見出し` と入力するとマークダウンになります。改行はエンターを2回押して空行を作ると綺麗に反映されます。")
    
    category = st.selectbox("編集するカテゴリ（フェーズ）を選択", list(data.keys()))
    expanders = data[category]
    
    for e_idx, exp in enumerate(expanders):
        with st.container(border=True):
            col_del_exp, col_title_exp = st.columns([0.5, 9.5])
            with col_del_exp:
                if st.button("❌", key=f"del_exp_{category}_{e_idx}", help="この大項目ごと削除"):
                    expanders.pop(e_idx)
                    save_manual_data(data)
                    st.rerun()
            with col_title_exp:
                exp['title'] = st.text_input(f"大見出し {e_idx+1}", exp['title'], key=f"edit_t_{category}_{e_idx}")
            
            for b_idx, block in enumerate(exp['blocks']):
                c1, c2, c3 = st.columns([1.5, 8, 0.5])
                with c1:
                    block['type'] = st.selectbox(
                        "表示種別", 
                        ["text", "code"], 
                        index=0 if block['type'] == 'text' else 1, 
                        key=f"ty_{category}_{e_idx}_{b_idx}"
                    )
                with c2:
                    block['content'] = st.text_area(
                        "内容", 
                        block['content'], 
                        key=f"cn_{category}_{e_idx}_{b_idx}",
                        rows=5
                    )
                with c3:
                    if st.button("🗑️", key=f"del_b_{category}_{e_idx}_{b_idx}", help="この文章ブロックを削除"):
                        exp['blocks'].pop(b_idx)
                        save_manual_data(data)
                        st.rerun()
            
            if st.button("➕ 文章ブロックを追加", key=f"add_p_{category}_{e_idx}"):
                exp['blocks'].append({"type": "text", "content": ""})
                save_manual_data(data)
                st.rerun()
                
    st.divider()
    
    if st.button("✨ このフェーズに新しい大項目を追加"):
        expanders.append({"title": "新規項目", "blocks": [{"type": "text", "content": ""}]})
        save_manual_data(data)
        st.rerun()
        
    st.divider()
    
    if st.button("💾 すべての変更を確定保存", type="primary"):
        save_manual_data(data)
        st.success("マニュアルを更新しました！「運営マニュアル 📜」タブから確認できます。✨")
