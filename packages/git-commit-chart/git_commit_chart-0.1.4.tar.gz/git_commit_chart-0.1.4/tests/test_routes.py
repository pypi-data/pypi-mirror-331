import pytest
from unittest.mock import patch
from git_commit_chart.app import app
import requests

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

@patch('git_commit_chart.app.requests.get')
def test_get_commits_valid_input(mock_get, client):
    """Test the get_commits route with valid input."""
    # Mock successful API response
    mock_get.return_value.json.return_value = [
        {'commit': {'author': {'date': '2024-02-01T00:00:00Z'}}}
    ]
    mock_get.return_value.raise_for_status.return_value = None

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

@patch('git_commit_chart.app.requests.get')
def test_get_commits_by_user_valid_input(mock_get, client):
    """Test the get_commits_by_user route with valid input."""
    # Mock successful API response
    mock_get.return_value.json.return_value = [
        {'commit': {'author': {'date': '2024-02-01T00:00:00Z', 'name': 'test-user'}}}
    ]
    mock_get.return_value.raise_for_status.return_value = None

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

@patch('git_commit_chart.app.requests.get')
def test_get_commits_rate_limit(mock_get, client):
    """Test handling of GitHub API rate limit errors."""
    # Mock rate limit error response
    class MockResponse:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError('403 Client Error: rate limit exceeded')
    mock_get.return_value = MockResponse()

    response = client.post('/get_commits', json={
        'owner': 'facebook',
        'repo': 'react'
    })
    assert response.status_code == 403
    data = response.get_json()
    assert 'error' in data 