from flask import Flask, request, render_template, jsonify
import requests
import re

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=[ 'POST'])
def scrape():
    url = request.form.get('urlName')

    resp = requests.get(url)
    anchor_pattern = re.compile(r'<a.*?href.*?>.*?</a>')
    anchors = anchor_pattern.findall(resp.text)
    href_pattern = r'href=[\'"]([^\'" >]+)'
    hrefs = []
    for anchor in anchors:
        match_obj = re.search(href_pattern, anchor)
        hrefs.append(match_obj.group(1))

    return jsonify(hrefs)
    
                     
app.run(host='0.0.0.0', port=8080, debug=False)
