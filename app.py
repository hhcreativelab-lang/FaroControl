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
            margin-top: 24px;
            margin-bottom: 12px;
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

        @media (max-width: 600px) {
            .main .block-container {
                padding-left: 18px;
                padding-right: 18px;
                padding-top: 20px;
            }

            .hh-title {
                font-size: 30px;
            }

            .hh-subtitle {
                font-size: 16px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)

WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")

if not WEBHOOK_URL:
    st.error("WEBHOOK_URL не найден в Streamlit Secrets.")
    st.stop()

# -----------------------------
# Новые операции по направлениям
# -----------------------------
OPERATIONS = {
    "Прямострочка": {
        "Органайзер дно — заготовка — 5 ₽": {
            "id": "OP001",
            "needs_dogs": True,
            "hint": "Укажите количество изделий и количество собачек. Собачки здесь учитываются, но отдельно не оплачиваются.",
        },
        "Органайзер бок — заготовка — 4 ₽": {
            "id": "OP002",
            "needs_dogs": False,
            "hint": "Укажите количество изделий.",
        },
        "Картон — вставка — 2 ₽": {
            "id": "OP005",
            "needs_dogs": False,
            "hint": "Укажите количество вставленного картона.",
        },
        "Кофр — заготовка — 18 ₽ + собачка 1 ₽": {
            "id": "OP006",
            "needs_dogs": True,
            "hint": "Укажите количество изделий и количество собачек. Собачки оплачиваются отдельно по 1 ₽.",
        },
    },
    "Окантовщики": {
        "Органайзер дно — окантовка — 7 ₽": {
            "id": "OP003",
            "needs_dogs": False,
            "hint": "Укажите количество изделий.",
        },
        "Органайзер верх — окантовка — 6 ₽": {
            "id": "OP004",
            "needs_dogs": False,
            "hint": "Укажите количество изделий.",
        },
        "Кофр — окантовка — 24 ₽": {
            "id": "OP007",
            "needs_dogs": False,
            "hint": "Укажите количество изделий.",
        },
    },
}


def format_money(value):
    try:
        amount = int(float(value))
    except Exception:
        amount = 0
    return f"{amount:,}".replace(",", " ") + " ₽"


def normalize_direction(value):
    return str(value or "").strip()


def get_token_from_url():
    try:
        value = st.query_params.get("token", "")
    except Exception:
        value = st.experimental_get_query_params().get("token", [""])[0]

    if isinstance(value, list):
        value = value[0] if value else ""

    return str(value).strip()


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
token = get_token_from_url()

if not token:
    st.error("Личная ссылка не найдена.")
    st.info("Откройте форму по личной ссылке сотрудника.")
    st.stop()

# -----------------------------
# Получаем профиль сотрудника по token
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

worker_name = str(profile_data.get("worker_name", "")).strip()
worker_direction = normalize_direction(profile_data.get("direction", ""))

if not worker_direction:
    st.error("У сотрудника не указано направление. Обратитесь к ответственному.")
    st.stop()

if worker_direction not in OPERATIONS:
    st.error(f"Для направления '{worker_direction}' не настроены операции.")
    st.stop()

# -----------------------------
# Приветствие
# -----------------------------
if worker_name:
    st.markdown(
        f"""
        <div class="hh-greeting">
            <b>Здравствуйте, {worker_name}!</b><br>
            Это ваша личная форма сдачи работы.<br>
            Направление: <b>{worker_direction}</b>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <div class="hh-greeting">
            <b>Здравствуйте!</b><br>
            Это ваша личная форма сдачи работы.<br>
            Направление: <b>{worker_direction}</b>
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
        Выберите операцию, укажите количество изделий и при необходимости количество собачек.
    </div>
    """,
    unsafe_allow_html=True
)

available_operations = OPERATIONS[worker_direction]
operation_labels = list(available_operations.keys())

with st.form("submit_work_form", clear_on_submit=True):
    operation_label = st.selectbox("Операция", operation_labels)
    operation_data = available_operations[operation_label]

    st.caption(operation_data.get("hint", ""))

    quantity = st.number_input(
        "Количество изделий",
        min_value=1,
        step=1
    )

    dogs_quantity = 0

    if operation_data.get("needs_dogs"):
        dogs_quantity = st.number_input(
            "Количество собачек",
            min_value=0,
            step=1
        )

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
        "operation_id": operation_data["id"],
        "quantity": int(quantity),
        "dogs_quantity": int(dogs_quantity),
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
                today_date = salary_data.get("today_date", "")
                week_start = salary_data.get("week_start", "")
                week_end = salary_data.get("week_end", "")

                salary_name = worker_name or salary_data.get("worker_name", "сотрудника")

                salary_text = (
                    f"**Начисления для {salary_name}**\n\n"
                    f"Сегодня: **{format_money(today_amount)}**\n\n"
                    f"Текущая неделя: **{format_money(week_amount)}**\n\n"
                    f"Текущий месяц: **{format_money(month_amount)}**\n\n"
                    f"Всего записей: **{records_count}**\n\n"
                    f"Всего по всем найденным записям: **{format_money(total_amount)}**"
                )

                if today_date or (week_start and week_end):
                    salary_text += "\n\n---\n"
                    if today_date:
                        salary_text += f"Дата проверки: {today_date}\n\n"
                    if week_start and week_end:
                        salary_text += f"Период недели: {week_start} — {week_end}"

                st.success(salary_text)
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
