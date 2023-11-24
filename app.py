from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

customer_data = {}
feedback_data = {'tevreden': 0, 'niet tevreden': 0}

# FUNCTIONS
# voorraad functions

def load_and_format_csv(csv_file):
    voorraad = {}
    show_voorraad = False
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_directory, csv_file)

    with open(csv_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            voorraad[row['color']] = int(row['Voorraad'])
            show_voorraad = True

    return voorraad, show_voorraad

def save_voorraad_to_csv(voorraad):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_directory, 'voorraad.csv')

    with open(csv_path, mode='w', newline='') as csvfile:
        fieldnames = ['color', 'Voorraad']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for color, voorraad_value in voorraad.items():
            writer.writerow({'color': color, 'Voorraad': voorraad_value})

def update_inventory_and_redirect(gekozen_kleur, voorraad):
    if gekozen_kleur in voorraad and voorraad[gekozen_kleur] > 0:
        voorraad[gekozen_kleur] -= 1
        save_voorraad_to_csv(voorraad)

    return redirect(url_for('info', color=gekozen_kleur))


# Enquete functions

def process_enquete_results(result):
    with open('enquete_data.csv', mode='a', newline='') as file:
        fieldnames = ['Naam', 'color', 'resultaat']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()

        for name, resultaat in result.items():
            writer.writerow({'Naam': name, 'color': resultaat['color'], 'resultaat': resultaat['result']})


# ROUTES

@app.route('/', methods=['GET', 'POST'])
def index():
    voorraad, show_voorraad = load_and_format_csv('voorraad.csv')

    if request.method == 'POST':
        gekozen_kleur = request.form.get('color')
        update_inventory_and_redirect(gekozen_kleur, voorraad)

        return redirect(url_for('info'))

    return render_template('index.html', voorraad=voorraad, show_voorraad=show_voorraad)

@app.route('/voorraad', methods=['GET'])
def voorraad_route():
    voorraad, _ = load_and_format_csv('voorraad.csv')
    print_voorraad(voorraad)
    return render_template('voorraad.html')

@app.route('/submit_stock', methods=['POST','GET'])
def submit_stock():
    voorraad, _ = load_and_format_csv('voorraad_beheer.csv')

    gekozen_kleur = request.form.get('color')

    if gekozen_kleur is not None and gekozen_kleur in voorraad:
        update_inventory_and_redirect(gekozen_kleur, voorraad)


        data = {'color': gekozen_kleur, 'voorraad': voorraad[gekozen_kleur]}
        with open('voorraad_beheer.csv', mode='a', newline='') as file:
            fieldnames = ['color', 'voorraad']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)

    return redirect(url_for('results'))




@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
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

@app.route('/bedankt', methods=['GET', 'POST'])
def bedankt():
    if request.method == 'POST':
        return redirect(url_for('bedankt'))

    return render_template('bedankt.html')


@app.route('/form.html', methods=['GET', 'POST'])
def form():
    question = [
        {"name": "q1", "question_text": "Bent u tevreden over de gebruikersvriendelijkheid van de website?"},
        {"name": "q2", "question_text": "Bent u tevreden over de verzending en levering van de website?"},
        {"name": "q3", "question_text": "Bent u tevreden over de pasvorm van uw T-shirt?"},
        {"name": "q4", "question_text": "Bent u tevreden over uw product in het algemeen?"},
        {"name": "q5", "question_text": "Zou u deze website aanraden aan vrienden of familie?"}
    ]

    if request.method == 'POST':
        name = request.form.get("name")
        feedback = {
            "q1": request.form.get("q1", ""),
            "q2": request.form.get("q2", ""),
            "q3": request.form.get("q3", ""),
            "q4": request.form.get("q4", ""),
            "q5": request.form.get("q5", "")
        }

        if name not in feedback_data:
            feedback_data[name] = []

        feedback_data[name].append(feedback)

        return redirect(url_for('results'))

    return render_template('form.html')


@app.route('/submit_enquete', methods=['POST', 'GET'])
def submit_enquete():
    data = request.form.to_dict()

    resultaat_values = [data.pop(f'q{i}') for i in range(1, 6)]
    data['resultaat'] = "tevreden" if resultaat_values.count("ja") >= 3 else "niet tevreden"

    feedback_data[data['resultaat']] += 1

    with open('enquete_data.csv', mode='a', newline='') as file:
        fieldnames = ['Naam', 'color', 'resultaat']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)

    return redirect(url_for('results'))


@app.route('/results', methods=['GET', 'POST'])
def results():

    return render_template('results.html')

@app.route('/verwerk_resultaten', methods=['GET', 'POST'])
def verwerk_resultaten():
    result = {}
    for naam, resultaat in feedback_data.items():
        if naam != 'tevreden' and naam != 'niet tevreden':
            result[naam] = "TEVREDEN" if resultaat.count("ja") >= 3 else "NIET TEVREDEN"
    print("Resultaten:")
    print("{:<20} {:<20}".format("Naam", "Resultaat"))
    for naam, resultaat in result.items():
        print("{:<20} {:<20}".format(naam, resultaat))
    
    return "Resultaten verwerkt en afgedrukt naar enquete_data."


if __name__ == '__main__':
    current_directory = os.getcwd()
    csv_file_path = os.path.join(current_directory, 'form.csv')
    app.run(debug=True)

