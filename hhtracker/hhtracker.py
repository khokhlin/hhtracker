"""hhtracker - track new vacancies on hh.ru"""
import logging
from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta
import requests
import click
from .models import Employer
from .models import Vacancy
from .models import create_tables
from . import config


URL = config.api.url
MAX_TIMEOUT = config.api.max_timeout
MAX_PER_PAGE = config.api.max_per_page
MOSCOW_CODE = config.api.moscow_code

FMT = """{vacancy_name:<50.50} | {salary_from}/{salary_to} \
({currency}) | {created_at}")
{vacancy_url}
{employer_name} ({employer_url})
"""

def show(vacancies):
    """
    Available keys:
    [
        'type', 'archived', 'created_at', 'response_letter_required', 'snippet',
        'area', 'employer', 'alternate_url', 'sort_point_distance', 'relations',
        'url', 'department', 'published_at', 'salary', 'apply_alternate_url',
        'id', 'name', 'address', 'premium'
    ]
    """
    for vacancy in vacancies:
        vacancy_id = vacancy.get("id")
        vacancy_name = vacancy.get("name")
        vacancy_url = vacancy.get("url")
        salary = vacancy.get("salary") or {}
        currency = salary.get("currency") or "..."
        salary_from = salary.get("from") or "..."
        salary_to = salary.get("to") or "..."
        gross = salary.get("gross")
        employer = vacancy.get("employer")
        employer_name = employer.get("name")
        employer_url = employer.get("url")
        created_at = vacancy.get("created_at")
        print(FMT.format_map(locals()))

def show_():
    for vacancy in Vacancy.new_vacancies():
        click.echo("{} | {}".format(vacancy.name, vacancy.employer.name))

def fetch_pages(params):
    headers = {'user-agent': 'hhtracker'}
    params["page"] = 0
    while True:
        try:
            response = requests.get(URL,
                                    params=params,
                                    headers=headers,
                                    timeout=MAX_TIMEOUT)
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


def save(items):
    for vacancy in items:
        Vacancy.create(**vacancy)


def get_vacancies(text, region):
    date_from = datetime.now() - timedelta(hours=24)
    params = {
        "per_page": MAX_PER_PAGE,
        "area": region,
        "search_field": "name",
        "date_from": date_from.strftime("%Y%m%d"),
        "text": text
    }
    items = []
    for page in fetch_pages(params):
        items.extend(page["items"])
    save(items)
    show_()
    return items


@click.group()
def cli():
    pass


@cli.command()
def init_db():
    create_tables()


@cli.command()
@click.option("--keyword", "keywords", multiple=True)
@click.option("--region", type=int, default=MOSCOW_CODE)
def new(keywords, region):
    get_vacancies(text=" ".join(keywords), region=region)


def main():
    cli()


if __name__ == "__main__":
    main()
