import json
import asyncio
import aio_pika
import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

async def send_welcome_email(payload):
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = payload['email']
    message["Subject"] = "Добро пожаловать в систему инвентаризации!"
    
    content = (
        f"Привет, {payload['displayName']}!\n\n"
        f"Вы успешно зарегистрированы в нашей системе.\n"
        f"Ваш уникальный ID: {payload['userId']}\n\n"
        f"С уважением, команда ddos_dimas."
    )
    message.set_content(content)

    await aiosmtplib.send(
        message, 
        hostname=settings.SMTP_HOST, 
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER, 
        password=settings.SMTP_PASS, 
        use_tls=True,
        timeout=10 
    )

async def start_worker():
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    
    await channel.declare_exchange(
        'app.events', 
        aio_pika.ExchangeType.DIRECT, 
        durable=True
    )

    await channel.declare_exchange('app.dlx', aio_pika.ExchangeType.DIRECT, durable=True)
    await channel.declare_queue('wp.auth.user.registered.dlq', durable=True)

    queue = await channel.declare_queue(
        'wp.auth.user.registered', 
        durable=True,
        arguments={
            "x-dead-letter-exchange": "app.dlx",
            "x-dead-letter-routing-key": "user.registered"
        }
    )
    
    await queue.bind('app.events', routing_key='user.registered')

    print("[*] Воркер запущен и ожидает сообщений...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(requeue=True): 
                data = json.loads(message.body)
                payload = data['payload']
                email = payload['email']
                
                print(f"[*] Получено событие. Отправка Email для: {email}")
                try:
                    await send_welcome_email(payload)
                    print(f"[+] Письмо успешно отправлено на {email}")
                except Exception as e:
                    print(f"[!] Ошибка при отправке письма для {email}: {e}")
                    raise