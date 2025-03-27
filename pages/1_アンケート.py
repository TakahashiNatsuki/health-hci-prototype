import streamlit as st
import pandas as pd
import datetime
import json

st.set_page_config(page_title="健康体型学習 アンケート＋知識テスト", layout="centered")
st.title("健康体型学習：アンケート＋知識テスト")

# ID取得（セッション or 入力）
user_id = st.session_state.get("user_id", "")
if not user_id:
    user_id = st.text_input("IDを入力してください（前のページで設定したもの）")

# 基礎代謝（BMR）取得（セッション or 仮値）
bmr = st.session_state.get("bmr", 1400.0)

if user_id:
    st.markdown(f"現在のID: `{user_id}`")

    st.header("🔸 意識調査")
    q1 = st.radio("普段から健康に気を使っていますか？", ["はい", "どちらともいえない", "いいえ"])
    q2 = st.text_input("1日に何食食べますか？")
    q3 = st.text_input("間食をする頻度は？")
    q4 = st.radio("栄養バランスを意識して食事を選びますか？", ["はい", "どちらともいえない", "いいえ"])
    q5 = st.radio("ダイエット経験はありますか？", ["はい", "どちらともいえない", "いいえ"])
    q6 = st.radio("体型を変えるには何が必要だと思いますか？", ["運動", "食事", "両方", "その他"])

    st.header("🔸 知識テスト（自己申告）")
    know_bmr = st.radio("「基礎代謝」という言葉を知っていますか？", ["はい", "いいえ"])
    know_bmi = st.radio("「BMI」という言葉を知っていますか？", ["はい", "いいえ"])

    st.header("🔸 知識テスト（内容理解）")
    if know_bmr == "はい":
        bmr_q1 = st.radio("基礎代謝が高いほど痩せやすい？", ["はい", "いいえ"])
        bmr_q2 = st.radio("基礎代謝は年齢とともに下がる？", ["はい", "いいえ"])
    else:
        bmr_q1, bmr_q2 = "", ""

    if know_bmi == "はい":
        bmi_q1 = st.radio("BMIは身長と体重から計算される？", ["はい", "いいえ"])
        bmi_q2 = st.radio("BMIが22だと病気になりにくい？", ["はい", "いいえ"])
    else:
        bmi_q1, bmi_q2 = "", ""

    st.header("🔸 応用問題")
    kcal_input = st.text_input("自分に必要な1日のカロリー量は何kcalくらいだと思いますか？（数値で）")

    activity_level = st.radio(
        "自分の日常の運動レベルはどれに当てはまると思いますか？",
        [
            "低い：生活の大部分が座位で、静的な活動が中心の場合",
            "ふつう：座位中心の仕事だが、移動や立ち作業などが含まれる場合",
            "高い：移動・立位が多い仕事や、活発な運動習慣がある場合"
        ]
    )

    # 活動係数を決定
    if "低い" in activity_level:
        activity_factor = 1.5
    elif "ふつう" in activity_level:
        activity_factor = 1.75
    else:
        activity_factor = 2.0

    need_kcal = round(bmr * activity_factor, 2)

    if st.button("送信して保存"):
        now = datetime.datetime.now().isoformat()
        data = {
            "timestamp": now,
            "user_id": user_id,
            "q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5, "q6": q6,
            "know_bmr": know_bmr, "know_bmi": know_bmi,
            "bmr_q1": bmr_q1, "bmr_q2": bmr_q2,
            "bmi_q1": bmi_q1, "bmi_q2": bmi_q2,
            "kcal_input": kcal_input,
            "activity_level_self": activity_level,
            "activity_factor": activity_factor,
            "calculated_need_kcal": need_kcal,
            "bmr_from_previous": bmr
        }

        df = pd.DataFrame([data])
        csv_filename = f"full_questionnaire_{user_id}.csv"
        json_filename = f"user_data_{user_id}.json"

        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        st.success("回答が保存されました。")
        st.download_button("CSVをダウンロード", data=df.to_csv(index=False).encode("utf-8-sig"),
                           file_name=csv_filename, mime="text/csv")
        st.download_button("JSONをダウンロード（Unity用）", data=json.dumps(data, ensure_ascii=False, indent=2),
                           file_name=json_filename, mime="application/json")
else:
    st.info("IDを入力してください。")
