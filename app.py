import asyncio

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
    asyncio.create_task(get_urls_from_data_folder(urls, industryName))

    return jsonify({"message": "Processing started, check back later for results."})


if __name__ == "__main__":
    app.run()
# if __name__ == "__main__":
#     app.run(debug=True)