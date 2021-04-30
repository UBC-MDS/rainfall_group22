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


def return_prediction(input_vals: list) -> float:
    """Return model prediction

    Parameters
    ----------
    input_vals : list
        list of length 25 for model to predict

    Returns
    -------
    float
        model's predicted value

    Raises
    ------
    APIError
        incorrect input type
    APIError
        wrong length list
    """    
    if not isinstance(input_vals, list):
        raise APIError(
            f'Input must be of type list|ndarray, you input: ({type(input_vals)}, {input_vals})')
    
    len_vals = len(input_vals)
    if not len_vals == 25:
        raise APIError(
            f'Input array must be of length 25, your array length: {len_vals}'
        )

    x = np.array(input_vals).reshape(1, len(input_vals))
    return model.predict(x)[0]

@app.route("/")
def index():
    header = 'Welcome to our rain prediction service'

    body = Markup("""
    <h3>525 Group 22</h3>

    To use this service, make a JSON post request to the <code>/predict</code> url with an array of 25 input values between 0 and 250.<br>
    Requests with an empty array will return a prediction for 25 random values.<br><br>
    
    eg:
    <pre>curl -X POST http://<ec2_ip_address>:8080/predict -d '{"data":[1,2,3,4,53,11,22,37,41,53,11,24,31,44,53,11,22,35,42,53,12,23,31,42,53]} -H "Content-Type: application/json"<br>
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
        if isinstance(content, dict) and len(content) > 0:
            input_vals = list(content.values())[0]
        else:
            raise APIError('Input data incorrect format.')
    else:
        raise APIError('Missing input data.')

    # allow blank input, just use random numbers for input_vals
    if (
        input_vals is None
        or (isinstance(input_vals, list) and len(input_vals) == 0)):

        input_vals = np.random.randint(0, 250, 25).tolist()

    predicted_rainfall = return_prediction(input_vals=input_vals)

    results = dict(
        predicted_rainfall=f'{predicted_rainfall:.2f}mm',
        input_vals=input_vals)

    return jsonify(results), 200
