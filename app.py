from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import boto3
import requests
import os
import json
import re, uuid

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)
app.config['SECRET_KEY'] = "FOO"

Cache = {}

@app.before_request
def verify_session_id():
    allowed_routes = ['index']
    if request.endpoint not in allowed_routes  and 'session_id' not in session:
        return redirect(url_for('index'))

@app.route('/', methods=['POST', 'GET'])
def index():
    if 'session_id' not in session:
        session['session_id'] = uuid.uuid1()
    return render_template('index.html')

@app.route('/scrape', methods=[ 'POST', 'GET'])
def scrape():
    if request.method == 'POST':
        url = request.form.get('urlName')

        resp = requests.get(url)
        anchor_pattern = re.compile(r'<a.*?href.*?>.*?</a>')
        anchors = anchor_pattern.findall(resp.text)
        href_pattern = r'href=[\'"]([^\'" >]+)'
        hrefs = []
        for anchor in anchors:
            match_obj = re.search(href_pattern, anchor)
            hrefs.append(match_obj.group(1))
        file_name = '_'.join(url.split("//")[1].split('/'))
        Cache[session['session_id']] = dict(
            file_name = file_name,
            data = hrefs
        )
        return jsonify(hrefs)
    else:
        return render_template('index.html')
    
@app.route('/save')
def save_scrape():
    if 'session_id' in session:
        s3 = boto3.resource('s3')
        s3.Bucket(
            os.environ.get("BUCKET_NAME")
        ).put_object(
            Key=f"{session['session_id']}/{Cache[session['session_id']]['file_name']}.json",
            Body=json.dumps(Cache[session['session_id']]['data'])
        )
        return jsonify({'status': 'saved'})
    else:
        return redirect('/')

app.run(host='0.0.0.0', port=8080, debug=False)
