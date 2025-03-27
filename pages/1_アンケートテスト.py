import streamlit as st
import pandas as pd
import datetime
import json
import os

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
    st.markdown(f"現在のID: `{user_id}`")

    if "questions_locked" not in st.session_state:
        st.session_state["questions_locked"] = False

    if not st.session_state["questions_locked"]:
        st.header("\ud83d\udd38 日常生活・意識について")
        st.session_state["q1"] = st.radio("普段から健康に気を使っていますか？", ["はい", "どちらともいえない", "いいえ"], key="q1")
        st.session_state["q2"] = st.text_input("1日に何食食べますか？", key="q2")
        st.session_state["q3"] = st.text_input("間食をする頻度は？", key="q3")
        st.session_state["q4"] = st.radio("栄養バランスを意識して食事を選びますか？", ["はい", "どちらともいえない", "いいえ"], key="q4")
        st.session_state["q5"] = st.radio("ダイエット経験はありますか？", ["はい", "どちらともいえない", "いいえ"], key="q5")

        st.header("\ud83d\udd38 健康・体型知識について")
        st.session_state["know_bmr"] = st.radio("\u300c基礎代謝\u300dという言葉を知っていますか？", ["はい", "いいえ"], key="know_bmr")
        st.session_state["know_bmi"] = st.radio("\u300cBMI\u300dという言葉を知っていますか？", ["はい", "いいえ"], key="know_bmi")

        if st.session_state["know_bmr"] == "はい":
            st.session_state["bmr_q1"] = st.radio("基礎代謝が高いほど痩せやすい？", ["はい", "いいえ"], key="bmr_q1")
            st.session_state["bmr_q2"] = st.radio("基礎代謝は年齢とともに下がる？", ["はい", "いいえ"], key="bmr_q2")

        if st.session_state["know_bmi"] == "はい":
            st.session_state["bmi_q1"] = st.radio("BMIは身長と体重から計算される？", ["はい", "いいえ"], key="bmi_q1")
            st.session_state["bmi_q2"] = st.radio("BMIが22だと病気になりにくい？", ["はい", "いいえ"], key="bmi_q2")

        if st.button("この回答内容で確定して次に進む"):
            st.session_state["questions_locked"] = True
            st.rerun()

    else:
        st.success("質問はすでに確定済みです。下のカロリーセクションへ進んでください。")
        st.markdown("### \ud83d\udd38 回答内容（確認用）")
        for q in ["q1", "q2", "q3", "q4", "q5", "know_bmr", "know_bmi", "bmr_q1", "bmr_q2", "bmi_q1", "bmi_q2"]:
            if q in st.session_state:
                st.write(f"{q}: {st.session_state[q]}")

        st.header("\ud83d\udd38 カロリー感覚・応用")
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

            base_data = {}
            try:
                with open(f"userdata/userdata_{user_id}.json", "r", encoding="utf-8") as f:
                    base_data = json.load(f)
            except FileNotFoundError:
                st.warning("main.py の情報が見つかりません。先に前ページで入力してください。")
                st.stop()

            survey_data = {
                "timestamp": now,
                "activity_level": activity_level,
                "activity_factor": activity_factor,
                "calculated_need_kcal": need_kcal,
                "kcal_input": kcal_input,
                "q1": st.session_state["q1"],
                "q2": st.session_state["q2"],
                "q3": st.session_state["q3"],
                "q4": st.session_state["q4"],
                "q5": st.session_state["q5"],
                "know_bmr": st.session_state["know_bmr"],
                "know_bmi": st.session_state["know_bmi"],
                "bmr_q1": st.session_state.get("bmr_q1", ""),
                "bmr_q2": st.session_state.get("bmr_q2", ""),
                "bmi_q1": st.session_state.get("bmi_q1", ""),
                "bmi_q2": st.session_state.get("bmi_q2", "")
            }

            result = {**base_data, **survey_data}

            os.makedirs("userdata", exist_ok=True)
            df = pd.DataFrame([result])
            df.to_csv(f"userdata/userdata_{user_id}_full.csv", index=False, encoding="utf-8-sig")
            with open(f"userdata/userdata_{user_id}_full.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            st.success("全データを保存しました。ありがとうございました！")

            with open(f"userdata/userdata_{user_id}_full.csv", "rb") as f:
                st.download_button(
                    label="全データ（CSV）をダウンロード",
                    data=f,
                    file_name=f"userdata_{user_id}_full.csv",
                    mime="text/csv"
                )
else:
    st.info("IDまたは基礎代謝量が不足しています。前のページからの入力が必要です。")
