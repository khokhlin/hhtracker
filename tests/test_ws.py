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
        vacancy = self.client.get("/api/vacancies").get_json()[0]
        self.assertEqual(vacancy_params["vacancy_id"], vacancy["vacancy_id"])
        self.assertEqual(vacancy_params["salary"], vacancy["salary"])
        self.assertEqual(vacancy_params["employer"], vacancy["employer"])

        for i in range(2, 10):
            vacancy_params["vacancy_id"] = i
            Vacancy.create(**vacancy_params)

        page1 = self.client.get("/api/vacancies").get_json()
        self.assertEqual(len(page1), 3)
        page2 = self.client.get("/api/vacancies").get_json()

        # Change the first record visibility

        self.client.post("/api/vacancy/1", json={"visible": False})
        resp = self.client.get("/api/vacancies?per_page=10").get_json()
        self.assertEqual(len(resp), 8)
        self.assertEqual(len([item for item in resp if item["vacancy_id"] == 1]), 0)
