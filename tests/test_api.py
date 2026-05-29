import pytest
import time
from app.models import Client, Parking, ClientParking

@pytest.mark.parametrize('endpoint', ['/clients', '/clients/1'])
def test_get(client, endpoint):
    assert client.get(endpoint).status_code == 200

def test_create_client(client, db):
    r = client.post('/clients', json={'name': 'A', 'surname': 'B', 'credit_card': '1', 'car_number': 'X'})
    assert r.status_code == 201
    assert db.session.query(Client).count() == 2

def test_create_parking(client, db):
    r = client.post('/parkings', json={'address': 'Addr', 'opened': True, 'count_places': 5})
    assert r.status_code == 201
    assert db.session.query(Parking).count() == 2

@pytest.mark.parking
def test_enter(client, db):
    c = client.post('/clients', json={'name': 'E', 'surname': 'T', 'credit_card': '1', 'car_number': 'C1'}).get_json()
    p = client.post('/parkings', json={'address': 'P1', 'opened': True, 'count_places': 5}).get_json()
    r = client.post('/client_parkings', json={'client_id': c['id'], 'parking_id': p['id']})
    assert r.status_code == 201
    assert db.session.get(Parking, p['id']).count_available_places == 4

@pytest.mark.parking
def test_exit(client, db):
    c = client.post('/clients', json={'name': 'Ex', 'surname': 'It', 'credit_card': '5555', 'car_number': 'E1'}).get_json()
    p = client.post('/parkings', json={'address': 'P2', 'opened': True, 'count_places': 3}).get_json()
    client.post('/client_parkings', json={'client_id': c['id'], 'parking_id': p['id']})
    time.sleep(0.01)
    r = client.delete('/client_parkings', json={'client_id': c['id'], 'parking_id': p['id']})
    assert r.status_code == 200
    log = ClientParking.query.filter_by(client_id=c['id'], parking_id=p['id']).first()
    assert log.time_out > log.time_in

def test_exit_no_card(client, db):
    c = client.post('/clients', json={'name': 'No', 'surname': 'Card', 'car_number': 'N1'}).get_json()
    p = client.post('/parkings', json={'address': 'P3', 'opened': True, 'count_places': 2}).get_json()
    client.post('/client_parkings', json={'client_id': c['id'], 'parking_id': p['id']})
    r = client.delete('/client_parkings', json={'client_id': c['id'], 'parking_id': p['id']})
    assert r.status_code == 400
