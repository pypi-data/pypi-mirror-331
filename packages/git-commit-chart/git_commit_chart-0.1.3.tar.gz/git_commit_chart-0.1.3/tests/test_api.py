import pytest
from git_commit_chart.app import get_commit_history, get_commits_by_user

def test_get_commit_history_valid_repo():
    """Test getting commit history for a valid repository."""
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

def test_get_commits_by_user_valid_repo():
    """Test getting commits by user for a valid repository."""
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