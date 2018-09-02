import sys
import datetime
from peewee import Model
from peewee import SqliteDatabase
from peewee import BooleanField
from peewee import CharField
from peewee import DateField
from peewee import IntegerField
from peewee import ForeignKeyField
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


class Vacancy(BaseModel):
    vacancy_id = IntegerField(primary_key=True)
    name = CharField()
    salary = IntegerField()
    created_at = DateField(default=datetime.datetime.now)
    employer = ForeignKeyField(Employer, backref="vacancies")
    visible = BooleanField(default=True)

    @classmethod
    def create(cls, **kwargs):
        employer_params = kwargs.pop("employer")
        employer = Employer.create(**employer_params)
        return super().create(employer=employer, **kwargs)

    @classmethod
    def new_vacancies(cls):
        return cls.select().join(Employer).where(cls.visible == True, Employer.visible == True)


def create_tables():
    db.connect()
    db.create_tables([Employer, Vacancy])
