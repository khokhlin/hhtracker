"""hhtracker - track new vacancies on hh.ru"""
import sys
import logging
from datetime import datetime
from datetime import timedelta
import requests


URL = "https://api.hh.ru/vacancies"
MAX_TIMEOUT = 3
MAX_PER_PAGE = 100


def show(vacancy):
    """
    Available keys:
    [
        'type', 'archived', 'created_at', 'response_letter_required', 'snippet',
        'area', 'employer', 'alternate_url', 'sort_point_distance', 'relations',
        'url', 'department', 'published_at', 'salary', 'apply_alternate_url',
        'id', 'name', 'address', 'premium'
    ]
    """
    vacancy_id = vacancy.get("id")
    vacancy_name = vacancy.get("name")
    salary = vacancy.get("salary") or {}
    currency = salary.get("currency") or "..."
    salary_from = salary.get("from") or "..."
    salary_to = salary.get("to") or "..."
    gross = salary.get("gross")
    employer = vacancy.get("employer")
    employer_name = employer.get("name", "")
    created_at = vacancy.get("created_at")

    print(
        "{vacancy_id}: {vacancy_name} | SALARY: {salary_from}/{salary_to}({currency}) "
        "| CREATED: {created_at} | EMPLOYER: {employer_name}".format_map(locals())
    )


def fetch_pages(params):
    headers = {'user-agent': 'hhtracker'}
    params.update({
        "per_page": MAX_PER_PAGE,
        "page": 0
    })
    while True:
        try:
            result = requests.get(URL, params=params,
                                  headers=headers, timeout=MAX_TIMEOUT)
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
            if params["page"] == next_page:
                logging.error("Wrong page parameter")
                break
            params["page"] = next_page


def get_vacancies(text):
    date_from = datetime.now() - timedelta(hours=24)
    params = {
        "search_field": "name",
        "date_from": date_from.strftime("%Y%m%d"),
        "text": text
    }
    for page in fetch_pages(params):
        for vacancy in page["items"]:
            show(vacancy)


def main():
    if len(sys.argv) != 2:
        print("search argument is required")
        sys.exit(-1)

    get_vacancies(text=sys.argv[1])


if __name__ == "__main__":
    main()
