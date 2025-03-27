import streamlit as st
import pandas as pd
import datetime
import json

st.set_page_config(page_title="健康体型学習 入力フォーム", layout="centered")
st.title("健康体型学習 入力フォーム")

# 入力欄
user_id = st.text_input("指定のIDを入力してください。")
age = st.number_input("年齢（18〜64歳）", min_value=18, max_value=64)
sex = st.selectbox(
    "性別（※計算式の関係上、生まれ持った性別を選択してください。）",
    ["男性（出生時）", "女性（出生時）"]
)
height = st.number_input("身長（cm、小数第1位まで。）", min_value=100.0, max_value=250.0, step=0.1, format="%.1f")
weight = st.number_input("体重（kg、小数第1位まで。）", min_value=30.0, max_value=200.0, step=0.1, format="%.1f")

# ✅ 体脂肪率：空欄可にするため text_input + float変換
body_fat_str = st.text_input("体脂肪率（%、小数第1位まで。空欄可）")
try:
    body_fat = float(body_fat_str) if body_fat_str else None
except ValueError:
    st.error("数値を入力してください。")
    body_fat = None

# ボタン押下で処理
if st.button("送信する"):
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    # ✅ 修正済：基礎代謝の式
    if sex == "男性（出生時）":
        bmr = (0.0481 * weight + 0.0234 * height - 0.0138 * age - 0.4235) * 1000 / 4.186
    else:
        bmr = (0.0481 * weight + 0.0234 * height - 0.0138 * age - 0.9708) * 1000 / 4.186

    now = datetime.datetime.now().isoformat()

    data = {
        "timestamp": now,
        "user_id": user_id,
        "age": age,
        "sex": sex,
        "height_cm": f"{height:.1f}",
        "weight_kg": f"{weight:.1f}",
        "body_fat": f"{body_fat:.1f}" if body_fat is not None else "",
        "bmi": round(bmi, 2),
        "bmr": round(bmr, 2)
    }

    df = pd.DataFrame([data])
    csv_filename = f"userdata_{user_id}.csv"
    json_filename = f"userdata_{user_id}.json"

    # 保存（CSV & JSON）
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    st.success("データが作成されました。以下のボタンを押してください。")
    st.download_button("CSVをダウンロード", data=df.to_csv(index=False).encode("utf-8-sig"), file_name=csv_filename, mime="text/csv")
    st.download_button("JSONをダウンロード（Unity用）", data=json.dumps(data, ensure_ascii=False, indent=2), file_name=json_filename, mime="application/json")

    # セッションに保存
    st.session_state["user_id"] = user_id
    st.session_state["bmr"] = round(bmr, 2)
    st.session_state["submitted"] = True

# 次ページへの案内
if st.session_state.get("submitted") and st.session_state.get("user_id"):
    st.markdown("### 次に進む")
    if st.button("➡ アンケート・テストに進む"):
        st.success("次のページに進んでください。")
        st.markdown("👉 サイドバーから『アンケート・テスト』ページを選択してください。")
