import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager as fm
import matplotlib as mpl
import plotly.express as px  # Plotlyをインポート

# --- 関数定義 ---
# CSVダウンロードボタンを生成する関数
def df_to_csv_download_button(df, filename):
    csv = df.to_csv(index=True).encode('utf-8-sig') # index=Trueでクロス集計の行名も保存
    st.download_button(
        label="📄 この表をCSVでダウンロード",
        data=csv,
        file_name=f'{filename}.csv',
        mime='text/csv',
    )

# --- フォント設定（変更なし） ---
font_path = os.path.abspath("ipaexg.ttf")
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    mpl.rcParams["font.family"] = font_prop.get_name()
    plt.rc("font", family=font_prop.get_name())
else:
    st.error("❌ フォントファイルが見つかりません。")

# --- サイドバーの設定 ---
with st.sidebar:
    st.header("1. データ準備")
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
    
    st.subheader("📥 サンプルCSVのダウンロード")
    sample_data = {
        "氏名": ["山田太郎", "佐藤花子", "鈴木一郎", "田中次郎", "高橋三郎", "伊藤さくら"],
        "立場": ["担任", "支援員", "担任", "支援員", "担任", "支援員"],
        "性別": ["男性", "女性", "男性", "男性", "男性", "女性"], # 新しいカテゴリ列
        "支援の目標が共有されている": [5, 4, 3, 5, 4, 3],
        "役割分担は明確である": [4, 3, 4, 4, 5, 2],
        "支援の方針について話し合っている": [5, 4, 4, 5, 5, 3],
        "事前評価": [60, 55, 58, 70, 65, 62],
        "事後評価": [75, 70, 72, 85, 80, 75]
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
        「担任」と「支援員」など、2つのグループ間で特定の数値（満足度など）に統計的に意味のある差（有意差）があるかを検定します。
        
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
df = pd.read_csv(uploaded_file)
with st.expander("アップロードしたデータのプレビュー", expanded=False):
    st.dataframe(df)

# 列タイプを自動で取得
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

# 分析タブを作成
tab1, tab2, tab3, tab4 = st.tabs(["① 記述統計", "② クロス集計", "③ 群間比較", "④ 前後比較"])

# --- タブ1: 記述統計 ---
with tab1:
    st.header("① 記述統計")
    selected_cols_desc = st.multiselect("分析したい数値列を選択", numeric_cols, key="desc_cols")

    if selected_cols_desc:
        desc = df[selected_cols_desc].describe().T
        desc["median"] = df[selected_cols_desc].median()
        st.write("要約統計量")
        st.dataframe(desc)
        df_to_csv_download_button(desc, "descriptive_stats")

        # Plotlyでインタラクティブなグラフを作成
        st.write("📊 各項目の可視化")
        df_melted = df[selected_cols_desc].melt(var_name='項目', value_name='値')
        
        col1, col2 = st.columns(2)
        with col1:
            fig_bar = px.bar(df_melted, x='項目', y='値', title='平均値の棒グラフ', labels={'値': '平均値'}, color='項目')
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            fig_box = px.box(df_melted, x='項目', y='値', title='箱ひげ図', color='項目')
            fig_box.update_layout(showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

# --- タブ2: クロス集計 ---
with tab2:
    st.header("② クロス集計")
    col1_cross, col2_cross = st.columns(2)
    with col1_cross:
        row_col = st.selectbox("行に使うカテゴリ列", cat_cols, key="cross1")
    with col2_cross:
        col_col = st.selectbox("列に使うカテゴリ列", cat_cols, key="cross2")

    if row_col and col_col:
        if row_col == col_col:
            st.warning("行と列には異なる列を選択してください。")
        else:
            cross_tab = pd.crosstab(df[row_col], df[col_col])
            st.write(f"「{row_col}」と「{col_col}」のクロス集計表")
            st.dataframe(cross_tab)
            df_to_csv_download_button(cross_tab, f"crosstab_{row_col}_vs_{col_col}")

            st.write("📊 クロス集計の棒グラフ")
            fig = px.bar(cross_tab, barmode='stack', title="積み上げ棒グラフ")
            fig.update_layout(xaxis_title=row_col, yaxis_title="件数")
            st.plotly_chart(fig, use_container_width=True)

# --- タブ3: 群間比較 ---
with tab3:
    st.header("③ 群間比較：t検定／U検定")
    col1_group, col2_group = st.columns(2)
    with col1_group:
        group_col = st.selectbox("グループを分ける列", cat_cols, key="test1")
    with col2_group:
        value_col = st.selectbox("比較する数値データ列", numeric_cols, key="test2")

    if group_col and value_col:
        groups = df[group_col].dropna().unique()
        if len(groups) != 2:
            st.warning(f"⚠️ グループ数が2つの列を選択してください。\n（現在選択されている'{group_col}'には{len(groups)}個のグループがあります: {list(groups)}）")
        else:
            g1 = df[df[group_col] == groups[0]][value_col].dropna()
            g2 = df[df[group_col] == groups[1]][value_col].dropna()

            st.write(f"**対象グループ**: {groups[0]} (n={len(g1)}) vs {groups[1]} (n={len(g2)})")
            test_type = st.radio("検定方法の選択", ["t検定", "U検定（マン・ホイットニー検定）"], horizontal=True)
            
            if test_type == "t検定":
                stat, p = stats.ttest_ind(g1, g2, equal_var=False)
            else:
                stat, p = stats.mannwhitneyu(g1, g2, alternative="two-sided")

            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric(label="検定統計量", value=f"{stat:.3f}")
            with res_col2:
                st.metric(label="p値", value=f"{p:.4f}")

            if p < 0.05:
                st.success(f"**結論: {groups[0]}と{groups[1]}の間には、統計的に有意な差があると言えます。** (p < 0.05)")
            else:
                st.info(f"**結論: {groups[0]}と{groups[1]}の間に、統計的に有意な差があるとは言えません。** (p ≥ 0.05)")

            st.write("📦 箱ひげ図による可視化")
            fig = px.box(df, x=group_col, y=value_col, color=group_col, title=f"{group_col}別 {value_col}の分布")
            st.plotly_chart(fig, use_container_width=True)

# --- タブ4: 前後比較 ---
with tab4:
    st.header("④ 前後比較：対応のあるt検定 or ウィルコクソン検定")
    col1_pre, col2_post = st.columns(2)
    with col1_pre:
        col_pre = st.selectbox("事前（Before）データ列", numeric_cols, key="before")
    with col2_post:
        col_post = st.selectbox("事後（After）データ列", numeric_cols, key="after")

    if col_pre and col_post:
        if col_pre == col_post:
            st.warning("事前と事後には異なる列を選択してください。")
        else:
            # 欠損値を含む行をペアで削除
            temp_df = df[[col_pre, col_post]].dropna()
            before = temp_df[col_pre]
            after = temp_df[col_post]
            
            if len(before) == 0:
                st.warning("比較できる有効なデータがありません。")
            else:
                st.write(f"**比較対象**: {col_pre} vs {col_post} (n={len(before)})")
                test_type_rel = st.radio("使用する検定", ["対応のあるt検定", "ウィルコクソン検定"], horizontal=True)
                
                if test_type_rel == "対応のあるt検定":
                    stat, p = stats.ttest_rel(before, after)
                else:
                    stat, p = stats.wilcoxon(before, after)

                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric(label="検定統計量", value=f"{stat:.3f}")
                with res_col2:
                    st.metric(label="p値", value=f"{p:.4f}")

                if p < 0.05:
                    st.success("**結論: 事前と事後で統計的に有意な変化が見られます。** (p < 0.05)")
                else:
                    st.info("**結論: 事前と事後で統計的に有意な変化は見られませんでした。** (p ≥ 0.05)")

                # 前後比較の可視化
                df_plot = pd.DataFrame({'平均値': [before.mean(), after.mean()]}, index=['事前', '事後'])
                fig = px.bar(df_plot, y='平均値', color=df_plot.index, title='事前・事後の平均値比較')
                st.plotly_chart(fig, use_container_width=True)