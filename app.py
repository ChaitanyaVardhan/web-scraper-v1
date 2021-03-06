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

@app.route('/test', methods=['POST', 'GET'])
def test():
    if 'session_id' not in session:
        session['session_id'] = uuid.uuid1()
    return render_template('test.html')

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
            hrefs.append(
                dict(
                    url=match_obj.group(1)
                )
            )
        file_name = '_'.join(url.split("//")[1].split('/'))
        Cache[session['session_id']] = dict(
            file_name = file_name,
            data = hrefs
        )
        return render_template("scrapes.html", hrefs=hrefs)
    else:
        return render_template('index.html')
    
@app.route('/save', methods = ["POST"])
def save_scrape():
    if request.method == "POST":
        if 'session_id' in session:
            email_id = request.form.get('emailId')
            dir_name = email_id
            s3 = boto3.resource('s3')
            BUCKET_NAME = os.environ.get("BUCKET_NAME")
            s3.Bucket(
                BUCKET_NAME
            ).put_object(
                Key=f"{dir_name}/{Cache[session['session_id']]['file_name']}.json",
                Body=json.dumps(Cache[session['session_id']]['data'])
            )
            return jsonify({'status': 'saved'})
    else:
        return redirect('/')

app.run(host='0.0.0.0', port=8080, debug=False)
