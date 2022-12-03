from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')
    # return "<p>Hello, World!</p>"

@app.route("/about")
def about():
    name="Dhanesh"
    return render_template('about.html',name=name)
    # return "<p>Hello, World!</p>"

app.run(debug=True)