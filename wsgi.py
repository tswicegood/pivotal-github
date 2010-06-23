from dolt.apis.github import GitHub
import jinja2
import json
import yajl
import os

BASE_PATH = os.path.dirname(__file__)
CONFIG = json.load(open(os.path.join(BASE_PATH, "config.json")))

templates = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.join(BASE_PATH, 'templates')
))

def grab_open_issues():
    gh = GitHub()
    return getattr(getattr(gh.issues.list, CONFIG['github_user']), CONFIG['github_repo']).open()

def application(environ, start_response):
    template = templates.get_template("pivotal.xml")
    start_response(200, [('Content-Type', 'application/xml')])
    return [template.render(**grab_open_issues())]


