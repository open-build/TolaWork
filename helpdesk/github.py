import requests
import json
from helpdesk.models import Ticket, FollowUp
from django.conf import settings

def get_issue(repo,id):
    repo = repo + "/issues/" + id
    r = requests.get(repo)
    if(r.ok):
        issue = json.loads(r.text or r.content)
    else:
        issue = None

    return issue


def new_issue(repo,ticket):

    payload = {}
    labels = ['Tola-Work Ticket']
    payload['title'] = ticket.title
    payload['body'] = ticket.submitter_email + " " + ticket.ticket_url + " " + ticket.description
    payload['labels'] = labels

    token = settings.GITHUB_AUTH_TOKEN

    repo = repo + "/issues"

    header = {'Authorization': 'token %s' % token}
    r = requests.post(repo,json.dumps(payload),headers=header)

    #Update ticket with new github info if created successfully "201" response
    if int(r.status_code) == 201:
        #print r.content
        data = json.loads(r.content)
        github_issue_url = data['html_url']
        github_issue_number = data['number']
        github_issue_id = data['id']


        update_ticket = Ticket.objects.get(id=ticket.id)
        update_ticket.github_issue_url = github_issue_url
        update_ticket.github_issue_number = github_issue_number
        update_ticket.github_issue_id = github_issue_id
        update_ticket.save()

    return r.status_code


def update_issue(repo,ticket):

    print "Called Update"

    payload = {}
    payload['title'] = ticket.title
    payload['body'] = ticket.description
    payload['labels'] = labels

    token = settings.GITHUB_AUTH_TOKEN
    repo = repo + "/issues/" + ticket.github_issue_number

    header = {'Authorization': 'token %s' % token}
    r = requests.post(repo,json.dumps(payload),headers=header)
    #Update ticket with new github info if created successfully "201" response
    if int(r.status_code) == 201:
        print "201"

        getComments = FollowUp.objects.all().filter(ticket=ticket)
        for comment in getComments:
            comment_status = update_comments(repo, ticket, comment, comment.user.email)

            print comment_status

    return r.status_code


def update_comments(repo, ticket, comment, email):

    payload = {}
    payload['body'] = email + " " + ticket.ticket_url + " " + comment

    token = settings.GITHUB_AUTH_TOKEN

    repo = repo + "/issues/" + ticket.github_issue_number + "/comments"

    header = {'Authorization': 'token %s' % token}
    r = requests.post(repo,json.dumps(payload),headers=header)

    print repo

    print r.status_code

    return r.status_code


def latest_release(repo):

    token = settings.GITHUB_AUTH_TOKEN
    repo = repo + "/releases/latest"
    print repo
    header = {'Authorization': 'token %s' % token}
    r = requests.get(repo,headers=header)
    print r
    if str(r.status_code) == "200":
        content = json.loads(r.text or r.content)
    else:
        content = json.loads(r.text or r.content)
        print content
        print r.status_code
        content = None

    return content