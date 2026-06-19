# git test
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
plt.rcParams["font.family"] = "Meiryo"

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
    # LLM改善提案
    # =========================
    def make_learning_summary(df):
        total_hours = df["study_time"].sum()
        study_days = df["date"].dt.date.nunique()
        avg_understanding = df["understanding"].mean()

        subject_summary = (
            df.groupby("subject").agg(
                total_hours=("study_time", "sum"),
                avg_understanding=("understanding", "mean"),
                session_count=("subject", "count")
            )
            .reset_index()
            .sort_values("total_hours", ascending=False)
        )

        problem_summary = df["問題タイプ"].value_counts().reset_index()
        problem_summary.columns = ["問題タイプ", "件数"]

        recent_records = (
            df.sort_values("date").tail(10)[["date", "subject", "study_time", "understanding", "理解度レベル", "問題タイプ"]]
        )
        summary = f"""
[全体概要]
総学習時間: {total_hours:.1f}時間
学習日数: {study_days}日
平均理解度: {avg_understanding:.2f}

[科目別集計]
{subject_summary.to_string(index=False)}

[問題タイプ別件数]
{problem_summary.to_string(index=False)}

[直近の学習記録]
{recent_records.to_string(index=False)}
"""
        return summary
    
    def generate_llm_advice(df):
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        learning_summary = make_learning_summary(df)

        prompt = f"""
以下は、学習記録アプリから得られた学習データの集計結果です。

{learning_summary}

このデータをもとに、学習者に向けて以下の形式で日本語で改善提案をしてください。

出力形式:
1.全体の学習傾向
2.良い点
3.課題
4.科目別の改善提案
5.次の1週間で実行すべき具体的な行動計画

条件:
-厳しすぎず、現実的な提案にする
-学習時間と理解度の両方を考慮する
-抽象論ではなく、具体的な行動に落とし込む
-200~400字程度でまとめる
"""
        response = client.responses.create(
            model="gpt-5.5",
            input=prompt
        )
        return response.output_text
    
    # 表示

    st.subheader("LLMによる学習改善提案")

    st.write("現在の学習データをもとに、AIが改善提案を生成します。")

    if st.button("AI改善提案を生成"):
        try:
            with st.spinner("AIが学習状況を分析しています..."):
                advice = generate_llm_advice(df)
                st.markdown(advice)
        except Exception as e:
            st.error("AI改善提案の生成に失敗しました。APIキーや通信環境を確認してください。")
            st.exception(e)

    # =========================
    # 日付ごとの総学習時間グラフ
    # =========================
    st.subheader("総学習時間の推移")

    total_study_time = df.groupby('date')['study_time'].sum().reset_index()

    fig, ax = plt.subplots()
    ax.plot(total_study_time["date"], total_study_time["study_time"], marker = 'o')
    ax.set_xlabel("日付")
    ax.set_ylabel("総学習時間")
    fig.autofmt_xdate()
    st.pyplot(fig)

    # =========================
    # 科目別の総学習時間グラフ
    # =========================

    st.subheader('科目別総学習時間の推移')
    fig, ax = plt.subplots()

    for subject , group in df.groupby('subject'):
        total_study_time = group.groupby('date')['study_time'].sum().reset_index() 
        ax.plot(total_study_time["date"], total_study_time["study_time"], marker = 'o', label=subject)
    
    
    ax.set_xlabel("日付")
    ax.set_ylabel("科目別学習時間")
    fig.autofmt_xdate()

    ax.legend()
    st.pyplot(fig)

    