from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Client, Parking, ClientParking

api = Blueprint('api', __name__)

@api.route('/clients', methods=['GET'])
def get_clients():
    return jsonify([c.to_dict() for c in Client.query.all()]), 200

@api.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = db.session.get(Client, client_id)
    if not client:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(client.to_dict()), 200

@api.route('/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    new = Client(name=data['name'], surname=data['surname'],
                 credit_card=data.get('credit_card'), car_number=data.get('car_number'))
    db.session.add(new)
    db.session.commit()
    return jsonify(new.to_dict()), 201

@api.route('/parkings', methods=['POST'])
def create_parking():
    data = request.get_json()
    parking = Parking(address=data['address'], opened=data.get('opened', True),
                     count_places=data['count_places'],
                     count_available_places=data['count_places'])
    db.session.add(parking)
    db.session.commit()
    return jsonify(parking.to_dict()), 201

@api.route('/client_parkings', methods=['POST'])
def enter_parking():
    data = request.get_json()
    client_id, parking_id = data['client_id'], data['parking_id']
    parking = db.session.get(Parking, parking_id)
    if not parking or not parking.opened:
        return jsonify({'error': 'Parking closed'}), 400
    if parking.count_available_places <= 0:
        return jsonify({'error': 'No free places'}), 400
    active = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id, time_out=None).first()
    if active:
        return jsonify({'error': 'Already parked'}), 400
    cp = ClientParking(client_id=client_id, parking_id=parking_id, time_in=datetime.utcnow())
    parking.count_available_places -= 1
    db.session.add(cp)
    db.session.commit()
    return jsonify(cp.to_dict()), 201

@api.route('/client_parkings', methods=['DELETE'])
def exit_parking():
    data = request.get_json()
    client_id, parking_id = data['client_id'], data['parking_id']
    cp = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id, time_out=None).first()
    if not cp:
        return jsonify({'error': 'No active session'}), 404
    client = db.session.get(Client, client_id)
    if not client or not client.credit_card:
        return jsonify({'error': 'No credit card'}), 400
    time_out = datetime.utcnow()
    delta = time_out - cp.time_in
    cost = int(delta.total_seconds() / 3600 * 10) + 1 if delta.total_seconds() > 0 else 1
    cp.time_out = time_out
    parking = db.session.get(Parking, parking_id)
    if parking:
        parking.count_available_places += 1
    db.session.commit()
    return jsonify({'message': 'Exited', 'cost': cost}), 200
