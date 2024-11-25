import asyncio
import os
import aio_pika
from aiohttp import ClientSession
from aio_pika import connect_robust
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
import sys

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
QUEUE_NAME = os.getenv("QUEUE_NAME")


async def fetch_links(url, session):
    """
    Извлекает внутренние абсолютные ссылки из HTML страницы.
    """
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            raw_link = a["href"]
            abs_link = urljoin(url, raw_link)

            # Пропускаем некорректные ссылки
            if not abs_link.startswith(("http://", "https://")):
                continue

            # Фильтруем только внутренние ссылки
            if urlparse(abs_link).netloc == urlparse(url).netloc:
                links.append((a.get_text(strip=True), abs_link))
        return links


async def publish_links(url):
    """
    Ищет ссылки на странице и публикует их в очередь RabbitMQ.
    """
    connection = await connect_robust(
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
    )
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_NAME, durable=True)

        async with ClientSession() as session:
            links = await fetch_links(url, session)
            for name, link in links:
                print(f"Found: {name} -> {link}")
                await channel.default_exchange.publish(
                    aio_pika.Message(body=link.encode()),
                    routing_key=QUEUE_NAME,
                )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python initial_loader.py <URL>")
        exit(1)

    start_url = sys.argv[1]
    asyncio.run(publish_links(start_url))
