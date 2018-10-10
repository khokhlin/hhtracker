import logging
import sys
import datetime
from peewee import Model
from peewee import SqliteDatabase
from peewee import BooleanField
from peewee import CharField
from peewee import DateField
from peewee import IntegerField
from peewee import ForeignKeyField
from playhouse.shortcuts import model_to_dict
from . import config


if config.test is True:
    config.database = ":memory:"

db = SqliteDatabase(config.database)


class BaseModel(Model):
    class Meta:
        database = db


class Employer(BaseModel):
    employer_id = IntegerField(primary_key=True)
    name = CharField()
    visible = BooleanField(default=True)

    _visible_fields = [employer_id, name]


class Vacancy(BaseModel):
    vacancy_id = IntegerField(primary_key=True)
    name = CharField()
    salary = IntegerField()
    created_at = DateField(default=datetime.datetime.now)
    employer = ForeignKeyField(Employer, backref="vacancies")
    currency = CharField()
    visible = BooleanField(default=True)

    _visible_fields = [
        vacancy_id, name, salary, currency, created_at, employer
    ] + Employer._visible_fields

    @classmethod
    def create(cls, **kwargs):
        employer = kwargs.pop("employer", None)
        if employer:
            new_employer, created = Employer.get_or_create(**employer)
            kwargs["employer_id"] = new_employer.employer_id
        return super().create(**kwargs)

    @classmethod
    def save_vacancies(cls, items):
        for vacancy in items:
            employer = vacancy.pop("employer")
            try:
                employer["employer_id"] = employer.pop("id")
                vacancy["vacancy_id"] = vacancy.pop("id")
            except KeyError:
                logging.error("Mailformed vacancy: %s", vacancy)
                continue
            new_employer, created = Employer.get_or_create(
                employer_id=employer["employer_id"], defaults=employer)
            vacancy["employer_id"] = new_employer.employer_id
            new_vacancy, created =  Vacancy.get_or_create(
                vacancy_id=vacancy["vacancy_id"], defaults=vacancy)
            yield new_vacancy

    @classmethod
    def new_vacancies(cls, page, per_page):
        return cls.select().join(Employer).where(
            cls.visible == True,
            Employer.visible == True
        ).paginate(page, per_page)

    def to_dict(self):
        return  model_to_dict(self, recurse=True, only=self._visible_fields)


def create_tables():
    if db.is_closed():
        db.connect()
    db.create_tables([Employer, Vacancy])


def drop_tables():
    if db.is_closed():
        db.connect()
    db.drop_tables([Employer, Vacancy])
