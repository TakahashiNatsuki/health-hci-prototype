import streamlit as st
import pandas as pd
import datetime
import json
import os
import urllib.parse

st.set_page_config(page_title="アンケート・テスト", layout="centered")
st.title("アンケート・テスト")

user_id = st.session_state.get("user_id", "")
bmr = st.session_state.get("bmr", None)

if not user_id:
    user_id = st.text_input("IDを入力してください（前のページと同じ）")

if bmr is None:
    bmr_input = st.text_input("基礎代謝量（前のページで計算された数値）を入力してください（kcal）")
    try:
        bmr = float(bmr_input)
    except ValueError:
        bmr = None
        st.error("数値を入力してください")

if user_id and bmr:
    st.markdown(f"現在のID: `{user_id}`　／　基礎代謝: `{round(bmr, 2)} kcal`")

    st.header("日常生活・意識について")
    q1 = st.radio("普段から健康に気を使っていますか？", ["はい", "どちらともいえない", "いいえ"], key="q1")
    q2 = st.text_input("1日に何食食べますか？", key="q2")
    q3 = st.text_input("間食をする頻度は？", key="q3")
    q4 = st.radio("栄養バランスを意識して食事を選びますか？", ["はい", "どちらともいえない", "いいえ"], key="q4")
    q5 = st.radio("ダイエット経験はありますか？", ["はい", "どちらともいえない", "いいえ"], key="q5")

    st.header("健康・体型知識について")
    know_bmr = st.radio("「基礎代謝」という言葉を知っていますか？", ["はい", "いいえ"])
    know_bmi = st.radio("「BMI」という言葉を知っていますか？", ["はい", "いいえ"])

    bmr_q1 = bmr_q2 = bmi_q1 = bmi_q2 = ""
    if know_bmr == "はい":
        bmr_q1 = st.radio("基礎代謝が高いほど痩せやすい？", ["はい", "いいえ"])
        bmr_q2 = st.radio("基礎代謝は年齢とともに下がる？", ["はい", "いいえ"])
    if know_bmi == "はい":
        bmi_q1 = st.radio("BMIは身長と体重から計算される？", ["はい", "いいえ"])
        bmi_q2 = st.radio("BMIが22だと病気になりにくい？", ["はい", "いいえ"])

    kcal_input = st.text_input("自分に必要な1日のカロリー量は何kcalくらいだと思いますか？（数値で）")

    activity_level = st.radio(
        "あなたの日常での運動レベルを選んでください",
        [
            "低い：生活の大部分が座位で、静的な活動が中心の場合",
            "ふつう：座位中心の仕事だが、移動や立ち作業などが含まれる場合",
            "高い：移動・立位が多い仕事や、活発な運動習慣がある場合"
        ]
    )

    if "低い" in activity_level:
        activity_factor = 1.5
    elif "ふつう" in activity_level:
        activity_factor = 1.75
    else:
        activity_factor = 2.0

    need_kcal = round(bmr * activity_factor, 2)

    if st.button("送信して保存"):
        now = datetime.datetime.now().isoformat()
        result = {
            "timestamp": now,
            "user_id": user_id,
            "bmr": round(bmr, 2),
            "activity_level": activity_level,
            "activity_factor": activity_factor,
            "calculated_need_kcal": need_kcal,
            "kcal_input": kcal_input,
            "q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5,
            "know_bmr": know_bmr, "know_bmi": know_bmi,
            "bmr_q1": bmr_q1, "bmr_q2": bmr_q2,
            "bmi_q1": bmi_q1, "bmi_q2": bmi_q2
        }

        os.makedirs("userdata", exist_ok=True)
        df = pd.DataFrame([result])
        df.to_csv(f"userdata/userdata_{user_id}_qa.csv", index=False, encoding="utf-8-sig")
        with open(f"userdata/userdata_{user_id}_qa.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        st.success("回答を保存しました。")

        # クエリ文字列生成（Unity用URL）
        query = urllib.parse.urlencode(result)
        unity_url = f"https://your-unity-app-url.netlify.app/?{query}"

        st.markdown("### 続けて教材に進みますか？")
        if st.button("Unity教材に進む"):
            st.markdown(
                f'<meta http-equiv="refresh" content="0;url={unity_url}">',
                unsafe_allow_html=True
            )

else:
    st.info("IDまたは基礎代謝量が不足しています。前のページからの入力が必要です。")
