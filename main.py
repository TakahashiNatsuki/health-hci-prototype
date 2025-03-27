import streamlit as st
import pandas as pd
import datetime
import json
import os

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

# 空欄OKな体脂肪率入力
body_fat_str = st.text_input("体脂肪率（%、小数第1位まで。空欄可）")
try:
    body_fat = float(body_fat_str) if body_fat_str else None
except ValueError:
    st.error("数値を入力してください。")
    body_fat = None

if st.button("送信する"):
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    # 修正済みの基礎代謝計算式
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

    # サーバー側保存
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ローカル保存（バックアップ用）
    local_csv_path = os.path.join("userdata", csv_filename)
    local_json_path = os.path.join("userdata", json_filename)
    os.makedirs("userdata", exist_ok=True)
    df.to_csv(local_csv_path, index=False, encoding='utf-8-sig')
    with open(local_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # セッションに保存
    st.session_state["user_id"] = user_id
    st.session_state["bmr"] = round(bmr, 2)
    st.session_state["go_to_questionnaire"] = True

    st.success("データが保存されました。アンケートに移動します。")

# 次の描画フレームで遷移（go_to_questionnaire が True の場合）
if st.session_state.get("go_to_questionnaire", False):
    st.session_state["go_to_questionnaire"] = False
    st.switch_page("pages/1_questionnaire_test.py")
