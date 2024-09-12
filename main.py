from flask import Flask, request, send_from_directory, jsonify, render_template, url_for

app = Flask(__name__)

@app.route('/')
def get_ok():
    return render_template("game.html")

@app.route('/static/&lt;path:path&gt;')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80, threaded = True)