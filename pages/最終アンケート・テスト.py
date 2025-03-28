import streamlit as st
import pandas as pd
import datetime
import json
import os

st.set_page_config(page_title="最終アンケート・テスト", layout="centered")
st.title("最終アンケート・テスト")

user_id = st.session_state.get("user_id", "")
if not user_id:
    user_id = st.text_input("IDを入力してください（前のページと同じ）")

if user_id:
    st.markdown(f"現在のID: `{user_id}`")

    st.header("今回の教材について")
    f1 = st.radio("今回の教材（Unity教材）は分かりやすかったですか？", ["はい", "どちらともいえない", "いいえ"])
    f2 = st.radio("実生活に役立つと感じましたか？", ["はい", "どちらともいえない", "いいえ"])
    f3 = st.radio("健康や体型への意識が高まりましたか？", ["はい", "どちらともいえない", "いいえ"])
    f4 = st.radio("このような教材を今後も使いたいと思いますか？", ["はい", "どちらともいえない", "いいえ"])
    f5 = st.text_area("自由記述欄（ご意見・ご感想などがあればご記入ください）")

    if st.button("送信して終了"):
        now = datetime.datetime.now().isoformat()
        result = {
            "timestamp": now,
            "user_id": user_id,
            "f1": f1,
            "f2": f2,
            "f3": f3,
            "f4": f4,
            "f5": f5
        }

        SAVE_DIR = "/mount/data/userdata"
        os.makedirs(SAVE_DIR, exist_ok=True)
        df = pd.DataFrame([result])
        df.to_csv(os.path.join(SAVE_DIR, f"userdata_{user_id}_final.csv"), index=False, encoding="utf-8-sig")
        with open(os.path.join(SAVE_DIR, f"userdata_{user_id}_final.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        st.success("ご協力ありがとうございました。アンケートはこれで終了です。")
else:
    st.info("IDが不足しています。前のページからの入力が必要です。")

