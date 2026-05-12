import streamlit as st
import requests

st.set_page_config(
    page_title="FaroControl",
    page_icon="🧵",
    layout="centered"
)

# Пока используем TEST webhook.
# Позже заменим на Production URL.
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

st.info("Введите код сотрудника, PIN, выберите операцию и укажите количество.")

with st.form("submit_work_form"):
    worker_id = st.text_input("Код сотрудника", placeholder="Например: W001")
    pin = st.text_input("PIN", placeholder="Например: 4821", type="password")
    operation_label = st.selectbox("Операция", list(OPERATIONS.keys()))
    quantity = st.number_input("Количество", min_value=1, step=1)

    submitted = st.form_submit_button("Сдать работу")

if submitted:
    payload = {
        "worker_id": worker_id.strip().upper(),
        "pin": pin.strip(),
        "operation_id": OPERATIONS[operation_label],
        "quantity": int(quantity),
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
