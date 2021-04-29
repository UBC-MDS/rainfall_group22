import json
from typing import Type
import traceback

import joblib
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

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

    return """
    <h1>Welcome to our rain prediction service</h1>
    To use this service, make a JSON post request to the /predict url with 5 climate model outputs.
    """

@app.route('/predict', methods=['GET', 'POST'])
def rainfall_prediction():
    content = request.json
    input_vals = None

    if not content is None:
        input_vals = list(content.values())[0]

    if (
        input_vals is None
        or (isinstance(input_vals, list) and not len(input_vals) == 25)):

        input_vals = np.random.randint(0, 250, 25).tolist()

    predicted_rainfall = return_prediction(input_vals=input_vals)

    results = dict(
        input_vals=input_vals,
        predicted_rainfall=f'{predicted_rainfall:.2f}mm')

    return jsonify(results), 200
