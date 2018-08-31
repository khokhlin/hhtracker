from unittest import TestCase
import requests_mock
from hhtracker import config
config.test = True
from hhtracker.hhtracker import get_vacancies


class TestHHTracker(TestCase):

    @requests_mock.Mocker()
    def test_vacancy_created(self, mocker):
        resp = {"page": "0", "pages": 1, "items": []}
        mocker.get(requests_mock.ANY, json=resp)
        result = get_vacancies("python", 1)
        self.assertEqual(result, [])

        resp = {
            "page": "0",
            "pages": 1,
            "items": [{
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

        expected = [{
            'currency': 'RUB',
            'employer': {'employer_id': 1, 'name': 'Google'},
            'name': 'Python developer',
            'salary': '100000'
        }]
        self.assertEqual(result, expected)
