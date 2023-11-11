from flask import Flask


app = Flask(__name__)
@app.route('/')

def index():
    return 'RUCHAM CI STARA ESSAAAAAAAAAAAAAAAAAAAAAAAAA'

if __name__ == '__main__':
    app.run(debug=True)