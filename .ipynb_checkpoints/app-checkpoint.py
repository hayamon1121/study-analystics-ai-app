import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# タイトル
# =========================
st.title("学習記録・可視化AI")

st.write("CSVをアップロードしてください")

# =========================
# CSVアップロード
# =========================
uploaded_file = st.file_uploader("学習ログCSV", type="csv")

    
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, parse_dates=["date"])

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")    
    st.subheader("学習データ")
    st.dataframe(df)

    # =========================
    # STEP4：ルールベース分析
    # =========================
    def understanding_level(x):
        if x <= 2:
            return "低"
        elif x == 3:
            return "中"
        else:
            return "高"

    df["理解度レベル"] = df["understanding"].apply(understanding_level)

    avg_study_time = df["study_time"].mean()

    def diagnose_problem(row):
        if row["理解度レベル"] == "低":
            if row["study_time"] < avg_study_time:
                return "努力不足"
            else:
                return "理解不足"
        else:
            return "問題なし"

    df["問題タイプ"] = df.apply(diagnose_problem, axis=1)

    def recommend_action(problem_type):
        if problem_type == "努力不足":
            return "学習時間を増やしましょう"
        elif problem_type == "理解不足":
            return "別教材や復習を検討しましょう"
        else:
            return "この調子で継続しましょう"

    df["推薦アクション"] = df["問題タイプ"].apply(recommend_action)

    # =========================
    # 結果表示
    # =========================
    st.subheader("分析・推薦結果")
    st.dataframe(df)

    # =========================
    # グラフ
    # =========================
    st.subheader("学習時間の推移")


    fig, ax = plt.subplots()
    ax.plot(df["date"], df["study_time"])
    ax.set_xlabel("日付")
    ax.set_ylabel("学習時間")
    st.pyplot(fig)

   

