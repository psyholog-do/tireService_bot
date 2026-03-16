### Telegram Tire Service Bot (aiogram 3)

Производственный Telegram-бот для шиномонтажа по адресу **Раиса Гареева 110**.

Функции:

- **/start меню**: прайс, запись, карта, звонок
- **Пошаговая запись** с FSM (имя → телефон → тип авто → дата → время → подтверждение)
- **Интеграция с Google Sheets** (gspread + Service Account)
- **Фильтрация занятых слотов** (каждые 20 минут, 09:00–18:40)
- **Напоминания за 1 час** до записи через APScheduler

---

### Стек

- Python 3.11+
- `aiogram` 3.x
- `gspread` + `google-auth`
- `APScheduler`
- `python-dotenv`

---

### Структура проекта

- `bot.py` – точка входа бота

- `handlers/`
  - `start.py` – команда `/start` и главное меню
  - `price.py` – показ прайса
  - `booking.py` – FSM записи на шиномонтаж
  - `location.py` – отправка геолокации сервиса

- `keyboards/`
  - `inline.py` – inline-клавиатуры (меню, тип авто, даты, слоты, подтверждение)

- `services/`
  - `google_sheets.py` – обёртка над Google Sheets (создание/чтение записей)
  - `slot_manager.py` – генерация слотов каждые 20 минут
  - `reminder_service.py` – APScheduler-напоминания за 1 час

- `database/`
  - `models.py` – модель `Booking` (вспомогательный dataclass)

- `utils/`
  - `config.py` – загрузка `.env`, константы и базовые настройки

- `.env.example` – пример конфигурации окружения
- `requirements.txt` – зависимости Python

---

### 1. Установка зависимостей

1. Клонируйте/скопируйте проект и перейдите в папку:

```bash
cd path/to/bot/project
```

2. Создайте и активируйте виртуальное окружение (рекомендуется):

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

---

### 2. Настройка Google Sheets

1. **Создайте проект в Google Cloud**
   - Откройте консоль: `https://console.cloud.google.com`
   - Создайте новый проект (например, `tire-service-bot`)

2. **Включите Google Sheets API**
   - В меню выберите **APIs & Services → Library**
   - Найдите **Google Sheets API** и включите его (**Enable**)

3. **Создайте Service Account**
   - Перейдите в **APIs & Services → Credentials**
   - Нажмите **Create credentials → Service account**
   - Укажите название (например, `tire-bot-sa`) и завершите создание

4. **Создайте ключ и скачайте `credentials.json`**
   - Откройте созданный сервисный аккаунт
   - Вкладка **Keys → Add key → Create new key**
   - Тип ключа: **JSON**
   - Скачайте файл и сохраните его как **`credentials.json`** в корень папки `project/`

5. **Создайте Google Sheet и выдайте доступ**
   - Создайте новую таблицу в Google Sheets, например **`Tire Service Bookings`**
   - Скопируйте **имя таблицы** (точно, как в интерфейсе) – оно пойдёт в `GOOGLE_SHEET_NAME`
   - Нажмите **Share** и поделитесь таблицей с e-mail сервисного аккаунта (из `credentials.json`)
   - Выдайте права **Editor**

**Структура таблицы**

При первом запуске бот автоматически создаст заголовок листа:

- `Name`
- `Phone`
- `Car Type`
- `Date` (формат `YYYY-MM-DD`)
- `Time` (формат `HH:MM`)
- `Created At`
- `Telegram ID`

Каждая запись добавляется в конец листа.

---

### 3. Настройка окружения (.env)

1. Скопируйте пример:

```bash
cp .env.example .env
```

2. Откройте `.env` и заполните:

```env
BOT_TOKEN=ваш_telegram_bot_token
ADMIN_ID=123456789          # Telegram ID администратора для уведомлений
GOOGLE_SHEET_NAME=Tire Service Bookings

# Необязательно: можно изменить номер телефона и координаты
PHONE_NUMBER=+79991234567
TELEGRAM_LOCATION_LAT=55.725995
TELEGRAM_LOCATION_LON=49.174686
```

3. **BOT_TOKEN**
   - Получите токен у `@BotFather` в Telegram

4. **ADMIN_ID**
   - Узнайте свой ID через бота `@userinfobot` или аналогичный

5. **GOOGLE_SHEET_NAME**
   - Точное имя таблицы, которую вы создали в Google Sheets

6. **Координаты**
   - По умолчанию стоят координаты улицы Раиса Гареева 110 в Казани
   - При необходимости замените на свои (широта/долгота)

---

### 4. Запуск бота локально

Из папки `project/` выполните:

```bash
venv\Scripts\activate  # если ещё не активировано
python bot.py
```

Если всё настроено корректно:

- бот запустится и начнёт long polling
- APScheduler стартует в том же процессе

Откройте Telegram, найдите своего бота и отправьте `/start`.

---

### 5. Логика бота и запись

- **/start**
  - Отправляет приветствие, режим работы и inline-меню:
    - `Прайс`
    - `Запись`
    - `📍 Как проехать`
    - `📞 Позвонить`

- **Прайс**
  - Показывает фиксированный прайс с кнопкой `Назад`

- **📍 Как проехать**
  - Отправляет геолокацию по координатам из `.env`

- **📞 Позвонить**
  - Открывает звонок на номер из `.env` (формат `tel:+7999...`)

- **Запись (FSM)**
  1. Имя (текст)
  2. Телефон (текст)
  3. Тип авто (кнопки: `Легковая`, `Кроссовер`, `Внедорожник`)
  4. Дата:
     - `Сегодня`
     - `Завтра`
     - `Выбрать дату` (inline-календарь на ближайшие 30 дней)
  5. Время:
     - Кнопки с доступными слотами каждые 20 минут с 09:00 до 18:40
     - Уже занятые слоты скрываются (фильтрация по Google Sheets)
  6. Подтверждение:
     - Показ всех данных
     - Кнопки `Подтвердить` / `Отмена`

- После подтверждения:
  - Запись сохраняется в Google Sheets
  - Пользователь получает подтверждение с датой, временем и адресом
  - Администратор (ADMIN_ID) получает уведомление о новой записи
  - APScheduler планирует напоминание за 1 час до записи

---

### 6. Напоминания (APScheduler)

- Используется `AsyncIOScheduler` из `APScheduler`
- При создании записи:
  - Высчитывается `booking_datetime = date + time`
  - Планируется задание на `(booking_datetime - 1 час)`
  - Если время напоминания уже прошло, напоминание не создаётся (защита от спама)
- Текст напоминания:

> Напоминаем!  
> Вы записаны на шиномонтаж сегодня в {time}.  
> Адрес: Раиса Гареева 110

**Важно:** задачи планируются только в памяти процесса.  
Если бот перезапускается, уже запланированные напоминания теряются.  
Для "твёрдого" продакшена можно подключить persistent job store (например, Redis или БД).

---

### 7. Деплой (общая схема)

Базовая схема деплоя на сервер (Linux/VPS):

1. Скопируйте папку `project/` на сервер
2. Установите Python 3.11+
3. Создайте виртуальное окружение и установите зависимости:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Скопируйте `.env` и `credentials.json` на сервер в папку `project/`
5. Запустите бота через **systemd** или **pm2**/**supervisor**, например:

```bash
python bot.py
```

6. Убедитесь, что процесс перезапускается при падении и автоматически стартует при перезагрузке сервера.

Для продакшена также рекомендуется:

- ограничить доступ к файлу `credentials.json`

---

### 8. Логирование и мониторинг

#### Логирование

- В `utils/logger.py` настроено базовое логирование:
  - вывод в консоль
  - ротация файла `logs/bot.log` (до 5 МБ, 3 бэкапа)
- Логгер инициализируется в `bot.py` через `setup_logging()` при старте.
- В `handlers/booking.py` пишутся ключевые события:
  - начало записи
  - ввод имени
  - отмена записи
  - успешное подтверждение (c датой/временем и данными клиента)

Вы можете расширить логирование, добавив свои `logger.info()` / `logger.error()` в нужные места.

#### Мониторинг процесса

Минимальный вариант мониторинга на Linux/VPS:

- Запустить бота как systemd‑unit с авто‑рестартом:

```ini
[Unit]
Description=Telegram Tire Service Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/venv/bin/python bot.py
Restart=always
RestartSec=5
User=www-data

[Install]
WantedBy=multi-user.target
```

- Включить юнит:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-tire-bot.service
sudo systemctl start telegram-tire-bot.service
```

Дальше можно:

- смотреть логи через `journalctl -u telegram-tire-bot.service` и файл `logs/bot.log`
- повесить внешний мониторинг (Zabbix, Prometheus, UptimeRobot и т.п.) на доступность сервера/процесса.

"# tire-service-bot" 
