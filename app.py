from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    name= "Shawshank Mishra"
    return render_template('abc.html',name1=name)

@app.route("/shaw")
def hello():
    return "<p>Hello shaw how are you!</p>"

app.run(debug=True)