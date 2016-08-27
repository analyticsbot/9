# import the Flask class from the flask module and other required modules
from flask import Flask, render_template, request, make_response, session, url_for, jsonify
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys, sqlite3
reload(sys)
sys.setdefaultencoding('utf-8')

# create the application object
app = Flask(__name__)
app.secret_key = "/\xfa-\x84\xfeW\xc3\xda\x11%/\x0c\xa0\xbaY\xa3\x89\x93$\xf5\x92\x9eW}"
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.WTF_CSRF_SECRET_KEY  = "spinningbot"
app.CSRF_ENABLED = True
app.debug = True


@app.route('/', methods=['GET'])
def home():
    """ flask view for the home page"""
    return render_template('index_2.html')

@app.route('/go', methods=['POST'])
def scrape(numrows=10):
    """ flask view for the search page"""
    if request.method == "POST":
        errors = {}
        url = request.form['url']
        
        session['url'] = url       
        
        if (url != ''):
            #print searchterm
            errors = {}
        else:
            errors =  {'error': 'url required'}
            

        return render_template('index.html', url = url, message = "Please Wait...")

if __name__ == '__main__':
        app.run(debug=True)
