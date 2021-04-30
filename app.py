import json
import traceback

import joblib
import numpy as np
from flask import Flask, jsonify, request, render_template, Markup

app = Flask(__name__, static_folder='static', template_folder='templates')

model_name = 'model.joblib'
model = joblib.load(model_name)

class APIError(Exception):
    """Custom known error"""
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.code = 400

@app.errorhandler(APIError)
def handle_exception(err):
    """Handle known exceptions (eg incorrect input)"""
    response = dict(error=str(err))
    return jsonify(response), err.code

@app.errorhandler(500)
def handle_exception(err):
    """Handle all other errors"""
    app.logger.error(f'Unknown Exception: {str(err)}')
    tb = traceback.format_exception(etype=type(err), value=err, tb=err.__traceback__)
    app.logger.debug(''.join(tb))

    response = dict(
        error='Sorry, an unknown exception occurred',
        description=str(err))

    return jsonify(response), 500


def return_prediction(input_vals: list=None) -> float:

    if not isinstance(input_vals, list):
        raise APIError(
            f'Input must be of type list|ndarray, you input: ({type(input_vals)}, {input_vals})')

    x = np.array(input_vals).reshape(1, len(input_vals))
    return model.predict(x)[0]

@app.route("/")
def index():
    header = 'Welcome to our rain prediction service'

    # <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
    body = Markup("""
    <h3>525 Group 22</h3>

    To use this service, make a JSON post request to the <code>/predict</code> url with an array of 25 input values between 0 and 250.<br>
    Requests with an empty array will return a prediction for 25 random values.<br><br>
    
    eg:
    <pre>curl -X POST ec2_ip_address/predict -d '{"data":[1,2,3,4,53,11,22,37,41,53,11,24,31,44,53,11,22,35,42,53,12,23,31,42,53]} -H "Content-Type: application/json"<br>
{
    "input_vals": [1, 2, 3, 4, 53, 11, 22, 37, 41, 53, 11, 24, 31, 44, 53, 11, 22, 35, 42, 53, 12, 23, 31, 42, 53], 
    "predicted_rainfall": "31.59mm"
}</pre><br><br>
    """)
    
    return render_template(
        "index.html",
        header=header,
        body=body), 200

@app.route('/predict', methods=['GET', 'POST'])
def rainfall_prediction():
    content = request.json
    input_vals = None

    if not content is None:
        input_vals = list(content.values())[0]

    # allow blank input, just use random numbers for input_vals
    if (
        input_vals is None
        or (isinstance(input_vals, list) and not len(input_vals) == 25)):

        input_vals = np.random.randint(0, 250, 25).tolist()

    predicted_rainfall = return_prediction(input_vals=input_vals)

    results = dict(
        predicted_rainfall=f'{predicted_rainfall:.2f}mm',
        input_vals=input_vals)

    return jsonify(results), 200
