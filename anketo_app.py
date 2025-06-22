import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager as fm
import matplotlib as mpl

# フォント設定
font_path = os.path.abspath("ipaexg.ttf")  # 絶対パス
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    mpl.rcParams["font.family"] = font_prop.get_name()
    plt.rc("font", family=font_prop.get_name())
    st.write(f"✅ フォント設定: {mpl.rcParams['font.family']}")
else:
    st.error("❌ フォントファイルが見つかりません。")
    
st.title("アンケートデータ統計分析アプリ")
# 初心者向け説明の表示切り替え
if "show_explanation" not in st.session_state:
           st.session_state.show_explanation = False
        # ボタンを押すたびにセッションステートを切り替える
if st.button("説明を表示/非表示"):
           st.session_state.show_explanation = not st.session_state.show_explanation

         # セッションステートに基づいて説明を表示
if st.session_state.show_explanation:
           st.markdown("""
                       
#### 🔍 記述統計とは？
記述統計は、データの「ざっくりとした特徴」を数値で表す方法です。

- **平均**：全員の得点を足して人数で割った「ふつうの点」。
- **中央値**：ちょうど真ん中の人の点数（極端な値に影響されません）。
- **標準偏差**：点数のバラつき具合。大きいと「個人差が大きい」、小さいと「だいたいみんな同じ」。

グラフも使って、どんな傾向があるかをわかりやすく見てみましょう。

                
#### 🔄 クロス集計とは？
クロス集計は、「ある2つの項目の関係」をまとめて見られる表です。

たとえば、\
- **「立場（担任・支援員）」と「満足度の回答」**をクロスして、\
- どの立場の人がどんな回答をしているのかを比べることができます。

積み上げ棒グラフも使って、\
グループごとの違いを直感的に確認できます。


#### ⚖ 群間比較とは？
「2つのグループに違いがあるか？」を**統計的に判断する方法**です。

- たとえば、「担任」と「支援員」で、満足度に違いがあるのか？
- または、「男子」と「女子」で、点数の差はあるのか？など。

使う検定方法は2つ：

- **t検定**：データが「ふつうに分布」しているとき使います。
- **U検定（マン・ホイットニー検定）**：データの分布がバラバラなときでも使えます（ノンパラメトリック）。

**p値**が0.05未満だと「違いがある」と判断します。
                
#### ⏱ 前後比較とは？
同じ人の**「ビフォー（事前）」と「アフター（事後）」**の変化を見る方法です。

たとえば…

- 研修の前と後で、先生の理解度は上がった？
- 支援の前後で、子どもの行動はどう変わった？など。

検定方法は2つ：

- **対応のあるt検定**：変化が「正規分布」していそうなとき。
- **ウィルコクソン検定**：変化がバラバラなときでも使える。

グラフで「平均の変化」や「ばらつきの変化」も見てみましょう。
           

""")            

st.subheader("📥 サンプルCSVのダウンロード")

# サンプルデータを定義
sample_data = {
    "氏名": ["小山貴之", "佐藤花子", "鈴木一郎"],
    "性別": ["男", "女", "男"],
    "立場": ["担任", "支援員", "担任"],
    "支援の目標が共有されている": [5, 4, 3],
    "役割分担は明確である": [4, 3, 4],
    "支援の方針について話し合っている": [5, 4, 4],
    "事前評価": [60, 55, 58],
    "事後評価": [75, 70, 72]
}
df_sample = pd.DataFrame(sample_data)

# ダウンロードボタン
csv = df_sample.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📄 サンプルCSVをダウンロード",
    data=csv,
    file_name="sample_survey.csv",
    mime="text/csv"
)

# CSVアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("データプレビュー", df.head())

    # --- 数値列とカテゴリ列をここで一度定義しておくと、後続の処理で再利用できます ---
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    st.subheader("① 記述統計（平均・中央値・標準偏差）")
    
    selected_cols = st.multiselect("分析したい数値列を選択", numeric_cols)

    if selected_cols:
        desc = df[selected_cols].describe().T
        desc["median"] = df[selected_cols].median()
        st.dataframe(desc)
        
        # 棒グラフ表示
        st.write("📊 平均値の棒グラフ（選択列）")
        fig, ax = plt.subplots()
        means = df[selected_cols].mean()
        means.plot(kind='bar', ax=ax)
        ax.set_ylabel("平均値", fontproperties=font_prop)
        ax.set_title("各項目の平均値", fontproperties=font_prop)
        ax.tick_params(axis='x', labelrotation=45)
        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)
        st.pyplot(fig)

        # 箱ひげ図表示
        st.write("📦 箱ひげ図（選択列）")
        fig, ax = plt.subplots()
        sns.boxplot(data=df[selected_cols], ax=ax)
        ax.set_ylabel("値", fontproperties=font_prop)
        ax.set_title("各項目の箱ひげ図", fontproperties=font_prop)
        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)
        st.pyplot(fig)        
        
    st.subheader("② クロス集計")
    
    col1 = st.selectbox("行に使うカテゴリ列", cat_cols, key="cross1")
    col2 = st.selectbox("列に使うカテゴリ列", cat_cols, key="cross2")
    if col1 and col2:
        cross_tab = pd.crosstab(df[col1], df[col2])
        st.dataframe(cross_tab)

        # 棒グラフ表示
        st.write("📊 クロス集計の棒グラフ")
        fig, ax = plt.subplots()
        cross_tab.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title("クロス集計結果（積み上げ棒グラフ）", fontproperties=font_prop)
        ax.set_xlabel(col1, fontproperties=font_prop)
        ax.set_ylabel("件数", fontproperties=font_prop)
        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)
        
        # <<< 修正箇所：凡例の日本語フォントを設定 >>>
        ax.legend(title=col2, prop=font_prop, title_fontproperties=font_prop)
        
        st.pyplot(fig)                

    st.subheader("③ 群間比較：t検定／U検定")
    
    group_col = st.selectbox("グループを分ける列（例：担任・支援員）", cat_cols, key="test1")
    value_col = st.selectbox("数値データ列（例：満足度など）", numeric_cols, key="test2")

    if group_col and value_col:
        groups = df[group_col].dropna().unique()
        if len(groups) == 2:
            g1 = df[df[group_col] == groups[0]][value_col].dropna()
            g2 = df[df[group_col] == groups[1]][value_col].dropna()

            st.write(f"対象グループ: {groups[0]} vs {groups[1]}")
            test_type = st.radio("検定方法の選択", ["t検定", "U検定"])
            if test_type == "t検定":
                stat, p = stats.ttest_ind(g1, g2, equal_var=False)
            else:
                stat, p = stats.mannwhitneyu(g1, g2, alternative="two-sided")

            st.write(f"検定統計量: {stat:.3f}, p値: {p:.4f}")
            if p < 0.05:
                st.success("有意差あり（p < 0.05）")
            else:
                st.info("有意差なし（p ≥ 0.05）")

            # 箱ひげ図
            st.write("📦 群間比較の箱ひげ図")
            fig, ax = plt.subplots()
            sns.boxplot(x=group_col, y=value_col, data=df, ax=ax)
            ax.set_title("群間比較（箱ひげ図）", fontproperties=font_prop)
            ax.set_xlabel("グループ", fontproperties=font_prop)
            ax.set_ylabel("値", fontproperties=font_prop)
            for label in ax.get_xticklabels():
                label.set_fontproperties(font_prop)
            st.pyplot(fig)                      

    st.subheader("④ 前後比較：対応のあるt検定 or ウィルコクソン検定")
    
    col_pre = st.selectbox("事前（Before）データ列", numeric_cols, key="before")
    col_post = st.selectbox("事後（After）データ列", numeric_cols, key="after")

    if col_pre and col_post:
        before = df[col_pre].dropna()
        after = df[col_post].dropna()
        if len(before) == len(after):
            test_type = st.radio("使用する検定", ["対応のあるt検定", "ウィルコクソン検定"])
            if test_type == "対応のあるt検定":
                stat, p = stats.ttest_rel(before, after)
            else:
                stat, p = stats.wilcoxon(before, after)

            st.write(f"検定統計量: {stat:.3f}, p値: {p:.4f}")
            if p < 0.05:
                st.success("有意な変化あり（p < 0.05）")
            else:
                st.info("有意な変化なし（p ≥ 0.05）")

            # 前後の棒グラフ
            st.write("📊 前後比較の平均値（棒グラフ）")
            fig, ax = plt.subplots()
            means = pd.Series([before.mean(), after.mean()], index=["事前", "事後"])
            means.plot(kind="bar", ax=ax)
            ax.set_ylabel("平均値", fontproperties=font_prop)
            ax.set_title("事前・事後の平均値比較", fontproperties=font_prop)
            for label in ax.get_xticklabels():
                label.set_fontproperties(font_prop)
            st.pyplot(fig)            
            
            # 前後の箱ひげ図
            st.write("📦 前後比較の箱ひげ図")
            fig, ax = plt.subplots()
            sns.boxplot(data=[before, after], ax=ax)
            ax.set_xticklabels(["事前", "事後"], fontproperties=font_prop)
            ax.set_title("事前・事後の箱ひげ図", fontproperties=font_prop)
            ax.set_ylabel("値", fontproperties=font_prop)
            st.pyplot(fig)            
            
        else:
            st.warning("事前と事後のデータ数が一致していません。")