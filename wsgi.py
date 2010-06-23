from dolt.apis.github import GitHub
import jinja2
import json
import os
import re

BASE_PATH = os.path.dirname(__file__)
CONFIG = json.load(open(os.path.join(BASE_PATH, "config.json")))

templates = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.join(BASE_PATH, 'templates')
))

def grab_open_issues():
    gh = GitHub()
    return getattr(getattr(gh.issues.list, CONFIG['github_user']), CONFIG['github_repo']).open()

def display_github_issues(environ, start_response):
    template = templates.get_template("pivotal.xml")
    start_response(200, [('Content-Type', 'application/xml')])
    return [template.render({"issues": grab_open_issues()['issues']})]


CHECK_FOR_GITHUB_REGEX = re.compile("<other_url>http://github.com/%s/%s/issues/\d+</other_url>" % (
    CONFIG['github_user'], CONFIG['github_repo']))
OTHER_ID_REGEX = re.compile("<other_id>(\d+)</other_id>")
EVENT_TYPE_REGEX = re.compile("<event_type>([^<]+)</event_type>")
UPDATE_TYPE_REGEX = re.compile("<current_state>([^<]+)</current_state>")

def do_issue_label(issue_id, label, action):
    gh = GitHub()
    req = getattr(getattr(getattr(getattr(getattr(
            gh.issues.label,
            action),
            CONFIG['github_user']),
            CONFIG['github_repo']),
            label),
            issue_id)
    return req.POST(login=CONFIG['github_user'], token=CONFIG['github_apikey'])

def add_label(issue_id, label):
    return do_issue_label(issue_id, label, 'add')

def remove_label(issue_id, label):
    return do_issue_label(issue_id, label, 'remove')

def get_issue(id):
    return getattr(getattr(getattr(
        GitHub().issues.show,
        CONFIG['github_user']),
        CONFIG['github_repo']),
        id
    )()['issue']

def do_issue(id, type):
    return getattr(getattr(getattr(getattr(
        GitHub().issues,
        type),
        CONFIG['github_user']),
        CONFIG['github_repo']),
	id).POST(login=CONFIG['github_user'], token=CONFIG['github_apikey'])

def reopen_issue(id):
    return do_issue(id, 'reopen')

def close_issue(id):
    return do_issue(id, 'close')

def update_github(environ, start_response):
    pivotal = environ['wsgi.input'].tmp.read()
    matches = OTHER_ID_REGEX.search(pivotal).groups()
    on_github = CHECK_FOR_GITHUB_REGEX.search(pivotal) != None
    if len(matches) != 1 or not on_github:
        start_response(404, [])
        return []

    issue_id = matches[0]
    event_type = EVENT_TYPE_REGEX.search(pivotal).groups()[0]

    if event_type == "story_create":
        add_label(issue_id, 'accepted')

    if event_type == "story_update":
        current_state = UPDATE_TYPE_REGEX.search(pivotal).groups()[0]
        if current_state == "finished":
            add_label(issue_id, "finished")
        elif current_state == "accepted":
            close_issue(issue_id)
        elif current_state == "delivered":
            pass # do not thing for now
        else:
            issue = get_issue(issue_id)
            if "finished" in issue['labels']:
                remove_label(issue_id, "finished")
            if issue['state'] == "closed":
                reopen_issue(issue_id)

    start_response(202, [])
    return []

def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        return update_github(environ, start_response)
    else:
        return display_github_issues(environ, start_response)

