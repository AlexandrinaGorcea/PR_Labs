from flask import Flask, request, jsonify
import threading
from ftplib import FTP
import os
import time
import requests
import json
import pika

app = Flask(__name__)


# RabbitMQ consumer setup
def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
    channel = connection.channel()
    channel.queue_declare(queue='products')

    def callback(ch, method, properties, body):
        product_data = json.loads(body)
        print(product_data)
        if isinstance(product_data, list):
            for product in product_data:
                response = requests.post('http://localhost:5000/products', json=product)
                print(f"Sent product to Flask API: {response.status_code}, {response.text}")

    channel.basic_consume(queue='products', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


# Start consumer in a separate thread
consumer_thread = threading.Thread(target=start_consumer)
consumer_thread.daemon = True
consumer_thread.start()


# # FTP file fetcher
# def fetch_ftp_file():
#     while True:
#         ftp = FTP('ftp')
#         ftp.login(user='user', passwd='password')
#         ftp.cwd('/home/user')
#         filename = 'data.json'
#         local_filename = os.path.join('./', filename)
#         with open(local_filename, 'wb') as local_file:
#             ftp.retrbinary(f'RETR {filename}', local_file.write)
#         ftp.quit()
#
#         # Send file to Flask API as multipart request
#         with open(local_filename, 'rb') as f:
#             files = {'file': (filename, f, 'application/json')}
#             response = requests.post('http://flask-api:5000/upload', files=files)
#             print(f"Uploaded product data to Flask API: {response.status_code}")
#
#         time.sleep(30)
#
#
# # Start FTP file fetcher in a separate thread
# ftp_thread = threading.Thread(target=fetch_ftp_file)
# ftp_thread.daemon = True
# ftp_thread.start()


@app.route('/')
def index():
    return "Manager/Intermediary Server"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)