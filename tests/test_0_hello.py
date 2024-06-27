from fastapi.testclient import TestClient
from fastapi import status
from main import app

clinet = TestClient(app)

def test_get_hello():
    response = clinet.get('/hello')
    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"hello"'

def test_post_echo():
    response = clinet.post('/echo', content="123")
    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"123"'

def test_post_wrong_echo():
    response = clinet.post('/echo', content="321")
    assert response.status_code == status.HTTP_200_OK
    assert response.text != '"123"'

def test_get_echo():
    response = clinet.get('/echo', headers={"foo": "bar"})
    assert response.status_code == status.HTTP_200_OK
    assert "foo" in response.json().keys()
    assert "bar" in response.json().values()

def test_get_wrong_echo():
    response = clinet.get('/echo', headers={"foo": "bar"})
    assert response.status_code == status.HTTP_200_OK
    assert "foo" not in response.json().values()
    assert "bar" not in response.json().keys()