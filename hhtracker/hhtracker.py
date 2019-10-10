"""hhtracker - track new vacancies on hh.ru"""
import asyncio
import logging
from datetime import datetime
from datetime import timedelta
from argparse import ArgumentParser
import aiohttp
import requests

from . import config
from .models import Vacancy
from .models import create_tables


class HhClient:

    resource_uri = config.api.url.strip("/") + "/vacancies"

    def get_pages(self,
                  per_page=config.api.max_per_page,
                  area=config.api.moscow_code,
                  search_field="text",
                  text=None,
                  page=0,
                  date_from=None):

        if date_from is None:
            date_from = (datetime.now() - timedelta(hours=24)).strftime("%Y%m%d")

        params = {
            "per_page": per_page,
            "area": area,
            "search_field": search_field,
            "text": text,
            "page": page,
            "date_from": date_from
        }

        max_timeout = config.api.max_timeout

        headers = {'user-agent': 'hhtracker'}


        while True:
            try:
                response = requests.get(self.resource_uri,
                                        params=params,
                                        headers=headers,
                                        timeout=max_timeout)
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


async def get_vacancies_async(query_text, region):
    session = aiohttp.ClientSession()
    resource_uri = config.api.url.strip("/") + "/vacancies"
    date_from = (datetime.now() - timedelta(hours=24)).strftime("%Y%m%d")
    params = {
        "per_page": config.api.per_page,
        "area": config.api.moscow_code,
        "search_field": "name",
        "text": query_text,
        "page": 0,
        "date_from": date_from
    }

    async with session.get(resource_uri, params=params) as resp:
        text = await resp.text()
        print(text)
    await session.close()
    return text


def get_vacancies(query_text, region):
    client = HhClient()
    pages = client.get_pages(
        area=region,
        text=query_text
    )
    def new_vacancies():
        for page in pages:
            for vacancy in page["items"]:
                vacancy["vacancy_id"] = vacancy.pop("id")
                employer = vacancy["employer"]
                employer["employer_id"] = employer.pop("id")
                vacancy["employer"] = employer
                yield vacancy
    saved = Vacancy.save_vacancies(new_vacancies())
    return (vacancy.to_dict() for vacancy in saved)


def parse_args():
    parser = ArgumentParser("hhtracker")
    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--region", type=int, default=config.api.moscow_code)
    parser.add_argument("--keywords", nargs="+", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.init_db:
        create_tables()

    query_text = " ".join(args.keywords or [])

    loop = asyncio.get_event_loop()
    vacancies = loop.run_until_complete(
        get_vacancies_async(query_text=query_text, region=args.region)
    )
    print(vacancies)


if __name__ == "__main__":
    main()
