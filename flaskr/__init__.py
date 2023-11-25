import os

from flask import Flask, render_template, request, jsonify
import plotly
import json

import flaskr.load_json_to_plot as ljtp


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
    
    ljtp.load_data_json("flaskr//acids.json")
    
    @app.route('/', methods=["GET", "POST"])
    def index():
        if request.method == 'POST':

            acid_name = request.form.get('substance')
            acid = next((acid for acid in ljtp.acid_list if acid.name == acid_name), None)
            [fig1, fig2, fig3, fig4, fig5] = ljtp.create_plot(acid)
            
            return jsonify({'graphs': [{'id': 'graph1', 'graphJSON': json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)},
                                       {'id': 'graph2', 'graphJSON': json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)},
                                       {'id': 'graph3', 'graphJSON': json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)},
                                       {'id': 'graph4', 'graphJSON': json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)},
                                       {'id': 'graph5', 'graphJSON': json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)}]})
        
        return render_template("home.html", options=ljtp.acid_list)
    
    return app
