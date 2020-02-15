from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/healthz')
def healthcheck():
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
