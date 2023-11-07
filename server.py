import os
from flask import Flask, send_from_directory, render_template, redirect, jsonify, request
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

def generate_regex_pattern(phrase):
    words = phrase.split()
    word_boundaries = ['\\b' + word + '\\b' for word in words]
    negative_lookahead = r'(?i)(?!' + '\\s'.join(word_boundaries) + ')'
    
    permutations = []
    for i in range(len(words)):
        # Create a pattern with one word replaced by [^ ]+ (match any non-space characters)
        permutation = words[:i] + [r'[^ ]+'] + words[i + 1:]
        # Add word boundaries to the entire permutation
        permutation_with_boundaries = '\\b' + '\\s'.join(permutation) + '\\b'
        permutations.append(permutation_with_boundaries)

    # Combine the permutations with alternation and non-capturing groups
    regex_pattern = negative_lookahead + '(?:' + '|'.join(permutations) + ')'
    return regex_pattern

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

@app.route('/tim')
def regex_generator():
    # Get the phrase from the query parameter named 'text'
    phrase = request.args.get('text')
    if phrase:
        regex_output = generate_regex_pattern(phrase)
        return jsonify({'regex': regex_output})
    else:
        # If no phrase is provided, return an error or instructions
        return "Please provide a phrase using the 'text' query parameter. Example: /tim?text=this product is green"

# ... Rest of your Flask app ...

@app.route('/<path:path>')
def all_routes(path):
    return redirect('/')

if __name__ == "__main__":
    app.run(port=port)
