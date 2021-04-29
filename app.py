import json
from typing import Type

import joblib
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

model_name = 'model.joblib'
model = joblib.load(model_name)


def return_prediction(input_vals: list=None) -> float:

    if not isinstance(input_vals, list):
        raise TypeError(
            f'Input must be of type "list|narray", you input "{type(input_vals)}": {input_vals}')

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

    if input_vals is None or not len(input_vals) == 25:
        input_vals = np.random.randint(0, 250, 25).tolist()

    predicted_rainfall = return_prediction(input_vals=input_vals)

    results = dict(
        input_vals=input_vals,
        predicted_rainfall=f'{predicted_rainfall:.2f}mm')

    print(results)

    return jsonify(results)
