"""Web Server Module"""
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import abort
from flask_bootstrap import Bootstrap
from hhtracker.models import Vacancy


app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
Bootstrap(app)

ITEMS_PER_PAGE = 3


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/vacancies", methods=["GET"])
def get_vacancies():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    return jsonify([
        vacancy.to_dict() for vacancy
        in Vacancy.new_vacancies(page, per_page)
    ])


@app.route("/api/vacancies/<int:vacancy_id>", methods=["POST"])
def update_vacancy(vacancy_id):
    vacancy = Vacancy.get_by_id(vacancy_id)
    if not vacancy:
        abort(404)
    data = request.json
    if data:
        vacancy.visible = data["visible"]
        vacancy.save()

    return jsonify(vacancy.to_dict())
