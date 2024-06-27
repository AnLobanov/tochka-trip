from fastapi import status

def test_login_successful(client, global_data):
    response = client.post('/auth/login', json={
        "email": "anton@example.com",
        "password": "string123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()
    global_data['access_token'] = response.json()['access_token']
    global_data['refresh_token'] = response.json()['refresh_token']

def test_get_flight_access(client, global_data):
    response = client.get('/booking/get', headers={"Authorization": "Bearer " + global_data['access_token']})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() != []

def test_get_flight_no_access(client):
    response = client.get('/booking/get')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_reserve_success(client, global_data):
    response = client.get('/booking/get', headers={"Authorization": "Bearer " + global_data['access_token']})
    flight = response.json()[0]['id']
    places = response.json()[0]['places'][-1]['id']
    response = client.post('/booking/reserve', headers={"Authorization": "Bearer " + global_data['access_token']}, json={"flight": flight, "places": [places]})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_reserve_no_access(client):
    response = client.post('/booking/reserve', json={"flight": 1, "places": [1, 2]})
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_reserve_wrong_places(client, global_data):
    response = client.get('/booking/get', headers={"Authorization": "Bearer " + global_data['access_token']})
    flight = response.json()[0]['id']
    place = response.json()[0]['places'][-1]['id'] + 1
    response = client.post('/booking/reserve', headers={"Authorization": "Bearer " + global_data['access_token']}, json={"flight": flight, "places": [1, place]})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_reserve_wrong_flight(client, global_data):
    response = client.post('/booking/reserve', headers={"Authorization": "Bearer " + global_data['access_token']}, json={"flight": 100, "places": [1, 2]})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_reservation_success(client, global_data):
    response = client.get('/booking/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": 1})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() != {}

def test_get_reservation_no_access(client):
    response = client.get('/booking/reservation', params={"reservation": 1})
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_reservation_wrong_id(client, global_data):
    response = client.get('/booking/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": 100})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_reservation_success(client, global_data):
    response = client.get('/booking/reservations', headers={"Authorization": "Bearer " + global_data['access_token']})
    reservation = response.json()[0]['id']
    response = client.delete('/booking/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": reservation})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_delete_reservation_no_access(client):
    response = client.delete('/booking/reservation', params={"reservation": 1})
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_reservation_wrong_id(client, global_data):
    response = client.delete('/booking/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": 100})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_pay_reservation_success(client, global_data):
    response = client.get('/booking/pay', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": 1})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() != {}

def test_pay_reservation_no_access(client):
    response = client.get('/booking/pay', params={"reservation": 1})
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_pay_reservation_wrong_id(client, global_data):
    response = client.get('/booking/pay', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": 100})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_subscribe_success(client, global_data):
    response = client.get('/booking/subscribe', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"flight": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_subscribe_no_access(client):
    response = client.get('/booking/subscribe', params={"flight": "1"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_subscribe_wrong_id(client, global_data):
    response = client.get('/booking/subscribe', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"flight": "100"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
