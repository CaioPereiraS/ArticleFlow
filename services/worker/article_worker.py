import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import asyncio
import time
from shared.rabbitmq_manager import RabbitMQManager
from article_gateway import ArticleGateway
import pika.exceptions


class ArticleWorker:
    def __init__(self):

        self.rabbitmq = RabbitMQManager()
        self.queue_name = self.rabbitmq.queues["articles_collect"]
        self.gateway = ArticleGateway()

    def callback(self, ch, method, properties, body):
        try:
            article_data = json.loads(body)
            print(f"Received URGENT article: {article_data.get('data', {}).get('url', 'Unknown url')}")

            success = self.process_articles(article_data)

            # Handle message acknowledgment based on processing result
            try:
                if success:
                    # Successfully processed - acknowledge to remove from queue
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print(f"URGENT article successfully processed and acknowledged: {article_data.get('data', {}).get('url', 'Unknown url')}")
                else:
                    # Failed processing - nack without requeue to drop from queue
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    print(f"URGENT article dropped from queue after all retries: {article_data.get('data', {}).get('url', 'Unknown url')}")
            except (pika.exceptions.ConnectionClosed, pika.exceptions.StreamLostError, 
                    pika.exceptions.ChannelClosed, ConnectionResetError) as conn_err:
                # If ack/nack fails due to connection issues, log the error
                # The message will be reprocessed when the connection is restored
                print(f"Connection error during ack/nack: {conn_err}")
                print(f"Message will be redelivered: {article_data.get('data', {}).get('url', 'Unknown url')}")

        except json.JSONDecodeError:
            print("Error: Received invalid JSON message")
            # Tentar fazer o nack com tratamento de erro
            try:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except (pika.exceptions.ConnectionClosed, pika.exceptions.StreamLostError, 
                    pika.exceptions.ChannelClosed, ConnectionResetError) as conn_err:
                print(f"Connection error during nack: {conn_err}")
                
        except Exception as e:
            print("Unhandled error in callback")
            # Tentar fazer o nack com tratamento de erro
            try:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except (pika.exceptions.ConnectionClosed, pika.exceptions.StreamLostError, 
                    pika.exceptions.ChannelClosed, ConnectionResetError) as conn_err:
                print(f"Connection error during nack: {conn_err}")
                print("Message will be redelivered when connection is restored")

    def start_consuming(self):
        while True:
            try:
                print(f"Starting ArticleWorker for queue: {self.queue_name}")
                self.rabbitmq.connect()
                self.rabbitmq.setup()

                channel = self.rabbitmq.channel
                if channel is not None:
                    channel.basic_qos(prefetch_count=1)
                    channel.basic_consume(
                        queue=self.queue_name,
                        on_message_callback=self.callback
                    )

                    print(f"Now listening for messages on {self.queue_name}")
                    channel.start_consuming()
                else:
                    print("Failed to set up RabbitMQ channel: Channel is None")
                    continue  # Skip to next iteration to retry connection

            except (pika.exceptions.ConnectionClosed, pika.exceptions.StreamLostError, 
                    pika.exceptions.ChannelClosed, ConnectionResetError) as conn_err:
                print(f"Connection lost: {conn_err}")
                print("Attempting to reconnect in 10 seconds...")
                
                # Fechar conexão atual se existir
                try:
                    if self.rabbitmq.connection:
                        self.rabbitmq.close()
                except:
                    pass
                
                # Aguardar antes de tentar reconectar
                time.sleep(10)
                continue
                
            except KeyboardInterrupt:
                print("Consumer interrupted by user")
                break
                
            except Exception as e:
                print(f"Error starting consumer: {e}")
                print("Restarting consumer in 10 seconds...")
                
                # Fechar conexão atual se existir
                try:
                    if self.rabbitmq.connection:
                        self.rabbitmq.close()
                except:
                    pass
                
                time.sleep(10)
                continue
        
        # Cleanup final
        try:
            if self.rabbitmq.connection and self.rabbitmq.connection.is_open:
                self.rabbitmq.close()
                print("RabbitMQ connection closed")
        except:
            pass

    def process_articles(self, article_data) -> bool:
        try:
            # Process the article data here
            print(f"Processing article: {article_data}")
            return self.gateway.process_article(article_data)
        except Exception as e:
            print(f"Error processing article: {e}")
            return False

if __name__ == "__main__":
    consumer = ArticleWorker()
    consumer.start_consuming()