"""hhtracker - track new vacancies on hh.ru"""
import logging
from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta
import requests


URL = "https://api.hh.ru/vacancies"
MAX_TIMEOUT = 3
MAX_PER_PAGE = 100
MOSCOW_CODE = 1
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


def fetch_pages(params):
    headers = {'user-agent': 'hhtracker'}
    params["page"] = 0
    while True:
        try:
            result = requests.get(URL,
                                  params=params,
                                  headers=headers,
                                  timeout=MAX_TIMEOUT)
            result.raise_for_status()

        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError):
            logging.error("Unable to connect to server")
            break
        except requests.exceptions.HTTPError:
            logging.error("Server error: %s", result.status_code)
            break
        else:
            data = result.json()
            current_page = int(data["page"])
            total_pages = int(data["pages"])
            yield data
            next_page = current_page + 1
            if next_page >= total_pages:
                break
            params["page"] = next_page


def get_vacancies(text, region):
    date_from = datetime.now() - timedelta(hours=24)
    params = {
        "per_page": MAX_PER_PAGE,
        "area": region,
        "search_field": "name",
        "date_from": date_from.strftime("%Y%m%d"),
        "text": text
    }
    for page in fetch_pages(params):
        show(page["items"])


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--keywords", nargs="+", help="Search keywords")
    parser.add_argument("--region", type=int, default=MOSCOW_CODE,
                        help="Region code. (https://api.hh.ru/areas)")
    return parser.parse_args()


def main():
    args = parse_args()
    get_vacancies(text=" ".join(args.keywords), region=args.region)


if __name__ == "__main__":
    main()
