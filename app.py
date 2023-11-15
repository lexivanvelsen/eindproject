from flask import Flask, render_template, request, redirect, url_for
import collections

app = Flask(__name__)

# Een eenvoudige database voor het bijhouden van klantgegevens en feedback
customer_data = {}
feedback_data = collections.defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info.html', methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        # Verwerk het formulier en bewaar de gegevens
        color = request.args.get('color')
        name = request.form['name']
        email = request.form['email']
        street = request.form['street']
        postcode = request.form['postcode']
        city = request.form['city']

        customer_data[name] = {
            'color': color,
            'name': name,
            'email': email,
            'street': street,
            'postcode': postcode,
            'city': city
        }

        return redirect(url_for('bedankt'))

    return render_template('info.html')

@app.route('/bedankt')
def bedankt():
    return render_template('bedankt.html')

@app.route('/form.html', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Verwerk het klanttevredenheidsonderzoek
        name = request.form['name']
        feedback = {
            'q1': request.form['q1'],
            'q2': request.form['q2'],
            'q3': request.form['q3'],
            'q4': request.form['q4'],
            'q5': request.form['q5']
        }

        feedback_data[name].append(feedback)

        return redirect(url_for('index'))

    return render_template('form.html')

@app.route('/results')
def results():
    # Analyseer klantfeedback
    result = {}
    for name, feedback_list in feedback_data.items():
        count_yes = 0
        count_no = 0
        for feedback in feedback_list:
            for answer in feedback.values():
                if answer == 'ja':
                    count_yes += 1
                elif answer == 'nee':
                    count_no += 1
        if count_yes >= 3:
            result[name] = "TEVREDEN"
        else:
            result[name] = "NIET TEVREDEN"

    return render_template('results.html', results=result)

if __name__ == '__main__':
    app.run(debug=True)
