import os

from flask import Flask, render_template, request, jsonify
from flaskr.plot import create_plot
import flaskr.main as m         # NOTE: plik main, myśle żeby zmienic nazwę
import plotly.express as px
import plotly

import json
from math import sqrt, log10
from numpy import roots


global acid
acid = None

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
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
    
    m.load_data_json("flaskr//acids.json")
    
    @app.route('/', methods=["GET", "POST"])
    def index():
        if request.method == 'POST':
            # tu potrzeba tworzenia wykresu

            acid_name = request.form.get('substance')
            for i in range(len(m.acid_list)):
                if m.acid_list[i].name == acid_name:
                    acid = m.acid_list[i]

            [fig1, fig2] = create_plot(acid)
            

            # tu potrzeba tworzenia wykresu
            height = request.form.get('pH')
            
            graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            return jsonify({'graphs': [{'id': 'graph1', 'graphJSON': graphJSON1},
                                       {'id': 'graph2', 'graphJSON': graphJSON2}]})
        
        return render_template("home.html", options=m.acid_list)
    
    return app
