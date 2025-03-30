import streamlit as st
import pandas as pd
import datetime
import json
import io
import csv

st.set_page_config(page_title="事前アンケート・テスト", layout="centered")
st.title("事前アンケート・テスト")

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
    st.session_state["user_id"] = user_id
    st.session_state["bmr"] = bmr
    st.markdown(f"現在のID: `{user_id}`")

    if "questions_locked" not in st.session_state:
        st.session_state["questions_locked"] = False

    if not st.session_state["questions_locked"]:
        st.header("日常生活・意識について")
        q1 = st.radio("普段から健康に気を使っていますか？", ["はい", "どちらともいえない", "いいえ"], key="q1")
        q2 = st.text_input("1日に何食食べますか？", key="q2")
        q3 = st.text_input("間食をする頻度は？", key="q3")
        q4 = st.radio("栄養バランスを意識して食事を選びますか？", ["はい", "どちらともいえない", "いいえ"], key="q4")
        q5 = st.radio("ダイエット経験はありますか？", ["はい", "どちらともいえない", "いいえ"], key="q5")

        st.header("健康・体型知識について")
        know_bmr = st.radio("「基礎代謝」という言葉を知っていますか？", ["はい", "いいえ"], key="know_bmr")
        know_bmi = st.radio("「BMI」という言葉を知っていますか？", ["はい", "いいえ"], key="know_bmi")

        bmr_q1 = bmr_q2 = bmi_q1 = bmi_q2 = ""
        if know_bmr == "はい":
            bmr_q1 = st.radio("基礎代謝が高いほど痩せやすい？", ["はい", "いいえ"], key="bmr_q1")
            bmr_q2 = st.radio("基礎代謝は年齢とともに下がる？", ["はい", "いいえ"], key="bmr_q2")
        if know_bmi == "はい":
            bmi_q1 = st.radio("BMIは身長と体重から計算される？", ["はい", "いいえ"], key="bmi_q1")
            bmi_q2 = st.radio("BMIが22だと病気になりにくい？", ["はい", "いいえ"], key="bmi_q2")

        if st.button("この内容で確定して次に進む"):
            st.session_state["questions_locked"] = True
            st.rerun()

    else:
        st.success("質問はすでに確定済みです。下のカロリーセクションへ進んでください。")
        st.markdown("### 回答内容（確認用）")
        for k in ["q1", "q2", "q3", "q4", "q5", "know_bmr", "know_bmi", "bmr_q1", "bmr_q2", "bmi_q1", "bmi_q2"]:
            if k in st.session_state:
                st.markdown(f"- **{k}**: {st.session_state[k]}")

        st.header("カロリー感覚・応用")
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
            }
            for k in ["q1", "q2", "q3", "q4", "q5", "know_bmr", "know_bmi", "bmr_q1", "bmr_q2", "bmi_q1", "bmi_q2"]:
                if k in st.session_state:
                    result[k] = st.session_state[k]

            st.session_state["saved_result"] = result
            st.session_state["saved"] = True
            st.rerun()

        if st.session_state.get("saved", False):
            result = st.session_state["saved_result"]
            st.success("回答を保存しました。下からダウンロードしてください。")

            df = pd.DataFrame([result])
            csv_bytes = io.BytesIO()
            df.to_csv(csv_bytes, index=False, encoding="shift_jis", quoting=csv.QUOTE_ALL)
            csv_bytes.seek(0)

            st.download_button(
                label="📥 CSVでダウンロード",
                data=csv_bytes,
                file_name=f"userdata_{user_id}_qa.csv",
                mime="text/csv"
            )

            json_str = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSONでダウンロード",
                data=json_str,
                file_name=f"userdata_{user_id}_qa.json",
                mime="application/json"
            )

            # ✅ Unity に userData を postMessage で送信（iframe）
            st.markdown("### Unity教材")
            st.components.v1.html(f"""
                <iframe id="unity-frame" src="https://silver-babka-01dea4.netlify.app/" width="100%" height="800px" style="border:none;"></iframe>
                <script>
                    const userData = {json_str};

                    // Unity が Ready と言ってきたら userData を postMessage で送る
                    window.addEventListener("message", function (event) {{
                        if (event.data === "UnityReady") {{
                            const iframe = document.getElementById("unity-frame");
                            if (iframe && iframe.contentWindow) {{
                                iframe.contentWindow.postMessage(userData, "*");
                                console.log("✅ userData を送信しました");
                            }}
                        }}
                    }});
                </script>
            """, height=820)

else:
    st.info("IDまたは基礎代謝量が不足しています。前のページからの入力が必要です。")
