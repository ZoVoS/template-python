import os
from flask import Flask, send_from_directory, render_template, redirect, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape')
def scrape():
    # Your scraping logic here
    url = "https://www.bmh-ltd.com/vehicle-parts/mini-parts/underframe/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'tablepress-2'})
    rows = table.find_all('tr')
    header = [th.text for th in rows[0].find_all('th')]
    data = [[td.text for td in row.find_all('td')] for row in rows[1:]]
    df = pd.DataFrame(data, columns=header)
    json_output = df.to_json(orient='split')
    
    return jsonify(json_output)

@app.route('/<path:path>')
def all_routes(path):
    return redirect('/')

if __name__ == "__main__":
    app.run(port=port)
