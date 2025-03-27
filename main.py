import streamlit as st
import pandas as pd
import datetime
import os

st.title("健康診断用 入力フォーム")

# 入力欄
user_id = st.text_input("ID（ニックネームやイニシャルでもOK）")

age = st.number_input("年齢（18〜64歳）", min_value=18, max_value=64)

sex = st.radio(
    "※計算式の関係上、生まれ持った性別を選択してください。",
    ["男性（出生時）", "女性（出生時）"]
)

height = st.number_input("身長（cm、小数第1位までOK）", min_value=100.0, max_value=250.0, step=0.1)

weight = st.number_input("体重（kg、小数第1位までOK）", min_value=30.0, max_value=200.0, step=0.1)

body_fat = st.number_input("体脂肪率（%）（任意）", min_value=0.0, max_value=60.0, step=0.1)

activity = st.selectbox(
    "あなたの運動レベルを選んでください（以下を参考にしてください）",
    [
        "低い：生活の大部分が座位で、静的な活動が中心の場合",
        "ふつう：座位中心の仕事だが、職場内での移動や立位での作業・接客等、あるいは通勤・買物・家事、軽いスポーツ等のいずれかを含む場合",
        "高い：移動や立位の多い仕事への従事者。あるいは、スポーツなど余暇における活発な運動習慣をもっている場合"
    ]
)

# 保存先のCSVファイル名
CSV_PATH = "userdata.csv"

if st.button("送信する"):
    # 計算
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    if sex == "男性（出生時）":
        bmr = (0.0481 * weight + 0.0234 * height + 0.0138 * age - 0.4235) * 1000 / 4.186
    else:
        bmr = (0.0481 * weight + 0.0234 * height + 0.0138 * age - 0.9708) * 1000 / 4.186

    if "低い" in activity:
        factor = 1.5
    elif "ふつう" in activity:
        factor = 1.75
    else:
        factor = 2.0

    need_kcal = bmr * factor

    # データまとめ
    now = datetime.datetime.now().isoformat()
    data = {
        "timestamp": now,
        "id": user_id,
        "age": age,
        "sex": sex,
        "height_cm": height,
        "weight_kg": weight,
        "body_fat": body_fat,
        "bmi": bmi,
        "bmr": bmr,
        "activity_level": activity,
        "activity_factor": factor,
        "need_kcal": need_kcal
    }

    df = pd.DataFrame([data])

    # ヘッダー付きで初回保存、それ以降は追記
    write_header = not os.path.exists(CSV_PATH)
    df.to_csv(CSV_PATH, mode="a", header=write_header, index=False)

    st.success("データが保存されました！次のステップに進んでください。")

