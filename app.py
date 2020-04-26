from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import requests
import re, uuid

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)
app.config['SECRET_KEY'] = "FOO"

@app.before_request
def verify_session_id():
    allowed_routes = ['index']
    if request.endpoint not in allowed_routes  and 'session_id' not in session:
        return redirect(url_for('index'))

@app.route('/', methods=['POST', 'GET'])
def index():
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
        return jsonify(hrefs)
    else:
        return render_template('index.html')
    
@app.route('/save')
def save_scrape():
    if 'session_id' in session:
        return jsonify({'status': 'saved'})
    else:
        return redirect('/')

app.run(host='0.0.0.0', port=8080, debug=False)
