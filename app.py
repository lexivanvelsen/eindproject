from flask import Flask, request, render_template

app = Flask(__name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info.html', methods=['GET'])
def info():
    color = request.args.get('color')
    return render_template('info.html', color=color)

# Implement the form submission and questionnaire handling here

if __name__ == '__main__':
    app.run(debug=True)
