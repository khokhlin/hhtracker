"""hhtracker - track new vacancies on hh.ru"""
import logging
from datetime import datetime
from datetime import timedelta
import requests
from hhtracker.models import Vacancy
from hhtracker.models import create_tables
from hhtracker import config


class HhClient:

    resource_uri = config.api.url.strip("/") + "/vacancies"
    max_timeout = config.api.max_timeout
    max_per_page = config.api.max_per_page
    moscow_code = config.api.moscow_code

    def _get_pages(self, params):
        headers = {'user-agent': 'hhtracker'}
        params["page"] = 0
        while True:
            try:
                response = requests.get(self.resource_uri,
                                        params=params,
                                        headers=headers,
                                        timeout=self.max_timeout)
                response.raise_for_status()
                data = response.json()
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError):
                logging.error("Unable to connect to server")
                break
            except requests.exceptions.HTTPError:
                logging.error("Server error: %s", response.status_code)
                break
            except ValueError:
                logging.error("Response is not JSON")
                break
            else:
                current_page = int(data["page"])
                total_pages = int(data["pages"])
                yield data
                next_page = current_page + 1
                if next_page >= total_pages:
                    break
                params["page"] = next_page

    def new_vacancies(self, keywords_str, region):
        date_from = datetime.now() - timedelta(hours=24)
        params = {
            "per_page": self.max_per_page,
            "area": region,
            "search_field": "name",
            "date_from": date_from.strftime("%Y%m%d"),
            "text": keywords_str
        }

        for page in self._get_pages(params):
            for vacancy in page["items"]:
                vacancy["vacancy_id"] = vacancy.pop("id")
                employer = vacancy["employer"]
                employer["employer_id"] = employer.pop("id")
                vacancy["employer"] = employer
                yield vacancy


def get_vacancies(keywords_str, region):
    client = HhClient()
    new_vacancies = client.new_vacancies(keywords_str, region)
    saved = Vacancy.save_vacancies(new_vacancies)
    return (vacancy.to_dict() for vacancy in saved)


def run(region=config.api.moscow_code, keywords=None, init_db=False):
    if init_db:
        create_tables()

    keywords_str = " ".join(keywords or [])
    get_vacancies(keywords_str=keywords_str, region=region)
