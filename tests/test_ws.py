from unittest import TestCase

from hhtracker import config
config.test = True
from hhtracker.models import create_tables, drop_tables
from hhtracker.models import Vacancy
from hhtracker.ws import app


class TestWebServer(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        create_tables()

    @classmethod
    def tearDownClass(cls):
        drop_tables()

    def test_can_get_vacancies(self):
        vacancy_params = {
            "vacancy_id": 1,
            "name": "Python Developer",
            "employer": {
                "employer_id": 1,
                "name": "Google",
            },
            "currency": "RUB",
            "salary": 100000,
        }
        Vacancy.create(**vacancy_params)
        vacancy = self.client.get("/").get_json()[0]
        self.assertEqual(vacancy_params["vacancy_id"], vacancy["vacancy_id"])
        self.assertEqual(vacancy_params["salary"], vacancy["salary"])
        self.assertEqual(vacancy_params["employer"], vacancy["employer"])

