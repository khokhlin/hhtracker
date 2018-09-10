from unittest import TestCase
import requests_mock
from hhtracker import config
config.test = True
from hhtracker.hhtracker import get_vacancies
from hhtracker.models import create_tables, drop_tables


class TestHHTracker(TestCase):

    @classmethod
    def setUpClass(cls):
        create_tables()

    @classmethod
    def tearDownClass(cls):
        drop_tables()

    @requests_mock.Mocker()
    def test_vacancies_created(self, mocker):
        resp = {"page": "0", "pages": 1, "items": []}
        mocker.get(requests_mock.ANY, json=resp)
        result = get_vacancies("python", 1)
        self.assertEqual(result, [])

        resp = {
            "page": "0",
            "pages": 1,
            "items": [{
                "vacancy_id": 1,
                "name": "Python developer",
                "salary": "100000",
                "currency": "RUB",
                "employer": {
                    "employer_id": 1,
                    "name": "Google"
                }
            }]
        }
        mocker.get(requests_mock.ANY, json=resp)

        result = get_vacancies("python", 1)
        result = get_vacancies("python", 1)

        result[0].pop("created_at")

        expected = [{
            'vacancy_id': 1,
            'currency': 'RUB',
            'employer': {'employer_id': 1, 'name': 'Google'},
            'name': 'Python developer',
            'salary': 100000
        }]
        self.assertEqual(result, expected)

        resp["items"].append({
            "vacancy_id": 2,
            "name": "Java Developer",
            "salary": "2000000",
            "currency": "RUB",
            "employer": {
                "employer_id": 1,
                "name": "Google",
            }
        })

        items = get_vacancies("python", 1)
        self.assertEqual(len(items), 2)
        self.assertEqual(int(items[0]["vacancy_id"]), 1)
        self.assertEqual(int(items[1]["vacancy_id"]), 2)
        self.assertEqual(int(items[0]["employer"]["employer_id"]), 1)
        self.assertEqual(int(items[1]["employer"]["employer_id"]), 1)
