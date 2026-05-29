import pytest
from app import create_app
from app.models import db as _db
from app.models import Client, Parking

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        _db.create_all()
        client = Client(name='Test', surname='User', credit_card='1234', car_number='A123')
        parking = Parking(address='Test Street', opened=True, count_places=10, count_available_places=10)
        _db.session.add_all([client, parking])
        _db.session.commit()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
