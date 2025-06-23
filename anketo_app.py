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
font_path = os.path.abspath("ipaexg.ttf")
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    mpl.rcParams["font.family"] = font_prop.get_name()
    plt.rc("font", family=font_prop.get_name())
else:
    # フォントファイルがない場合でもアプリは動作するが、Matplotlibの日本語が文字化けする
    st.warning("⚠️ 日本語フォントファイル 'ipaexg.ttf' が見つかりません。Matplotlibを使ったグラフの日本語が文字化けする可能性があります。")


# --- サイドバー ---
with st.sidebar:
    st.header("1. データ準備")
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
    
    if uploaded_file:
        st.success(f"✅ ファイルがアップロードされました: `{uploaded_file.name}`")

    st.subheader("📥 サンプルCSVのダウンロード")
    sample_data = {
        "氏名": ["山田太郎", "佐藤花子", "鈴木一郎", "田中次郎", "高橋三郎", "伊藤さくら"],
        "立場": ["担任", "支援員", "担任", "支援員", "担任", "支援員"],
        "性別": ["男性", "女性", "男性", "男性", "男性", "女性"],
        "支援の目標が共有されている": [1, 4, 2, 5, 2, 3],
        "役割分担は明確である": [4, 3, 4, 4, 5, 2],
        "支援の方針について話し合っている": [5, 4, 4, 5, 5, 3],
        "事前評価": [60, 55, 58, 70, 65, 62],
        "事後評価": [75, 90, 72, 85, 80, 90]
    }
    df_sample = pd.DataFrame(sample_data)
    csv = df_sample.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📄 サンプルCSVをダウンロード",
        data=csv,
        file_name="sample_survey.csv",
        mime="text/csv"
    )

    st.header("2. このアプリについて")
    with st.expander("各分析手法の簡単な説明", expanded=False):
        st.markdown("""
        #### 🔍 記述統計
        データの平均、中央値、ばらつき（標準偏差）などを計算し、データ全体の基本的な特徴を把握します。
        
        #### 🔄 クロス集計
        「立場」と「性別」など、2つのカテゴリの関係性を表にまとめ、グループごとの傾向を視覚化します。
        
        #### ⚖️ 群間比較
        「担任」と「支援員」など、2つのグループ間で特定の数値に統計的に意味のある差（有意差）があるかを検定します。
        
        #### ⏱ 前後比較
        研修の前後など、同じ対象の状況が変化したかを統計的に検定します。
        """)

# --- メイン画面 ---
st.title("📊 アンケートデータ統計分析アプリ")
st.write("アップロードしたCSVデータの簡単な統計分析と可視化を行います。")

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
tab1, tab2, tab3, tab4 = st.tabs(["① 記述統計", "② クロス集計", "③ 群間比較", "④ 前後比較"])

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
        
        # --- ★★★★★ グラフの修正箇所 ★★★★★ ---
        # 1. 各項目の平均値を計算
        df_mean = df[selected_cols_desc].mean().reset_index()
        df_mean.columns = ['項目', '平均値']

        # 2. ロングフォーマットのデータを作成（箱ひげ図用）
        df_melted = df[selected_cols_desc].melt(var_name='項目', value_name='値')
        
        col1, col2 = st.columns(2)
        with col1:
            # 3. 平均値のデータフレームを使って棒グラフを作成
            st.subheader("平均値の比較")
            fig_bar = px.bar(
                df_mean,
                x='項目',
                y='平均値',
                title='各項目の平均値',
                color='項目',
                text_auto=True # 棒グラフに数値を表示
            )
            fig_bar.update_traces(textposition='outside')
            fig_bar.update_layout(showlegend=False, yaxis_title="平均値")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            st.subheader("データの分布")
            fig_box = px.box(df_melted, x='項目', y='値', title='箱ひげ図', color='項目')
            fig_box.update_layout(showlegend=False, yaxis_title="値")
            st.plotly_chart(fig_box, use_container_width=True)

# --- タブ2: クロス集計 ---
with tab2:
    st.header("② クロス集計")
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
    st.header("③ 群間比較：t検定／U検定")
    st.write("2つのグループ間で、数値データに統計的に意味のある差（有意差）があるか検定します。")
    col1_group, col2_group = st.columns(2)
    with col1_group:
        group_col = st.selectbox("グループ分けに使う列（2つの値を持つ列）", cat_cols, key="test1")
    with col2_group:
        value_col = st.selectbox("比較する数値データ列", numeric_cols, key="test2")

    if group_col and value_col:
        groups = df[group_col].dropna().unique()
        if len(groups) != 2:
            st.warning(f"⚠️ グループ数が2つの列を選択してください。\n（現在選択されている'{group_col}'には{len(groups)}個のグループがあります: {list(groups)}）")
        else:
            g1 = df[df[group_col] == groups[0]][value_col].dropna()
            g2 = df[df[group_col] == groups[1]][value_col].dropna()

            st.write(f"**比較対象**: `{groups[0]}` (n={len(g1)}) vs `{groups[1]}` (n={len(g2)})")
            test_type = st.radio("検定方法の選択", ["t検定", "U検定（マン・ホイットニー検定）"], horizontal=True)
            
            st.markdown("---")
            if test_type == "t検定":
                st.info("_💡 **t検定**: 2つのグループの**平均値**に差があるか検定します。データが正規分布に近い場合に適しています。_")
                stat, p = stats.ttest_ind(g1, g2, equal_var=False) # 等分散を仮定しないWelchのt検定
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
            
            st.subheader("📦 箱ひげ図による可視化")
            fig = px.box(df, x=group_col, y=value_col, color=group_col, title=f"{group_col}別 {value_col}の分布", points="all")
            st.plotly_chart(fig, use_container_width=True)

# --- タブ4: 前後比較 ---
with tab4:
    st.header("④ 前後比較：対応のある検定")
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
            temp_df = df[[col_pre, col_post]].dropna() # 欠損値を含む行をペアで削除
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