import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager as fm
import matplotlib as mpl
import plotly.express as px
import scikit_posthocs as sp
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# --- ページ設定 ---
st.set_page_config(
    page_title="アンケートデータ統計分析アプリ",
    page_icon="📊",
    layout="wide",  # ワイドレイアウトで見やすく
)

# --- 関数定義 ---
def df_to_csv_download_button(df, filename):
    """CSVダウンロードボタンを生成する関数"""
    csv = df.to_csv(index=True).encode('utf-8-sig')
    st.download_button(
        label="📄 この表をCSVでダウンロード",
        data=csv,
        file_name=f'{filename}.csv',
        mime='text/csv',
    )

# --- フォント設定 (日本語対応) ---
# font_path = os.path.abspath("ipaexg.ttf") # ローカル環境でフォントファイルを置く場合
# if os.path.exists(font_path):
#     font_prop = fm.FontProperties(fname=font_path)
#     mpl.rcParams["font.family"] = font_prop.get_name()
#     plt.rc("font", family=font_prop.get_name())
# else:
#     # フォントファイルがない場合でもアプリは動作するが、Matplotlibの日本語が文字化けする
#     st.warning("⚠️ 日本語フォントファイルが見つかりません。Matplotlibを使ったグラフの日本語が文字化けする可能性があります。")


# --- サイドバー ---
with st.sidebar:
    st.header("1. データ準備")
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
    
    if uploaded_file:
        st.success(f"✅ ファイルがアップロードされました: `{uploaded_file.name}`")

    st.subheader("📥 サンプルCSVのダウンロード")
    sample_data = {
        "氏名": ["山田太郎", "佐藤花子", "鈴木一郎", "田中次郎", "高橋三郎", "伊藤さくら", "渡辺健太", "中村恵美", "小林直樹"],
        "所属": ["営業部", "開発部", "人事部", "開発部", "営業部", "人事部", "開発部", "営業部", "人事部"],
        "性別": ["男性", "女性", "男性", "男性", "男性", "女性", "男性", "女性", "男性"],
        "研修満足度": [3, 5, 4, 5, 2, 4, 4, 3, 5],
        "講師満足度": [4, 5, 5, 4, 3, 5, 4, 4, 5],
        "業務知識テスト（事前）": [60, 55, 58, 70, 65, 62, 80, 59, 68],
        "業務知識テスト（事後）": [75, 85, 72, 88, 78, 80, 92, 75, 85]
    }
    df_sample = pd.DataFrame(sample_data)
    csv = df_sample.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📄 サンプルCSVをダウンロード",
        data=csv,
        file_name="sample_survey_multi_group.csv",
        mime="text/csv"
    )

    st.header("2. このアプリについて")
    with st.expander("各分析手法の簡単な説明", expanded=False):
        st.markdown("""
        #### 🔍 記述統計
        データの平均、中央値、ばらつき（標準偏差）などを計算し、データ全体の基本的な特徴を把握します。
        
        #### 📊 段階評価分析
        「満足度」など、1〜5段階で評価された項目について、回答の割合を円グラフで可視化します。「所属」などのカテゴリ別に割合を見ることもできます。

        #### 🔄 クロス集計
        「所属」と「性別」など、2つのカテゴリの関係性を表にまとめ、グループごとの傾向を視覚化します。
        
        #### ⚖️ 群間比較
        「営業部」「開発部」「人事部」のように、複数のグループ間で特定の数値に統計的に意味のある差（有意差）があるかを検定します。
        - **2グループの場合**: t検定やU検定を用います。
        - **3グループ以上の場合**: **分散分析 (ANOVA)** やクラスカル・ウォリス検定を用います。
        
        *このアプリでは、グループ数を自動で判別して適切な手法を提案します。*
        
        #### ⏱ 前後比較
        研修の前後など、同じ対象の状況が変化したかを統計的に検定します。
        """)

    # --- 使い方ガイドボタンの追加 ---
    st.markdown("---")
    st.subheader("💡 使い方ガイド")
    if st.button("📚 アプリの使い方を見る", help="アプリの操作方法をステップバイステップで説明します。"):
        st.session_state["show_guide"] = True

# --- メイン画面 ---
st.title("📊 アンケートデータ統計分析アプリ")
st.write("アップロードしたCSVデータの簡単な統計分析と可視化を行います。")

# 使い方ガイドの表示
if st.session_state.get("show_guide", False):
    st.markdown("## 📚 使い方ガイド：アンケートデータ統計分析アプリ")
    st.markdown("このアプリは、アンケートデータをアップロードするだけで、様々な統計分析と可視化を簡単に行うことができます。")
    st.markdown("---")

    st.markdown("### ステップ 1: データの準備")
    st.markdown("1. まず、サイドバーの「**1. データ準備**」セクションを確認してください。")
    st.markdown("2. 「**CSVファイルをアップロードしてください**」ボタンをクリックし、分析したいアンケートデータをCSV形式でアップロードします。")
    st.markdown("   - **💡 ヒント**: CSVファイルは、1行目が項目名（ヘッダー）で、各列が数値データやカテゴリデータになっていることを確認してください。")
    st.markdown("3. もし手元にデータがない場合は、「**サンプルCSVをダウンロード**」ボタンからサンプルデータをダウンロードして試すことができます。")
    st.markdown("4. ファイルがアップロードされると、「**アップロードしたデータのプレビュー**」を展開して、データが正しく読み込まれているか確認できます。")
    st.image("https://example.com/upload_data.png", caption="データアップロードとプレビューのイメージ") # 画像生成のトリガー
    
    st.markdown("---")

    st.markdown("### ステップ 2: 分析タブの選択")
    st.markdown("データがアップロードされると、メイン画面の上部に5つの分析タブが表示されます。")
    st.markdown("- **① 記述統計**: データの基本的な特徴（平均、中央値、ばらつきなど）を把握します。")
    st.markdown("- **② 段階評価分析**: 1〜5段階評価などの項目について、回答の割合を円グラフで可視化します。")
    st.markdown("- **③ クロス集計**: 2つのカテゴリ変数の関係性を表とグラフで確認します。")
    st.markdown("- **④ 群間比較**: 複数のグループ間で数値データに統計的に意味のある差があるか検定します。")
    st.markdown("- **⑤ 前後比較**: 同じ対象の介入前後での数値データに変化があったか検定します。")
    st.image("https://example.com/analysis_tabs.png", caption="分析タブのイメージ") # 画像生成のトリガー

    st.markdown("---")

    st.markdown("### ステップ 3: 各分析の実行")
    st.markdown("各タブをクリックして、以下の手順で分析を進めます。")

    st.markdown("#### ① 記述統計")
    st.markdown("1. 「**分析したい数値列を選択してください**」で、平均値や標準偏差などを計算したい列を選びます。複数選択可能です。")
    st.markdown("2. 選択すると、要約統計量（平均、中央値、標準偏差、最小値、最大値など）の表が表示されます。")
    st.markdown("3. グラフとして、**平均値の比較**（棒グラフ）と**データの分布**（箱ひげ図）が表示され、視覚的にデータの傾向を把握できます。")
    st.image("https://example.com/descriptive_stats.png", caption="記述統計のイメージ") # 画像生成のトリガー

    st.markdown("#### ② 段階評価分析")
    st.markdown("1. 「**分析したい段階評価の列を選択してください**」で、「満足度」のような1〜5段階評価の数値列を選びます。")
    st.markdown("2. 必要に応じて、「**グループ分けに使う列を選択してください（任意）**」で、「所属」などのカテゴリ列を選ぶと、グループごとの評価割合を比較できます。")
    st.markdown("3. 円グラフと集計表で、各評価段階の割合を確認できます。")
    st.image("https://example.com/pie_chart_analysis.png", caption="段階評価分析のイメージ") # 画像生成のトリガー

    st.markdown("#### ③ クロス集計")
    st.markdown("1. 「**行に使うカテゴリ列**」と「**列に使うカテゴリ列**」で、関係性を知りたい2つのカテゴリ列を選びます。")
    st.markdown("2. 選ぶとすぐにクロス集計表が表示され、各カテゴリの組み合わせごとの件数を確認できます。")
    st.markdown("3. 「**グラフの種類を選択**」で「積み上げ棒グラフ」または「グループ化棒グラフ」を選び、視覚的に傾向を比較します。")
    st.image("https://example.com/crosstab.png", caption="クロス集計のイメージ") # 画像生成のトリガー

    st.markdown("#### ④ 群間比較：2群または多群の比較")
    st.markdown("1. 「**グループ分けに使う列**」で、比較したいグループ（例: 「所属」）の列を選びます。")
    st.markdown("2. 「**比較する数値データ列**」で、グループ間で比較したい数値データ（例: 「業務知識テスト（事後）」）を選びます。")
    st.markdown("3. 自動的に箱ひげ図が表示され、各グループのデータの分布を確認できます。")
    st.markdown("4. グループの数に応じて、適切な統計検定（2群ならt検定/U検定、3群以上なら分散分析/クラスカル・ウォリス検定）が提案されます。")
    st.markdown("5. 提案された検定方法を選択し、検定結果（検定統計量、p値）と統計的な結論（有意差があるか否か）を確認します。")
    st.markdown("   - **💡 ヒント**: p値が0.05未満であれば「有意な差がある」と判断されます。")
    st.image("https://example.com/group_comparison.png", caption="群間比較のイメージ") # 画像生成のトリガー

    st.markdown("#### ⑤ 前後比較：対応のある検定")
    st.markdown("1. 「**事前（Before）データ列**」と「**事後（After）データ列**」で、比較したい2つの数値データ列（例: 「業務知識テスト（事前）」と「業務知識テスト（事後）」）を選びます。")
    st.markdown("2. 「**使用する検定**」で「対応のあるt検定」または「ウィルコクソン符号順位検定」を選択します。")
    st.markdown("3. 検定結果（検定統計量、p値）と統計的な結論（有意な変化があったか否か）が表示されます。")
    st.markdown("4. 事前・事後の平均値を比較する棒グラフも表示されます。")
    st.image("https://example.com/pre_post_comparison.png", caption="前後比較のイメージ") # 画像生成のトリガー

    st.markdown("---")
    st.markdown("### ステップ 4: 結果のダウンロードと統計用語の確認")
    st.markdown("各分析結果の表には、「📄 この表をCSVでダウンロード」ボタンがついており、結果をCSVファイルとして保存できます。")
    st.markdown("メイン画面下部にある「**📖 統計用語の簡単な説明**」を展開すると、p値や平均値などの統計用語について学ぶことができます。")

    st.markdown("---")
    st.success("これでアプリの使い方は終わりです！ ぜひご自身のデータで様々な分析を試してみてください。")
    if st.button("ガイドを閉じる"):
        st.session_state["show_guide"] = False
    
    st.stop() # ガイド表示中はメインのアプリ本体は停止

if not uploaded_file:
    st.info("👆 サイドバーからCSVファイルをアップロードして分析を開始してください。")
    st.stop()

# --- ファイルがアップロードされた後の処理 ---
try:
    df = pd.read_csv(uploaded_file)
    with st.expander("アップロードしたデータのプレビュー", expanded=False):
        st.dataframe(df)
except Exception as e:
    st.error(f"❌ ファイルの読み込み中にエラーが発生しました: {e}")
    st.stop()


# 列タイプを自動で取得
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

# --- 分析タブ ---
tab1, tab5, tab2, tab3, tab4 = st.tabs(["① 記述統計", "② 段階評価分析", "③ クロス集計", "④ 群間比較", "⑤ 前後比較"])

# --- タブ1: 記述統計 ---
with tab1:
    st.header("① 記述統計")
    st.write("データの基本的な特徴（平均、中央値、ばらつき等）を把握します。")
    selected_cols_desc = st.multiselect("分析したい数値列を選択してください", numeric_cols, default=numeric_cols[:min(len(numeric_cols), 3)])

    if selected_cols_desc:
        desc = df[selected_cols_desc].describe().T
        desc["median"] = df[selected_cols_desc].median() # 中央値を追加
        st.write("📋 **要約統計量**")
        st.dataframe(desc.style.format("{:.2f}"), use_container_width=True) # 小数点以下2桁に整形
        df_to_csv_download_button(desc, "descriptive_stats")

        st.write("📊 **各項目の可視化**")
        
        df_mean = df[selected_cols_desc].mean().reset_index()
        df_mean.columns = ['項目', '平均値']
        df_melted = df[selected_cols_desc].melt(var_name='項目', value_name='値')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("平均値の比較")
            fig_bar = px.bar(
                df_mean, x='項目', y='平均値', title='各項目の平均値',
                color='項目', text_auto=True
            )
            fig_bar.update_traces(textposition='outside')
            fig_bar.update_layout(showlegend=False, yaxis_title="平均値")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            st.subheader("データの分布")
            fig_box = px.box(df_melted, x='項目', y='値', title='箱ひげ図', color='項目')
            fig_box.update_layout(showlegend=False, yaxis_title="値")
            st.plotly_chart(fig_box, use_container_width=True)

# --- ★★★★★ ここからが追加した機能 ★★★★★ ---
# --- タブ5: 段階評価分析 ---
with tab5:
    st.header("② 段階評価分析")
    st.write("1〜5段階評価などのアンケート項目について、回答の割合を円グラフで可視化します。")
    st.info("💡 「研修満足度」などの整数で評価された数値列を選択してください。")

    col1_pie, col2_pie = st.columns(2)
    with col1_pie:
        # 分析対象の列を選択
        pie_target_col = st.selectbox(
            "分析したい段階評価の列を選択してください",
            numeric_cols,
            index=None,
            placeholder="分析する列を選択...",
            key="pie_target"
        )
    with col2_pie:
        # グループ分けの列を選択
        pie_group_col_options = ["(全体で集計)"] + cat_cols
        pie_group_col = st.selectbox(
            "グループ分けに使う列を選択してください（任意）",
            pie_group_col_options,
            key="pie_group"
        )

    if pie_target_col:
        st.markdown("---")

        # --- 全体での集計 ---
        if pie_group_col == "(全体で集計)":
            st.subheader(f"📊 「{pie_target_col}」の全体集計")
            
            # 欠損値を除外して集計
            df_target = df.dropna(subset=[pie_target_col])
            
            # データ集計
            df_counts = df_target[pie_target_col].value_counts().sort_index()
            df_pie = df_counts.reset_index()
            df_pie.columns = [pie_target_col, '人数']

            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("**集計表**")
                st.dataframe(df_pie, use_container_width=True)
                df_to_csv_download_button(df_pie, f"pie_chart_data_{pie_target_col}")

            with col2:
                st.write("**円グラフ**")
                fig_pie = px.pie(
                    df_pie,
                    names=pie_target_col,
                    values='人数',
                    title=f"「{pie_target_col}」の回答割合",
                    hole=0.3 # ドーナツグラフにする
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', sort=False)
                st.plotly_chart(fig_pie, use_container_width=True)

        # --- グループ別の集計 ---
        else:
            st.subheader(f"📊 「{pie_group_col}」別 - 「{pie_target_col}」の集計")
            groups = sorted(df[pie_group_col].dropna().unique())

            for group in groups:
                st.markdown(f"---")
                st.markdown(f"#### **グループ: {group}**")
                
                # グループとターゲット列で欠損値を除外
                df_filtered_pie = df.dropna(subset=[pie_group_col, pie_target_col])
                df_filtered_pie = df_filtered_pie[df_filtered_pie[pie_group_col] == group]

                if df_filtered_pie.empty:
                    st.write("このグループには表示できるデータがありません。")
                    continue

                # データ集計
                df_counts = df_filtered_pie[pie_target_col].value_counts().sort_index()
                df_pie = df_counts.reset_index()
                df_pie.columns = [pie_target_col, '人数']

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write("**集計表**")
                    st.dataframe(df_pie, use_container_width=True)
                    df_to_csv_download_button(df_pie, f"pie_chart_data_{pie_group_col}_{group}_{pie_target_col}")

                with col2:
                    st.write("**円グラフ**")
                    if df_pie.empty:
                         st.write("表示するデータがありません。")
                         continue
                    fig_pie_group = px.pie(
                        df_pie,
                        names=pie_target_col,
                        values='人数',
                        title=f"「{pie_target_col}」の回答割合 ({group})",
                        hole=0.3
                    )
                    fig_pie_group.update_traces(textposition='inside', textinfo='percent+label', sort=False)
                    st.plotly_chart(fig_pie_group, use_container_width=True)
    else:
        st.info("👆 分析したい列と、必要に応じてグループ分けの列を選択してください。")

# --- ★★★★★ 追加機能はここまで ★★★★★ ---

# --- タブ2: クロス集計 ---
with tab2:
    st.header("③ クロス集計")
    st.write("2つのカテゴリ変数の関係性を表とグラフで確認します。")
    if len(cat_cols) < 2:
        st.warning("クロス集計を行うには、カテゴリ列が2つ以上必要です。")
    else:
        col1_cross, col2_cross = st.columns(2)
        with col1_cross:
            row_col = st.selectbox("行に使うカテゴリ列", cat_cols, index=0, key="cross1")
        with col2_cross:
            col_col = st.selectbox("列に使うカテゴリ列", cat_cols, index=1, key="cross2")

        if row_col and col_col:
            if row_col == col_col:
                st.warning("行と列には異なる列を選択してください。")
            else:
                cross_tab = pd.crosstab(df[row_col], df[col_col])
                st.write(f"**「{row_col}」と「{col_col}」のクロス集計表**")
                st.dataframe(cross_tab, use_container_width=True)
                df_to_csv_download_button(cross_tab, f"crosstab_{row_col}_vs_{col_col}")

                st.write("📊 **クロス集計の可視化**")
                graph_type = st.radio("グラフの種類を選択", ["積み上げ棒グラフ", "グループ化棒グラフ"], horizontal=True, key="cross_graph_type")
                barmode_option = 'stack' if graph_type == "積み上げ棒グラフ" else 'group'
                
                fig = px.bar(cross_tab, barmode=barmode_option, title=f"{graph_type}: {row_col} vs {col_col}")
                fig.update_layout(xaxis_title=row_col, yaxis_title="件数")
                st.plotly_chart(fig, use_container_width=True)

# --- タブ3: 群間比較 ---
with tab3:
    st.header("④ 群間比較：2群または多群の比較")
    st.write("選択したグループ間で、数値データに統計的に意味のある差（有意差）があるか検定します。")
    st.write("_グループ数が2つの場合はt検定/U検定を、3つ以上の場合は分散分析/クラスカル・ウォリス検定を自動的に実行します。_")

    col1_group, col2_group = st.columns(2)
    with col1_group:
        group_col = st.selectbox("グループ分けに使う列", cat_cols, key="test1_multi")
    with col2_group:
        value_col = st.selectbox("比較する数値データ列", numeric_cols, key="test2_multi")

    if not group_col or not value_col:
        st.stop()

    df_filtered = df[[group_col, value_col]].dropna()
    groups = sorted(df_filtered[group_col].unique()) # グループ名をソートして順序を固定
    group_count = len(groups)

    st.subheader("📊 箱ひげ図による可視化")
    fig = px.box(df_filtered, x=group_col, y=value_col, color=group_col,
                 title=f"{group_col}別 {value_col}の分布", points="all",
                 category_orders={group_col: groups}) # グラフの順序も固定
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    if group_count < 2:
        st.warning("比較するには、グループが2つ以上必要です。")

    elif group_count == 2:
        st.subheader("検定方法の選択（2群）")
        g1 = df_filtered[df_filtered[group_col] == groups[0]][value_col]
        g2 = df_filtered[df_filtered[group_col] == groups[1]][value_col]
        
        test_type = st.radio("検定方法の選択", ["t検定（平均値の差）", "U検定（分布の差）"], horizontal=True, key="2group_test")
        
        if "t検定" in test_type:
            st.info("_💡 **t検定**: 2つのグループの**平均値**に差があるか検定します。データが正規分布に近い場合に適しています。_")
            stat, p = stats.ttest_ind(g1, g2, equal_var=False)
        else:
            st.info("_💡 **U検定**: 2つのグループの**分布**に差があるか検定します。データが正規分布に従わない場合や、順序尺度の場合に用います。_")
            stat, p = stats.mannwhitneyu(g1, g2, alternative="two-sided")

        st.subheader("検定結果")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric(label="検定統計量", value=f"{stat:.3f}")
        res_col2.metric(label="p値", value=f"{p:.4f}")

        if p < 0.05:
            st.success(f"✅ **結論**: {groups[0]}と{groups[1]}の間には、統計的に**有意な差がある**と言えます。 (p < 0.05)")
        else:
            st.info(f"ℹ️ **結論**: {groups[0]}と{groups[1]}の間に、統計的に**有意な差があるとは言えません**。 (p ≥ 0.05)")

    else: # 3群以上の比較
        st.subheader(f"検定方法の選択（{group_count}群）")
        samples = [df_filtered[df_filtered[group_col] == g][value_col] for g in groups]
        
        test_type_multi = st.radio("検定方法の選択", ["分散分析ANOVA（平均値の差）", "クラスカル・ウォリス検定（分布の差）"], horizontal=True, key="multi_group_test")
        
        def display_posthoc_results(p_values_df):
            st.write("**p値の比較表（p < 0.05 の組み合わせをハイライト）**")
            st.dataframe(p_values_df.style.applymap(lambda x: 'background-color: #aaffaa' if x < 0.05 else ''))
            
            significant_pairs = []
            for i, col in enumerate(p_values_df.columns):
                for j, row_label in enumerate(p_values_df.index):
                    if i < j:
                        p_val = p_values_df.iloc[j, i]
                        if p_val < 0.05:
                            significant_pairs.append(f"**{col}** と **{row_label}**")
            
            st.markdown("---")
            st.write("#### **結論の要約**")
            if significant_pairs:
                st.success("以下のグループの組み合わせで、統計的に有意な差が見られました。")
                for pair in significant_pairs:
                    st.markdown(f"- {pair}")
            else:
                st.info("いずれのグループの組み合わせにおいても、統計的に有意な差は見られませんでした。")

        if "ANOVA" in test_type_multi:
            st.info("_💡 **分散分析 (ANOVA)**: t検定を3群以上に拡張した手法です。各グループのデータが正規分布に近く、分散が等しい場合に、**平均値**の差を検定するのに適しています。_")
            stat, p = stats.f_oneway(*samples)

            st.subheader("検定結果（分散分析）")
            res_col1, res_col2 = st.columns(2)
            res_col1.metric(label="F値", value=f"{stat:.3f}")
            res_col2.metric(label="p値", value=f"{p:.4f}")
            
            if p < 0.05:
                st.success("✅ **全体の結果**: いずれかのグループ間に、統計的に**有意な差がある**と言えます。 (p < 0.05)")
                st.markdown("---")
                st.subheader("多重比較（Tukey-HSD法）")
                st.info("_どのグループ間に具体的な差があるかを確認します。_")
                posthoc_p_values = sp.posthoc_tukey(df_filtered, val_col=value_col, group_col=group_col)
                display_posthoc_results(posthoc_p_values)
            else:
                st.info("ℹ️ **全体の結果**: グループ間に、統計的に**有意な差があるとは言えません**。 (p ≥ 0.05)")

        else:
            st.info("_💡 **クラスカル・ウォリス検定**: U検定を3群以上に拡張したノンパラメトリックな手法です。データが正規分布に従わない場合や、順序尺度の場合に、グループの**分布（中央値）**に差があるかを検定します。_")
            stat, p = stats.kruskal(*samples)
            
            st.subheader("検定結果（クラスカル・ウォリス検定）")
            res_col1, res_col2 = st.columns(2)
            res_col1.metric(label="H値", value=f"{stat:.3f}")
            res_col2.metric(label="p値", value=f"{p:.4f}")

            if p < 0.05:
                st.success("✅ **全体の結果**: いずれかのグループ間に、統計的に**有意な差がある**と言えます。 (p < 0.05)")
                st.markdown("---")
                st.subheader("多重比較（Dunn法）")
                st.info("_どのグループ間に具体的な差があるかを確認します。_")
                posthoc_p_values = sp.posthoc_dunn(df_filtered, val_col=value_col, group_col=group_col, p_adjust='holm')
                display_posthoc_results(posthoc_p_values)
            else:
                st.info("ℹ️ **全体の結果**: グループ間に、統計的に**有意な差があるとは言えません**。 (p ≥ 0.05)")

# --- タブ4: 前後比較 ---
with tab4:
    st.header("⑤ 前後比較：対応のある検定")
    st.write("同じ対象に対する介入の前後などで、数値に統計的に意味のある変化があったか検定します。")
    col1_pre, col2_post = st.columns(2)
    with col1_pre:
        col_pre = st.selectbox("事前（Before）データ列", numeric_cols, key="before")
    with col2_post:
        col_post = st.selectbox("事後（After）データ列", numeric_cols, key="after")

    if col_pre and col_post:
        if col_pre == col_post:
            st.warning("事前と事後には異なる列を選択してください。")
        else:
            temp_df = df[[col_pre, col_post]].dropna() 
            before = temp_df[col_pre]
            after = temp_df[col_post]
            
            if len(before) == 0:
                st.warning("比較できる有効なデータがありません。行に欠損値がないか確認してください。")
            else:
                st.write(f"**比較対象**: `{col_pre}` vs `{col_post}` (n={len(before)})")
                test_type_rel = st.radio("使用する検定", ["対応のあるt検定", "ウィルコクソン符号順位検定"], horizontal=True)

                st.markdown("---")
                if test_type_rel == "対応のあるt検定":
                    st.info("_💡 **対応のあるt検定**: 前後差のデータが正規分布に近い場合に適しています。_")
                    stat, p = stats.ttest_rel(before, after)
                else:
                    st.info("_💡 **ウィルコクソン符号順位検定**: 前後差のデータが正規分布に従わない場合に用います。_")
                    stat, p = stats.wilcoxon(before, after)

                st.subheader("検定結果")
                res_col1, res_col2 = st.columns(2)
                res_col1.metric(label="検定統計量", value=f"{stat:.3f}")
                res_col2.metric(label="p値", value=f"{p:.4f}")

                if p < 0.05:
                    st.success(f"✅ **結論**: 事前（{col_pre}）と事後（{col_post}）で統計的に**有意な変化が見られます**。 (p < 0.05)")
                else:
                    st.info(f"ℹ️ **結論**: 事前（{col_pre}）と事後（{col_post}）で統計的に**有意な変化は見られませんでした**。 (p ≥ 0.05)")

                st.subheader("📊 平均値の比較グラフ")
                df_plot = pd.DataFrame({'平均値': [before.mean(), after.mean()]}, index=[f'事前({col_pre})', f'事後({col_post})'])
                fig = px.bar(df_plot, y='平均値', color=df_plot.index, title='事前・事後の平均値比較', text_auto=True)
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("📖 統計用語の簡単な説明")
with st.expander("クリックして各用語の説明を確認"):
    st.markdown("""
    - **平均値 (mean)**: 全ての数値を足し合わせ、その個数で割った値。データ全体の中心を示す代表的な指標です。
    - **中央値 (median / 50%)**: データを小さい順に並べたときに、ちょうど真ん中にくる値。外れ値（極端に大きい・小さい値）の影響を受けにくい特徴があります。
    - **標準偏差 (std)**: データが平均値からどれくらい散らばっているか（ばらつきの度合い）を示す指標です。値が大きいほど、ばらつきが大きいことを意味します。
    - **最小値 (min)** / **最大値 (max)**: データの中で最も小さい値と最も大きい値です。
    - **四分位数 (25% / 75%)**: データを小さい順に並べ、4等分したときの区切りの値です。25%点を第1四分位数、75%点を第3四分位数と呼び、データのばらつき具合を箱ひげ図などで表現するのに使われます。
    - **p値 (p-value)**: 「観測された結果が、偶然そのようになった確率」を示す値です。統計的な判断基準として使われ、一般的にこの値が0.05（5%）より小さい場合に、「偶然とは考えにくく、統計的に意味のある差（=有意差）がある」と判断します。
    - **検定統計量 (Test Statistic)**: t検定やU検定などの各検定手法に基づいて計算される数値で、p値を算出するために使われます。
    """)