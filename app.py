import streamlit as st
import requests

st.set_page_config(
    page_title="FaroControl",
    page_icon="🧵",
    layout="centered"
)

WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

OPERATIONS = {
    "OP001 — Заготовка органайзеров / дно — 10 ₽": "OP001",
    "OP002 — Заготовка органайзеров / бок — 8 ₽": "OP002",
    "OP003 — Окантовка органайзеров / дно — 7 ₽": "OP003",
    "OP004 — Окантовка органайзеров / верх — 6 ₽": "OP004",
    "OP005 — Заготовка кофр — 12 ₽": "OP005",
    "OP006 — Окантовка кофр — 24 ₽": "OP006",
    "OP007 — Упаковка кофр — 3 ₽": "OP007",
    "OP008 — Упаковка органайзеров — 3 ₽": "OP008",
}

st.title("FaroControl")
st.subheader("Учёт выработки")

token = st.query_params.get("token", "")

if not token:
    st.error("Личная ссылка не найдена.")
    st.info("Откройте форму по личной ссылке сотрудника.")
    st.stop()

st.info("Выберите операцию, укажите количество и при необходимости добавьте короткий комментарий.")

with st.form("submit_work_form"):
    operation_label = st.selectbox("Операция", list(OPERATIONS.keys()))
    quantity = st.number_input("Количество", min_value=1, step=1)

    comment = st.text_area(
        "Комментарий",
        placeholder="Например: осталось 2 детали, лежат на столе.",
        max_chars=200,
        height=90
    )

    submitted = st.form_submit_button("Сдать работу")

if submitted:
    payload = {
        "token": token.strip(),
        "operation_id": OPERATIONS[operation_label],
        "quantity": int(quantity),
        "comment": comment.strip(),
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=20)

        if response.status_code != 200:
            st.error(f"Ошибка сервера: {response.status_code}")
            st.text(response.text)
        else:
            data = response.json()

            if data.get("success"):
                st.success("Работа сохранена")
                st.write(data.get("message", "Сохранено"))
            else:
                st.error(data.get("message", "Ошибка отправки"))

    except requests.exceptions.RequestException as e:
        st.error("Не удалось отправить данные в систему.")
        st.text(str(e))

st.divider()
st.caption("FaroControl · Web-форма учёта выработки")
