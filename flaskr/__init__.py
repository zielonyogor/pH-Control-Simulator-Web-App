import os

from flask import Flask, render_template, request
from flaskr.plot import create_plot
import plotly.express as px
import plotly.io as pio


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
    
    @app.route('/', methods=["GET", "POST"])
    def index():
        if request.method == 'POST':
            height = request.form.get('height')

            fig = create_plot(height)

            plot_html = pio.to_html(fig, full_html=False)

            return render_template('home.html', plot_html=plot_html)
        return render_template("home.html")

    return app