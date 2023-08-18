from threading import Thread
from flask import Flask, jsonify
from flask import render_template
import os
from flask import request
from services.sitemap_scraper import get_urls_from_data_folder

app = Flask(__name__, static_folder='savedDocuments')


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

    # Start the background task with the provided data
    thread = Thread(target=get_urls_from_data_folder, args=(urls, industryName))
    thread.start()

    return jsonify({"message": "Processing started, check back later for results."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
