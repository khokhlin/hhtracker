from flask import Flask
from flask import jsonify
from hhtracker.models import Vacancy


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify([
        vacancy.to_dict() for vacancy in Vacancy.new_vacancies()
    ])


if __name__ == "__main__":
    app.run()
