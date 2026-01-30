import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pika
import json
import time
from pika.exceptions import AMQPConnectionError, StreamLostError
from dotenv import load_dotenv



class RabbitMQManager:
    def __init__(self, exchange='articles_exchange'):
        load_dotenv()
        self.rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        self.exchange = exchange
        self.connection = None
        self.channel = None
        self.queues = {
            "articles_collect": "articles_collect_queue",
        }
        self.max_retries = 5
        self.retry_delay = 10

    def connect(self):
        retries = self.max_retries
        for attempt in range(retries):
            try:
                parameters = pika.URLParameters(self.rabbitmq_url)
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                return
            except (AMQPConnectionError, StreamLostError, ConnectionAbortedError) as e:
                if attempt < retries - 1:
                    time.sleep(self.retry_delay)
        raise ConnectionError("Could not connect to RabbitMQ after multiple attempts.")

    def setup(self):
        if not self.channel:
            self.connect()
        
        if not self.channel:
            raise ConnectionError("Unable to establish RabbitMQ channel")

        try:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')

            for routing_key, queue_name in self.queues.items():
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=routing_key)
        except Exception as e:
            self.connect()
            self.setup()

    def publish(self, article):
        max_publish_retries = 3
        for attempt in range(max_publish_retries):
            try:
                if not self.channel or not self.connection or self.connection.is_closed:
                    self.connect()
                    self.setup()
                
                if not self.channel:
                    continue
                
                self.channel.basic_publish(
                    exchange=self.exchange,
                    routing_key="articles_collect",
                    body=json.dumps(article),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                    )
                )
                return
            except (AMQPConnectionError, StreamLostError, ConnectionAbortedError) as e:
                if attempt < max_publish_retries - 1:
                    try:
                        self.close()
                    except:
                        pass
                    time.sleep(self.retry_delay / 2)
                    self.connect()
                    self.setup()

    def close(self):
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception as e:
                pass
