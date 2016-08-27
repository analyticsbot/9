import requests
import json

from flask import Flask
from flask import request, render_template
from logging import FileHandler
import logging

app = Flask(__name__)
import logging
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler('python.log', maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

@app.route('/')
def home():
    return 'active'

    
@app.route('/add_task')
def add_task():
    print 'add_task'
    if request.method == 'GET':
        spider = request.args.get('spider', 'amazon')
        search_term = request.args.get('searchterms_str', '')
        asin = request.args.get('asin', '')
        page = request.args.get('page', '')

        url = 'http://52.8.237.119/schedule.json'

        if not search_term:
            return "You should provide search term"

        params = {'project': 'spiders',
                  'spider': spider,
                  'searchterms_str': search_term}
        if page:
            params['page'] = page
        if asin:
            params['asin'] = asin

        res = requests.post(url, params=params)

        if res.status_code == 200:
            data = json.loads(res.content)
            if data['status'] == 'ok':
                task_id = data['jobid']

                link = 'http://52.8.237.119/items/spiders/' + spider + '/' \
                       + task_id + '.jl'
                return render_template('main.html', link=link)
            else:
                return data['message']
        else:
            return res.content

if __name__ == "__main__":
    app.debug = True
    logging.basicConfig(filename='debug.log',level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    app.run(host='0.0.0.0')

