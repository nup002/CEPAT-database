from flask import Flask, request, jsonify, send_file, make_response
from waitress import serve
from modules.definitions import FIELDS_SEARCH, FIELDS_RESULT
from modules.tools import analyze
#from modules.analysis import analyse
from modules.db import DB
import os
import traceback
DB = DB()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='f:RYjc%={iZ3Bh[ZKG=mKz[BHUK9r',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
  
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv    
  
def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

app = create_app()
app.config["DEBUG"] = True

@app.route('/add/', methods=['POST','GET','OPTIONS'])
def postEntry():
    try:
        if request.method == "OPTIONS": # CORS preflight
            return _build_cors_prelight_response()
        args = request.args
        entry_vector = {}
        entry_data = {}
        for field in FIELDS_SEARCH:
            field_value = args.get(field)
            if field_value:
                field_value = int(field_value)
            entry_vector[field] = field_value
        for field in FIELDS_RESULT:
            entry_data[field] = args.get(field)
    
        DB.addEntry(entry_vector, entry_data)
        
        return_list = {'Search parameters':entry_vector, 'Outcome parameters':entry_data}
        return_list.headers.add("Access-Control-Allow-Origin", "*")
        return return_list
    except Exception:
        print(traceback.format_exc())
        raise InvalidUsage(traceback.format_exc())

@app.route('/get/', methods=['POST','GET','OPTIONS'])
def search():
    try:
        if request.method == "OPTIONS": # CORS preflight
            print("Sending preflight check")
            return _build_cors_prelight_response()
        args = request.args
        search_vector = {}
        for field in FIELDS_SEARCH:
            field_value = args.get(field)
            if field_value:
                field_value = int(field_value)
            search_vector[field] = field_value
        
        search_result = DB.getEntries(search_vector)
        filepath = analyze(search_result)
        response = send_file(filepath, mimetype='image/png')
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception:
        print(traceback.format_exc())
        raise InvalidUsage(traceback.format_exc())

serve(app, host='0.0.0.0', port=5000)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    