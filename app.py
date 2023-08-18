from threading import Thread
from flask import Flask, jsonify
from flask import render_template
import os
from flask import request
from flask_socketio import SocketIO
from flask_socketio import start_background_task

from services.sitemap_scraper import get_urls_from_data_folder

app = Flask(__name__, static_folder='savedDocuments')
socketio = SocketIO(app)


@app.route('/')
def list_files():
    files = os.listdir("savedDocuments")
    return render_template('list_files.html', files=files)


@app.route('/start_sitemap_scrap', methods=['POST'])
def sitemap_scrap():
    # Extract data from the POST request
    data = request.get_json()
    urls = data.get("urls", [])
    industryName = data.get("industryName", "")

    def run_async_func():
        import asyncio
        asyncio.run(get_urls_from_data_folder(urls, industryName))

    start_background_task(run_async_func)


    return jsonify({"message": "Processing started, check back later for results."})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
