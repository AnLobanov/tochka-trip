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

def test_get_reservations(client, global_data):
    response = client.get('/admin/reservations', headers={"Authorization": "Bearer " + global_data['access_token']})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() != []

def test_get_reservations_no_access(client):
    response = client.get('/admin/reservations')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_confirm_reservation(client, global_data):
    response = client.get('/admin/reservations', headers={"Authorization": "Bearer " + global_data['access_token']})
    reservation = response.json()[-1]['id']
    print(reservation)
    response = client.patch('/admin/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": reservation})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_confirm_reservation_wrong_id(client, global_data):
    response = client.patch('/admin/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": 100})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_reservation(client, global_data):
    response = client.get('/admin/reservations', headers={"Authorization": "Bearer " + global_data['access_token']})
    reservation = response.json()[-1]['id']
    response = client.delete('/admin/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": reservation})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_delete_reservation_wrong_id(client, global_data):
    response = client.delete('/admin/reservation', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"reservation": 100})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_autoverify(client, global_data):
    response = client.get('/admin/autoverify', headers={"Authorization": "Bearer " + global_data['access_token']})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() != []

def test_change_autoverify(client, global_data):
    response = client.patch('/admin/autoverify', headers={"Authorization": "Bearer " + global_data['access_token']})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() in [True, False]

def test_change_price(client, global_data):
    response = client.patch('/admin/flight', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"flight": 1, "price": 1000})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_change_price_wrong_id(client, global_data):
    response = client.patch('/admin/flight', headers={"Authorization": "Bearer " + global_data['access_token']}, params={"flight": 100, "price": 1000})
    assert response.status_code == status.HTTP_404_NOT_FOUND