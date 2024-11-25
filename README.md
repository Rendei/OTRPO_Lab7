# RabbitMQ Web Crawler

Проект состоит из двух консольных приложений для асинхронного поиска внутренних ссылок на веб-страницах с использованием RabbitMQ для очередей сообщений.

1. **`initial_loader.py`:** 
   Загружает стартовую страницу, извлекает внутренние ссылки и публикует их в очередь RabbitMQ.
2. **`consumer_producer.py`:**
   Работает как постоянный консумер и продюсер. Читает ссылки из очереди, обрабатывает их и добавляет новые внутренние ссылки обратно в очередь.

---

## Основные возможности

- Поддержка как абсолютных, так и относительных ссылок (преобразование в абсолютные).
- Обрабатывает только внутренние ссылки (принадлежащие тому же домену, что и исходная страница).
- Асинхронная обработка с использованием `aiohttp` и `aio_pika`.
- Логирование прогресса (обрабатываемая страница, найденные ссылки).
- Завершение работы при таймауте очереди.

---

## Требования

- **Python** 3.8 или выше
- **RabbitMQ** (запущен в контейнере Docker или локально)
- Зависимости (устанавливаются через `pip`):
  ```bash
  pip install -r requirements.txt
  ```

---

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/Rendei/OTRPO_Lab7
   cd OTRPO_Lab7
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте `RabbitMQ`. Пример `docker-compose.yml` для RabbitMQ:
   ```yaml
   version: "3.2"
   services:
     rabbitmq:
       image: rabbitmq:3.13.7-management
       ports:
         - "5672:5672"
         - "15672:15672"
   ```

   Запустите RabbitMQ:
   ```bash
   docker-compose up -d
   ```

4. Создайте файл `.env` с параметрами подключения к RabbitMQ:
   ```env
   RABBITMQ_HOST=127.0.0.1
   RABBITMQ_PORT=5672
   RABBITMQ_USER=guest
   RABBITMQ_PASS=guest
   QUEUE_NAME=links_queue
   ```

---

## Использование

### 1. Запуск начального загрузчика

Передайте URL сайта для начала обработки:

```bash
python initial_loader.py <URL>
```

Пример:

```bash
python initial_loader.py https://example.com
```

Этот скрипт добавит все внутренние ссылки стартовой страницы в очередь RabbitMQ.

### 2. Запуск консумера/продюсера

Запустите `consumer_producer.py`, чтобы начать обработку ссылок из очереди:

```bash
python consumer_producer.py
```

Консумер извлекает ссылки из очереди, находит внутренние ссылки на этих страницах и публикует их обратно в очередь.

---

## Логирование

Во время работы приложения выводятся следующие данные:
- **`initial_loader.py`:** Все найденные ссылки с текстом.
- **`consumer_producer.py`:** Обрабатываемые ссылки и найденные ссылки на каждой странице.

Пример лога:

```text
Found: Example -> https://example.com/about
Found: Contact -> https://example.com/contact
Processing: https://example.com/about
Found: Team -> https://example.com/team
```

---

## Таймаут

Если очередь пуста в течение 10 секунд, консумер автоматически завершает работу с сообщением:

```text
Queue is empty, stopping consumer.
```

---

## Возможные ошибки

- **`aiormq.exceptions.AMQPConnectionError`:**
  Убедитесь, что RabbitMQ запущен, и параметры подключения в `.env` корректны.

- **`aiohttp.client_exceptions.ClientError`:**
  Убедитесь, что URL страницы доступен и корректен.

