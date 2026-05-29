import random
from faker import Faker
from factory import LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from app.models import Client, Parking, db

fake = Faker()

class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session
    name = LazyAttribute(lambda _: fake.first_name())
    surname = LazyAttribute(lambda _: fake.last_name())
    credit_card = LazyAttribute(lambda _: fake.credit_card_number() if random.choice([True, False]) else None)
    car_number = LazyAttribute(lambda _: fake.license_plate())

class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
    address = LazyAttribute(lambda _: fake.address())
    opened = LazyAttribute(lambda _: random.choice([True, False]))
    count_places = LazyAttribute(lambda _: random.randint(1, 100))
    count_available_places = LazyAttribute(lambda o: o.count_places)

def test_client_factory(db):
    c = ClientFactory()
    db.session.commit()
    assert c.id is not None

def test_parking_factory(db):
    p = ParkingFactory()
    db.session.commit()
    assert p.id is not None
