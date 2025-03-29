import streamlit as st
import pandas as pd
import datetime
import json
import io
import csv

st.set_page_config(page_title="最終アンケート・テスト", layout="centered")
st.title("最終アンケート・テスト")

# ✅ IDを再入力させず、前ページから自動取得
user_id = st.session_state.get("user_id", "")

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

        st.success("ご協力ありがとうございました。下からデータをダウンロードしてください。")

        # CSV（Shift_JIS）
        df = pd.DataFrame([result])
        csv_bytes = io.BytesIO()
        df.to_csv(csv_bytes, index=False, encoding="shift_jis", quoting=csv.QUOTE_ALL)
        csv_bytes.seek(0)
        st.download_button(
            label="📥 CSVでダウンロード（最終アンケート）",
            data=csv_bytes,
            file_name=f"userdata_{user_id}_final.csv",
            mime="text/csv"
        )

        # JSON
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 JSONでダウンロード（最終アンケート）",
            data=json_str,
            file_name=f"userdata_{user_id}_final.json",
            mime="application/json"
        )

else:
    st.warning("前のページからIDが正しく引き継がれていません。最初のページからやり直してください。")
