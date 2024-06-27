from fastapi import status
from data import crud
from time import sleep

def test_successful_register(client, db, global_data):
    response = client.post('/auth/register', json={
        "profile": {
            "name": "Anton Lobanov"
        },
        "auth": {
            "email": "example@example.com",
            "password": "string123",
            "role": "admin"
        }
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}
    global_data['id'] = str(crud.Auth.get_id(db, "example@example.com"))

def test_wrong_register(client):
    response = client.post('/auth/register', json={
        "profile": {
            "name": "Anton Lobanov"
        },
        "auth": {
            "email": "antnlobanov2gmail.com",
            "password": "qwerty",
            "role": "admin"
        }
    })
    assert response.status_code != status.HTTP_200_OK
    assert response.json() != {"result": "success"}

def test_login_without_confirm(client):
    response = client.post('/auth/login', json={
        "email": "example@example.com",
        "password": "string123"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"error": "invalid user"}

def test_login_wrong_credentials(client):
    response = client.post('/auth/login', json={
        "email": "antnlobanov@gmail.com",
        "password": "string123"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"error": "invalid user"}

def test_resend_wrong(client):
    response = client.get('/auth/resend', params={"email": "antnlobanov@gmail.com"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_resend_successful(client):
    sleep(46)
    response = client.get('/auth/resend', params={"email": "example@example.com"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_verify_successful(client, global_data):
    response = client.get('/auth/verify/' + global_data['id'])
    assert response.status_code == status.HTTP_200_OK
    
def test_verify_wrong(client):
    response = client.get('/auth/verify/QEWRWTRTW')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_successful(client, global_data):
    response = client.post('/auth/login', json={
        "email": "example@example.com",
        "password": "string123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()
    global_data['access_token'] = response.json()['access_token']
    global_data['refresh_token'] = response.json()['refresh_token']

def test_refresh_successful(client, global_data):
    response = client.get('/auth/refresh', headers={"Authorization": "Bearer " + global_data['refresh_token']})
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()
    global_data['access_token'] = response.json()['access_token']
    global_data['refresh_token'] = response.json()['refresh_token']

def test_refresh_wrong(client):
    response = client.get('/auth/refresh', headers={"Authorization": "Bearer " + "21312wergverwfg1"})
    assert response.status_code == status.HTTP_403_FORBIDDEN 

def test_restore_send_successful(client):
    sleep(46)
    response = client.get('/auth/restore', params={"mail": "example@example.com"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_restore_send_wrong(client):
    response = client.get('/auth/restore', params={"mail": "antnlobanov@gmail.com"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}

def test_restore_works(client, db):
    response = client.get('/auth/verify/' + str(crud.Auth.get_id(db, "example@example.com")), params={"restore": True})
    assert response.status_code == status.HTTP_200_OK

def test_register_test_profile(client, db):
    response = client.post('/auth/register', json={
        "profile": {
            "name": "Anton Lobanov"
        },
        "auth": {
            "email": "anton@example.com",
            "password": "string123",
            "role": "admin"
        }
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}
    response = client.get('/auth/verify/' + str(crud.Auth.get_id(db, "anton@example.com")))
    assert response.status_code == status.HTTP_200_OK