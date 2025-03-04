from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import os
import click

app = Flask(__name__)

# Default repository settings
DEFAULT_OWNER = "kubecost"
DEFAULT_REPO = "cost-analyzer-helm-chart"

def get_commit_history(owner=DEFAULT_OWNER, repo=DEFAULT_REPO):
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    
    # Get commits from the last 30 days
    since = datetime.now() - timedelta(days=30)
    params = {
        'since': since.isoformat(),
        'per_page': 100
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        commits = response.json()
        
        # Process commits by date
        commit_counts = defaultdict(int)
        for commit in commits:
            date = commit['commit']['author']['date'][:10]  # Get just the date part
            commit_counts[date] += 1
        
        # Sort by date
        dates = sorted(commit_counts.keys())
        counts = [commit_counts[date] for date in dates]
        
        return {'dates': dates, 'counts': counts}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_commits_by_user(owner=DEFAULT_OWNER, repo=DEFAULT_REPO):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    since = datetime.now() - timedelta(days=30)
    params = {
        'since': since.isoformat(),
        'per_page': 100
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        commits = response.json()
        
        # Process commits by date and user
        commit_data = defaultdict(lambda: defaultdict(int))
        users = set()
        dates = set()
        
        for commit in commits:
            date = commit['commit']['author']['date'][:10]
            user = commit['commit']['author']['name']
            commit_data[date][user] += 1
            users.add(user)
            dates.add(date)
        
        # Sort dates and users
        sorted_dates = sorted(dates)
        sorted_users = sorted(users)
        
        # Create datasets for each user
        datasets = []
        for user in sorted_users:
            user_commits = [commit_data[date][user] for date in sorted_dates]
            datasets.append({
                'user': user,
                'commits': user_commits
            })
        
        return {
            'dates': sorted_dates,
            'datasets': datasets
        }
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html', default_owner=DEFAULT_OWNER, default_repo=DEFAULT_REPO)

@app.route('/by-user')
def by_user():
    return render_template('by_user.html', default_owner=DEFAULT_OWNER, default_repo=DEFAULT_REPO)

@app.route('/get_commits', methods=['POST'])
def get_commits():
    data = request.json
    owner = data.get('owner', DEFAULT_OWNER)
    repo = data.get('repo', DEFAULT_REPO)
    
    if not owner or not repo:
        return jsonify({'error': 'Owner and repository name are required'}), 400
    
    commit_data = get_commit_history(owner, repo)
    return jsonify(commit_data)

@app.route('/get_commits_by_user', methods=['POST'])
def get_commits_by_user_route():
    data = request.json
    owner = data.get('owner', DEFAULT_OWNER)
    repo = data.get('repo', DEFAULT_REPO)
    
    if not owner or not repo:
        return jsonify({'error': 'Owner and repository name are required'}), 400
    
    commit_data = get_commits_by_user(owner, repo)
    return jsonify(commit_data)

@click.command()
@click.option('--port', default=5000, help='Port to run the application on')
@click.option('--host', default='127.0.0.1', help='Host to run the application on')
@click.option('--production/--development', default=False, help='Run in production mode')
def main(port, host, production):
    """Run the Git Commit Chart application."""
    if production:
        from waitress import serve
        click.echo(f"Running in production mode on http://{host}:{port}")
        serve(app, host=host, port=port)
    else:
        click.echo(f"Running in development mode on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    main() 