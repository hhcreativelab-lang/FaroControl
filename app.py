import streamlit as st
import requests

st.set_page_config(
    page_title="FaroControl",
    page_icon="🧵",
    layout="centered"
)

st.title("FaroControl")
st.subheader("Учёт выработки")

WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")

if not WEBHOOK_URL:
    st.error("WEBHOOK_URL не найден в Streamlit Secrets.")
    st.stop()

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

try:
    token = st.query_params.get("token", "")
except Exception:
    token = st.experimental_get_query_params().get("token", [""])[0]

if isinstance(token, list):
    token = token[0] if token else ""

token = str(token).strip()

if not token:
    st.error("Личная ссылка не найдена.")
    st.info("Откройте форму по личной ссылке сотрудника.")
    st.stop()

# Получаем имя сотрудника по token
try:
    profile_response = requests.post(
        WEBHOOK_URL,
        json={
            "action": "profile",
            "token": token,
        },
        timeout=20
    )

    if profile_response.status_code != 200:
        st.error(f"Ошибка сервера при проверке ссылки: {profile_response.status_code}")
        st.text(profile_response.text)
        st.stop()

    profile_data = profile_response.json()

except requests.exceptions.RequestException as e:
    st.error("Не удалось проверить личную ссылку.")
    st.text(str(e))
    st.stop()
except Exception as e:
    st.error("Сервер вернул некорректный ответ при проверке ссылки.")
    st.text(str(e))
    st.stop()

if not profile_data.get("success"):
    st.error(profile_data.get("message", "Личная ссылка не найдена."))
    st.stop()

worker_name = profile_data.get("worker_name", "").strip()

# Шафрановый блок приветствия
if worker_name:
    st.markdown(
        f"""
        <div style="
            background-color: #FFF3CD;
            color: #5C4300;
            padding: 16px 18px;
            border-radius: 10px;
            border: 1px solid #FFE08A;
            margin-bottom: 18px;
            font-size: 16px;
        ">
            <b>Здравствуйте, {worker_name}!</b><br>
            Это ваша личная форма сдачи работы.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div style="
            background-color: #FFF3CD;
            color: #5C4300;
            padding: 16px 18px;
            border-radius: 10px;
            border: 1px solid #FFE08A;
            margin-bottom: 18px;
            font-size: 16px;
        ">
            <b>Здравствуйте!</b><br>
            Это ваша личная форма сдачи работы.
        </div>
        """,
        unsafe_allow_html=True
    )

st.info("Выберите операцию, укажите количество и при необходимости добавьте короткий комментарий.")

with st.form("submit_work_form", clear_on_submit=True):
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
        "action": "submit",
        "token": token,
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
            try:
                data = response.json()
            except Exception:
                st.error("Сервер ответил не JSON-форматом.")
                st.text(response.text)
                st.stop()

            if data.get("success"):
                st.success("Работа сохранена")
                st.write(data.get("text", data.get("message", "Сохранено")))
            else:
                st.error(data.get("message", "Ошибка отправки"))

    except requests.exceptions.RequestException as e:
        st.error("Не удалось отправить данные в систему.")
        st.text(str(e))

st.divider()
st.caption("FaroControl · Web-форма учёта выработки")
