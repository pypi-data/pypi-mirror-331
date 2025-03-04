import pytest
from git_commit_chart.app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Git Commit History Visualization' in response.data

def test_by_user_route(client):
    """Test the by-user route."""
    response = client.get('/by-user')
    assert response.status_code == 200
    assert b'Git Commits by User' in response.data

def test_get_commits_valid_input(client):
    """Test the get_commits route with valid input."""
    response = client.post('/get_commits', json={
        'owner': 'facebook',
        'repo': 'react'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'dates' in data
    assert 'counts' in data

def test_get_commits_invalid_input(client):
    """Test the get_commits route with invalid input."""
    response = client.post('/get_commits', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_get_commits_by_user_valid_input(client):
    """Test the get_commits_by_user route with valid input."""
    response = client.post('/get_commits_by_user', json={
        'owner': 'facebook',
        'repo': 'react'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'dates' in data
    assert 'datasets' in data

def test_get_commits_by_user_invalid_input(client):
    """Test the get_commits_by_user route with invalid input."""
    response = client.post('/get_commits_by_user', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data 