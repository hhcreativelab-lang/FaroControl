import os
import streamlit as st
import requests

st.set_page_config(
    page_title="FaroControl",
    page_icon="🧵",
    layout="centered"
)

# -----------------------------
# Стили страницы
# -----------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #fbf9ff 0%, #ffffff 45%, #fafafa 100%);
        }

        .main .block-container {
            max-width: 760px;
            padding-top: 32px;
            padding-bottom: 32px;
        }

        .hh-header {
            text-align: center;
            margin-bottom: 22px;
        }

        .hh-title {
            font-size: 34px;
            font-weight: 800;
            color: #211833;
            margin-top: 8px;
            margin-bottom: 4px;
            letter-spacing: 0.3px;
        }

        .hh-subtitle {
            font-size: 18px;
            color: #5f5870;
            margin-bottom: 20px;
        }

        .hh-card {
            background: #ffffff;
            border: 1px solid #ece7f6;
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 10px 28px rgba(51, 32, 95, 0.08);
            margin-bottom: 18px;
        }

        .hh-greeting {
            background: linear-gradient(135deg, #fff4cf 0%, #fff9e8 100%);
            color: #5c4300;
            padding: 16px 18px;
            border-radius: 14px;
            border: 1px solid #f3d987;
            margin-bottom: 18px;
            font-size: 16px;
            line-height: 1.5;
        }

        .hh-info {
            background: #f1ecff;
            color: #38215f;
            padding: 14px 16px;
            border-radius: 14px;
            border: 1px solid #dfd3ff;
            margin-bottom: 18px;
            font-size: 15px;
            line-height: 1.5;
        }

        .hh-footer {
            text-align: center;
            color: #8a8496;
            font-size: 13px;
            margin-top: 28px;
            padding-top: 18px;
            border-top: 1px solid #eee9f7;
        }

        div.stButton > button:first-child,
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #6f18ff 0%, #7b2cff 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.65rem 1.1rem;
            font-weight: 700;
            box-shadow: 0 8px 18px rgba(111, 24, 255, 0.22);
        }

        div.stButton > button:first-child:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #5c0ee0 0%, #6f18ff 100%);
            color: white;
            border: none;
        }

        div[data-testid="stSelectbox"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stTextArea"] label {
            color: #211833;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True
)

WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")

if not WEBHOOK_URL:
    st.error("WEBHOOK_URL не найден в Streamlit Secrets.")
    st.stop()

OPERATIONS = {
    "Заготовка органайзеров — дно — 10 ₽": "OP001",
    "Заготовка органайзеров — бок — 8 ₽": "OP002",
    "Окантовка органайзеров — дно — 7 ₽": "OP003",
    "Окантовка органайзеров — верх — 6 ₽": "OP004",
    "Заготовка кофр — 12 ₽": "OP005",
    "Окантовка кофр — 24 ₽": "OP006",
    "Упаковка кофр — 3 ₽": "OP007",
    "Упаковка органайзеров — 3 ₽": "OP008",
}

# -----------------------------
# Верх страницы / логотип
# -----------------------------
st.markdown('<div class="hh-header">', unsafe_allow_html=True)

logo_path = "hhfaro_logo_purple.png"

if os.path.exists(logo_path):
    st.image(logo_path, width=280)

st.markdown(
    """
    <div class="hh-title">FaroControl</div>
    <div class="hh-subtitle">Учёт выработки</div>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Получаем token из ссылки
# -----------------------------
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

# -----------------------------
# Получаем имя сотрудника по token
# -----------------------------
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

# -----------------------------
# Приветствие
# -----------------------------
if worker_name:
    st.markdown(
        f"""
        <div class="hh-greeting">
            <b>Здравствуйте, {worker_name}!</b><br>
            Это ваша личная форма сдачи работы.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class="hh-greeting">
            <b>Здравствуйте!</b><br>
            Это ваша личная форма сдачи работы.
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div class="hh-info">
        Выберите операцию, укажите количество и при необходимости добавьте короткий комментарий.
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Форма сдачи работы
# -----------------------------
st.markdown('<div class="hh-card">', unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Отправка данных
# -----------------------------
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

st.markdown(
    """
    <div class="hh-footer">
        HH Faro · FaroControl · Web-форма учёта выработки
    </div>
    """,
    unsafe_allow_html=True
)
