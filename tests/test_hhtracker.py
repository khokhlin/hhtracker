from unittest import TestCase
import requests_mock
from click.testing import CliRunner
from hhtracker import config
config.test = True
from hhtracker.hhtracker import get_vacancies
from hhtracker.hhtracker import new
from hhtracker.models import create_tables


class TestHHTracker(TestCase):

    @classmethod
    def setUpClass(cls):
        create_tables()

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

    @requests_mock.Mocker()
    def test_cli(self, mocker):
        resp = {
            "page": "0",
            "pages": 1,
            "items": [{
                "name": "Python developer",
                "salary": "100000",
                "currency": "RUB",
                "employer": {
                    "employer_id": 2,
                    "name": "Google"
                }
            }]
        }
        mocker.get(requests_mock.ANY, json=resp)
        runner = CliRunner()
        result = runner.invoke(new, ["--keyword", "python"])
        self.assertIn("Python developer", result.output)
