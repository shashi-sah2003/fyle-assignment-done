from core.server import app
import pytest
from flask import Flask
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from core.server import handle_error

def test_ready():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'ready'
    assert 'time' in data

def test_integrity_error_handling():
    @app.route('/integrity-error')
    def integrity_error_route():
        raise IntegrityError('Integrity error', 'params', 'orig')

    client = app.test_client()
    response = client.get('/integrity-error')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'IntegrityError'
    assert data['message'] == 'orig'

def test_http_exception_handling():
    @app.route('/http-exception')
    def http_exception_route():
        raise BadRequest('Bad request')

    client = app.test_client()
    response = client.get('/http-exception')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'BadRequest'
    assert data['message'] == '400 Bad Request: Bad request'

def test_other_error_raising():
    """Test raising of non-HTTP exceptions"""
    app = Flask(__name__)
    
    with app.test_request_context():
        error = ValueError("Test error")
        
        with pytest.raises(ValueError):
            handle_error(error)