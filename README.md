# Каталог

Небольшой магазин: каталог на Next.js, API на FastAPI, товары из Telegram-бота, картинки в MinIO, корзина и заказ в Postgres. Оплаты нет.

## Запуск

Нужен Docker.

```bash
copy .env.example .env
```

В `.env` вписать `BOT_TOKEN` и свой `ADMIN_IDS` (id можно узнать командой `/id` у бота).

```bash
docker compose up --build
```

Сайт: http://localhost

Картинки отдаёт MinIO: http://localhost:9000  
Консоль MinIO: http://localhost:9001 (логин и пароль из `.env`)

Образ `minio/minio` с Docker Hub уже сняли, поэтому в compose стоит `cgr.dev/chainguard/minio`. Это тот же сервер MinIO. Бакет и публичное чтение картинок API создаёт само при старте.

Без токена бот не стартует, каталог в браузере всё равно открывается. Товар тогда можно создать запросом к API из контейнера, заголовок `X-Internal-Token`.

## Бот

Обычное сообщение и `/start`: «У меня есть товар» и кнопка «Открыть каталог». Кнопка открывает этот же сайт как Telegram Mini App.

Админ нажимает «Создать товар» и присылает одно сообщение: фото, название в подписи. Фото уходит в MinIO, запись — в Postgres.

Кнопка Mini App в Telegram работает только с https. Локально сайт открывается в браузере. Для проверки внутри Telegram нужен туннель (ngrok или аналог) на 80 порт, его адрес пишется в `WEBAPP_URL`.

## Несколько инстансов

В памяти процесса ничего нет: корзина в Postgres, сессия — cookie с id, файлы только в MinIO, у бота нет FSM.

API и фронт можно поднять в двух копиях, наружу смотрит только nginx:

```bash
docker compose up --build -d --scale api=2 --scale frontend=2
```

Бот в режиме `polling` должен быть один: Telegram не отдаёт обновления двум процессам. Для двух реплик бота: `BOT_MODE=webhook`, `WEBHOOK_BASE` — публичный https, nginx уже проксирует `/webhook`.
