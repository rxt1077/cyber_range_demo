import os
import pytest

from bs4 import BeautifulSoup

from app import create_app

TEST_DB_FILE = 'test.db'

@pytest.fixture()
def app():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    os.environ['DB_FILE'] = TEST_DB_FILE
    app = create_app()
    app.config.update({
        'TESTING': True,
    })

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def admin_logged_in(client):
    username = "admin"
    password = os.getenv("DEFAULT_ADMIN_PASSWORD")

    response = client.get('/login')
    soup = BeautifulSoup(response.text, features="html.parser")
    csrf_token = soup.find(id="csrf_token")['value']
    response = client.post('/login', data={
        "csrf_token": csrf_token, 
        "username"  : username,
        "password"  : password,})
    assert response.status_code == 302

    yield client
