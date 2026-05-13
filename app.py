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
            padding-top: 28px;
            padding-bottom: 32px;
        }

        .hh-header {
            text-align: center;
            margin-bottom: 20px;
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
            margin-bottom: 18px;
        }

        .hh-by {
            text-align: center;
            font-size: 11px;
            letter-spacing: 2px;
            color: rgba(95, 88, 112, 0.45);
            font-weight: 700;
            margin-bottom: 4px;
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

        .hh-section-title {
            font-size: 20px;
            font-weight: 800;
            color: #211833;
            margin-top: 22px;
            margin-bottom: 12px;
        }

        .salary-box {
            background: linear-gradient(135deg, #effaf2 0%, #ffffff 100%);
            border: 1px solid #bde7c8;
            border-radius: 16px;
            padding: 18px;
            margin-top: 14px;
            margin-bottom: 18px;
            color: #163b22;
            box-shadow: 0 8px 20px rgba(22, 59, 34, 0.06);
        }

        .salary-title {
            font-size: 18px;
            font-weight: 800;
            margin-bottom: 12px;
        }

        .salary-row {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid rgba(22, 59, 34, 0.10);
            padding: 8px 0;
            font-size: 16px;
        }

        .salary-row:last-child {
            border-bottom: none;
        }

        .salary-value {
            font-weight: 800;
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

def format_money(value):
    try:
        amount = int(float(value))
    except Exception:
        amount = 0
    return f"{amount:,}".replace(",", " ") + " ₽"

# -----------------------------
# Верх страницы / логотип
# -----------------------------
st.markdown('<div class="hh-header">', unsafe_allow_html=True)

logo_path = "hhfaro_logo_purple.png"

if os.path.exists(logo_path):
    st.markdown('<div class="hh-by">BY HH FARO</div>', unsafe_allow_html=True)
    st.image(logo_path, width=180)

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

# -----------------------------
# Сдача работы
# -----------------------------
st.markdown('<div class="hh-section-title">Сдать работу</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hh-info">
        Выберите операцию, укажите количество и при необходимости добавьте короткий комментарий.
    </div>
    """,
    unsafe_allow_html=True
)

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

# -----------------------------
# Проверка зарплаты
# -----------------------------
st.markdown('<div class="hh-section-title">Проверить зарплату</div>', unsafe_allow_html=True)

salary_clicked = st.button("Проверить зарплату")

if salary_clicked:
    try:
        salary_response = requests.post(
            WEBHOOK_URL,
            json={
                "action": "salary",
                "token": token,
            },
            timeout=20
        )

        if salary_response.status_code != 200:
            st.error(f"Ошибка сервера при проверке зарплаты: {salary_response.status_code}")
            st.text(salary_response.text)
        else:
            try:
                salary_data = salary_response.json()
            except Exception:
                st.error("Сервер ответил не JSON-форматом.")
                st.text(salary_response.text)
                st.stop()

            if salary_data.get("success"):
                today_amount = salary_data.get("today_amount", 0)
                week_amount = salary_data.get("week_amount", 0)
                month_amount = salary_data.get("month_amount", 0)
                total_amount = salary_data.get("total_amount", 0)
                records_count = salary_data.get("records_count", 0)

                st.markdown(
                    f"""
                    <div class="salary-box">
                        <div class="salary-title">Начисления для {worker_name}</div>

                        <div class="salary-row">
                            <span>Сегодня</span>
                            <span class="salary-value">{format_money(today_amount)}</span>
                        </div>

                        <div class="salary-row">
                            <span>Текущая неделя</span>
                            <span class="salary-value">{format_money(week_amount)}</span>
                        </div>

                        <div class="salary-row">
                            <span>Текущий месяц</span>
                            <span class="salary-value">{format_money(month_amount)}</span>
                        </div>

                        <div class="salary-row">
                            <span>Всего записей</span>
                            <span class="salary-value">{records_count}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error(salary_data.get("message", "Не удалось проверить зарплату."))

    except requests.exceptions.RequestException as e:
        st.error("Не удалось получить зарплату.")
        st.text(str(e))

st.markdown(
    """
    <div class="hh-footer">
        HH Faro · FaroControl · Web-форма учёта выработки
    </div>
    """,
    unsafe_allow_html=True
)
