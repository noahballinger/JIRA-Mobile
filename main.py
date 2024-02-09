from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
from jiraService import JIRAService
import datetime
from dateParser import parse_date
from commentParser import extract_attachment_references, clean_comment


app = Flask(__name__)
app.secret_key = os.urandom(24)  # set a secret key for sessions

@app.route("/", methods=('GET', 'POST'))
@app.route("/login", methods=('GET', 'POST'))
def login():
    

    return render_template('login.html')

@app.route("/auth", methods=('GET', 'POST'))

def auth():
    try:
        session["username"] = request.form.get("usern")
        session["password"] = request.form.get("passw")
        
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=30)



        return redirect('/dashboard')

        

    
    except:

        return redirect("/login")
    
@app.route("/logout", methods=('GET', 'POST'))

def logout():
    session.clear()
    return redirect("/login")

    
@app.route("/jql", methods=["GET", "POST"])
def jql():
    jql = request.form.get("jql")

    if jql == "":
        print('No JQL')
    else:
        session["jql"] = jql
    return redirect("/search")

@app.route("/comment", methods=["GET", "POST"])
def comment():
    username = session.get("username")
    password = session.get("password")
    issue = session.get('issue_key')
    comment = request.form.get("comment")

    jira= JIRAService(username, password, "https://servicedesk.isha.in")

    jira.makeComment(issue, comment)
    
    print(comment)

    return redirect('/ocd')
    
    



@app.route("/search")
def search():
    try:
        username = session.get("username")
        password = session.get("password")
        jql = session.get("jql")

        jira= JIRAService(username, password, "https://servicedesk.isha.in")

        print(jql)
        
        # if jira.get_issues_from_jql sends an empty request, it will return all tickets. This prevents that from showing
        # Not sure this is the best logic buy it works.


        if jql == None:
            tickets = []
    

        else:
            try:
                #for a succesful api request
                tickets = jira.get_issues_from_jql(jql)

#### This section is under construction
                
                # for ticket in tickets:
                #     sm_page = jira.get_sm_page(ticket['issue_key'])
                #     platform = jira.get_platform(ticket['issue_key'])

                #     if sm_page == 'Adiyogi':
                #         ticket['sm_icon'] = '/static/assets/icons/adiyogi.webp' # insert filepath here

                #     # ticket['platform_icon'] = 'filepath' # insert filepath here


                #     # print(sm_page)
                #     # print(platform)
                #     print(tickets)

            except:
                try:
                    #if api request fails, checks if user is logged in. If they are, it assumes the jql had incorrect formatting. 
                    jira.get_issue('OCD-203')
                    tickets=[]

                except:
                    return redirect("/login")
    except:
        return redirect("/login")
        
        
        
    # jql= 'assignee =' + username + ' AND type != "Imp New Content" AND type != "Imp Proofing" AND status not in ("text delivered", closed, Canceled, cancelled, DONE, Resolved, "Pending Requester Review", "EngPub Review", "Pending Requester Clarification", "W/Cust-Clar (Text)", "W/Cust-Review (Text)", "Text Under Review")'

        


    return render_template('search.html', tickets=tickets, last_jql=jql)

# This gets the issue key and routes it to appropriate ticket page type
@app.route("/search/<issue_key>")
def issue_routing(issue_key):
    session["issue_key"] = issue_key
    
    if "OCD" in issue_key:
        return redirect("/ocd")
    
    if "EPSD" in issue_key:
        return redirect('/ocd')
    else:
        return redirect("/default")

    
# This route only exists for the navbar- it routes to the ticket saved in state
@app.route("/ticket")
def ticket():
    issue_key = session.get("issue_key")
    try:
        ## From here on should be the same as the issue_routing function above
        if "OCD" in issue_key:
            return redirect("/ocd")
        else:
            return redirect("/default")
    except:
        return redirect('/search')


### these are the various pages for ticket types
@app.route("/default")
def default():
    try:
        username = session.get("username")
        password = session.get("password")
        issue_key = session.get("issue_key")


        jira= JIRAService(username, password, "https://servicedesk.isha.in")
            
        issue= jira.get_issue(issue_key)

        # Get all fields
        all_fields = jira.get_all_fields()
        
        field_map = {field['id']: field['name'] for field in all_fields}

        fields = {}

        # Replace field keys with their corresponding names
        for field_id in issue.raw['fields']:
            field_name = field_map.get(field_id, field_id)
            field_val = issue.raw['fields'][field_id]
            
            if field_val is not None and field_val != "Unresolved" and field_val != 0.0:
                fields[field_name] = field_val
        return render_template('default.html', username=username, fields=fields)
    except:
        return redirect('/search')
    
@app.route("/ocd")
def ocd():
    try:
        username = session.get("username")
        password = session.get("password")
        issue_key = session.get("issue_key")


        jira= JIRAService(username, password, "https://servicedesk.isha.in")
            
        issue= jira.get_issue(issue_key)

        # Get all fields
        all_fields = jira.get_all_fields()
        
        field_map = {field['id']: field['name'] for field in all_fields}

        fields = {}

        # Replace field keys with their corresponding names
        for field_id in issue.raw['fields']:
            field_name = field_map.get(field_id, field_id)
            field_val = issue.raw['fields'][field_id]
            
            if field_val is not None and field_val != "Unresolved" and field_val != 0.0:
                fields[field_name] = field_val

# Transitions and workflow
                
        transitions = jira.get_transitions(issue_key)


        # print(transitions)

## gets list of attachments (used later in comments)
        
        attachments = jira.attachments(issue_key)



### Comments
        comments_info = []

        comments = jira.get_comments(issue_key)
        for comment in comments:
            author = comment.author
            date = comment.created
            body = comment.body

            #searches for referenced attachments and downloads them.

            referenced_attachments = extract_attachment_references(body)
            download_dict = {k: attachments[k] for k in referenced_attachments if k in attachments}
            downloads = [value for value in download_dict.values()]
            filepaths = []

            for download in downloads:
                filepath = jira.download_attachment(download)
                filepaths.append(filepath)
            

            comment_info = {
                'author': author,
                'date': parse_date(date),
                'body': clean_comment(body),
                'attachments': filepaths
            }
            comments_info.append(comment_info)

        comments_info.reverse()


            
        return render_template('ocd.html', username=username, fields=fields, comments=comments_info, transitions=transitions, issue_key=issue_key)
    
    except:
        return redirect('/search')
    
   




@app.route("/transition/<id>")
def transition(id):
    transition = id
    username = session.get("username")
    password = session.get("password")
    issue_key = session.get("issue_key")


    jira= JIRAService(username, password, "https://servicedesk.isha.in")

    jira.transition_issue(issue_key, transition)
    return redirect('/ticket')
        
    

        

@app.route("/settings")
def settings():
    username = session.get("username")
    password = session.get("password")
    
    if username:
        return render_template('settings.html', user=username)
    else:
        return redirect('/login')

@app.route("/dashboard")
def dashboard():
    try:
        username = session.get("username")
        password = session.get("password")

        jira= JIRAService(username, password, "https://servicedesk.isha.in")
        
        jql= 'assignee =' + username + ' AND type != "Imp New Content" AND type != "Imp Proofing" AND status not in ("text delivered", closed, Canceled, cancelled, DONE, Resolved, "Pending Requester Review", "EngPub Review", "Pending Requester Clarification", "W/Cust-Clar (Text)", "W/Cust-Review (Text)", "Text Under Review")'
        
        tickets = jira.get_issues_from_jql(jql)

    except:
        return redirect("/login")
        
    return render_template('dashboard.html', tickets=tickets, last_jql=jql, username=username)