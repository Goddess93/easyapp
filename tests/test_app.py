# tests/test_app.py

import os
import io
import pytest
from myapp import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'test_uploads'
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(autouse=True)
def run_around_tests():
    # Create test upload folder before tests
    if not os.path.exists('test_uploads'):
        os.makedirs('test_uploads')
    yield
    # Clean up test upload folder after tests
    for file in os.listdir('test_uploads'):
        file_path = os.path.join('test_uploads', file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    os.rmdir('test_uploads')

def test_welcome_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_greet_page(client):
    response = client.post('/greet', data={'name': 'Alice', 'greet': 'Hello'})
    assert response.status_code == 200
    assert b"Hello, Alice" in response.data

def test_upload_no_file(client):
    response = client.post('/upload', data={})
    assert response.status_code == 302  # Redirects back to the form
    with client.session_transaction() as sess:
        flash_messages = list(sess['_flashes'])
        assert ('message', 'No file part') in flash_messages

def test_upload_empty_file(client):
    data = {
        'file': (b'', '')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 302  # Redirects back to the form
    with client.session_transaction() as sess:
        flash_messages = [(msg[0], msg[1]) for msg in sess['_flashes']]
        assert ('message', 'No file part') in flash_messages


def test_upload_file(client):
    data = {
        'file': (io.BytesIO(b"dummy file contents"), 'test.jpg')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"File successfully uploaded" in response.data

def test_upload_invalid_file(client):
    data = {
        'file': (io.BytesIO(b"dummy file contents"), 'test.txt')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 302  # Redirects back to the form
    with client.session_transaction() as sess:
        flash_messages = list(sess['_flashes'])
        assert ('message', 'File type not allowed') in flash_messages
