from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from hhtracker.models import Vacancy


app = Flask(__name__)
ITEMS_PER_PAGE = 3


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/vacancies", methods=["GET"])
def get_vacancies():
    page = request.args.get("page", 1, type=int)
    return jsonify([
        vacancy.to_dict() for vacancy
        in Vacancy.new_vacancies(page, ITEMS_PER_PAGE)
    ])

if __name__ == "__main__":
    app.run()
