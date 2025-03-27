import streamlit as st
import pandas as pd

st.set_page_config(page_title="健康体型学習 事前アンケート", layout="centered")
st.title("健康体型学習：事前アンケート")

user_id = st.session_state.get("user_id", "")

if user_id:
    st.markdown(f"現在のID: `{user_id}`")
else:
    st.warning("IDが見つかりません。前のページで入力を済ませてから来てください。")

q_list = [
    "普段から健康に気を使っていますか？",
    "1日に何食食べますか？",  # ← これはあとで自由入力でもいいかも
    "間食をする頻度は？",
    "栄養バランスを意識して食事を選びますか？",
    "ダイエット経験はありますか？",
    "正しいダイエット知識に自信はありますか？",
    "基礎代謝という言葉を知っていますか？",
    "BMIという言葉を知っていますか？",
    "健康診断で体重を気にしたことはありますか？",
    "体型を変えるには何が必要だと思いますか？（自由回答）"
]

# 3択用の選択肢（自由回答が必要な場合は除外）
choices = ["はい", "どちらともいえない", "いいえ"]

answers = []
for i, q in enumerate(q_list):
    if i == 1 or i == 2 or i == 9:  # Q2, Q3, Q10だけ自由記述（または変更可能）
        ans = st.text_input(f"Q{i+1}: {q}", key=f"q{i}")
    else:
        ans = st.radio(f"Q{i+1}: {q}", choices, key=f"q{i}", horizontal=True)
    answers.append(ans)

if st.button("アンケートを送信"):
    if not user_id:
        st.warning("IDが取得できていません。前のページで入力してから来てください。")
    else:
        df_q = pd.DataFrame([{
            "user_id": user_id,
            **{f"q{i+1}": ans for i, ans in enumerate(answers)}
        }])
        q_filename = f"questionnaire_{user_id}.csv"
        df_q.to_csv(q_filename, index=False, encoding='utf-8-sig')
        st.success("アンケートのご協力ありがとうございました！")
        st.download_button(
            label="CSVをダウンロード（アンケート回答）",
            data=df_q.to_csv(index=False).encode('utf-8-sig'),
            file_name=q_filename,
            mime='text/csv'
        )
