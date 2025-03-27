import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="健康体型学習 入力フォーム", layout="centered")
st.title("健康体型学習 入力フォーム")

user_id = st.text_input("指定のIDを入力してください。")
age = st.number_input("年齢（18〜64歳）", min_value=18, max_value=64)
sex = st.selectbox(
    "性別（※計算式の関係上、生まれ持った性別を選択してください。）",
    ["男性（出生時）", "女性（出生時）"]
)
height = st.number_input("身長（cm、小数第1位まで。）", min_value=100.0, max_value=250.0, step=0.1, format="%.1f")
weight = st.number_input("体重（kg、小数第1位まで。）", min_value=30.0, max_value=200.0, step=0.1, format="%.1f")
body_fat = st.number_input("体脂肪率（%、小数第1位まで。）（わからない場合は空欄にしてください。）", min_value=0.0, max_value=60.0, step=0.1, format="%.1f")
activity = st.selectbox(
    "あなたの日常での運動レベルを選んでください",
    [
        "低い：生活の大部分が座位で、静的な活動が中心の場合",
        "ふつう：座位中心の仕事だが、職場内での移動や立位での作業・接客等、あるいは通勤・買物・家事、軽いスポーツ等のいずれかを含む場合",
        "高い：移動や立位の多い仕事への従事者。あるいは、スポーツなど余暇における活発な運動習慣をもっている場合"
    ]
)

if st.button("送信する"):
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    if sex == "男性（出生時）":
        bmr = (0.0481 * weight + 0.0234 * height + 0.0138 * age - 0.4235) * 1000 / 4.186
    else:
        bmr = (0.0481 * weight + 0.0234 * height + 0.0138 * age - 0.9708) * 1000 / 4.186

    factor = 1.5 if "低い" in activity else 1.75 if "ふつう" in activity else 2.0
    need_kcal = bmr * factor
    now = datetime.datetime.now().isoformat()

    columns = [
        "timestamp", "id", "age", "sex", "height_cm", "weight_kg", "body_fat",
        "bmi", "bmr", "activity_level", "activity_factor", "need_kcal"
    ]

    user_data = {
        "timestamp": now,
        "id": user_id,
        "age": age,
        "sex": sex,
        "height_cm": f"{height:.1f}",
        "weight_kg": f"{weight:.1f}",
        "body_fat": f"{body_fat:.1f}",
        "bmi": round(bmi, 2),
        "bmr": round(bmr, 2),
        "activity_level": activity,
        "activity_factor": factor,
        "need_kcal": round(need_kcal, 2)
    }

    df = pd.DataFrame([[user_data[c] for c in columns]], columns=columns)

    filename = f"userdata_{user_id}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')

    st.success("データが作成されました。以下のボタンを押してください。")
    st.download_button(
        label="CSVをダウンロード",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name=filename,
        mime='text/csv'
    )

    st.markdown("➡️ 入力が完了したら、画面左上の **「アンケート」ページ** に進んでください。")
