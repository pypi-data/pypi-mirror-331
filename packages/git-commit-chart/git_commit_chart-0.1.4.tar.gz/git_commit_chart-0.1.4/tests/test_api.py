import pytest
from unittest.mock import patch
import requests
from git_commit_chart.app import get_commit_history, get_commits_by_user

@patch('git_commit_chart.app.requests.get')
def test_get_commit_history_valid_repo(mock_get):
    """Test getting commit history for a valid repository."""
    # Mock successful API response
    mock_get.return_value.json.return_value = [
        {'commit': {'author': {'date': '2024-02-01T00:00:00Z'}}}
    ]
    mock_get.return_value.raise_for_status.return_value = None

    result = get_commit_history('facebook', 'react')
    assert isinstance(result, dict)
    assert 'dates' in result
    assert 'counts' in result
    assert isinstance(result['dates'], list)
    assert isinstance(result['counts'], list)
    assert len(result['dates']) == len(result['counts'])

def test_get_commit_history_invalid_repo():
    """Test getting commit history for an invalid repository."""
    result = get_commit_history('invalid_user_123456789', 'invalid_repo_123456789')
    assert isinstance(result, dict)
    assert 'error' in result

@patch('git_commit_chart.app.requests.get')
def test_get_commits_by_user_valid_repo(mock_get):
    """Test getting commits by user for a valid repository."""
    # Mock successful API response
    mock_get.return_value.json.return_value = [
        {'commit': {'author': {'date': '2024-02-01T00:00:00Z', 'name': 'test-user'}}}
    ]
    mock_get.return_value.raise_for_status.return_value = None

    result = get_commits_by_user('facebook', 'react')
    assert isinstance(result, dict)
    assert 'dates' in result
    assert 'datasets' in result
    assert isinstance(result['dates'], list)
    assert isinstance(result['datasets'], list)
    for dataset in result['datasets']:
        assert 'user' in dataset
        assert 'commits' in dataset
        assert isinstance(dataset['commits'], list)
        assert len(dataset['commits']) == len(result['dates'])

def test_get_commits_by_user_invalid_repo():
    """Test getting commits by user for an invalid repository."""
    result = get_commits_by_user('invalid_user_123456789', 'invalid_repo_123456789')
    assert isinstance(result, dict)
    assert 'error' in result 