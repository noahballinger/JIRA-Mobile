from flask import Flask, render_template
from jira import JIRA

app = Flask(__name__)

tickets= [
    {
        'title':'EPSD-12345',
        'summary':'Adiyogi Test Ticket',
        'description':'Adiyogi is totally awesome'
    },
    {
        'title':'EPSD-67890',
        'summary':'Dhyanalinga Test Ticket',
        'description':'Experience the stillness'
    },
    {
        'title':'EPSD-67890',
        'summary':'Dhyanalinga Test Ticket',
        'description':'Experience the stillness'
    },
    {
        'title':'EPSD-67890',
        'summary':'Dhyanalinga Test Ticket',
        'description':'Experience the stillness'
    },
    {
        'title':'EPSD-67890',
        'summary':'Dhyanalinga Test Ticket',
        'description':'Experience the stillness'
    },
    {
        'title':'EPSD-67890',
        'summary':'Dhyanalinga Test Ticket',
        'description':'Experience the stillness'
    },
    {
        'title':'EPSD-67890',
        'summary':'Dhyanalinga Test Ticket',
        'description':'Experience the stillness'
    },
    {
        'title':'EPSD-67890',
        'summary':'Dhyanalinga Test Ticket',
        'description':'Experience the stillness'
    },

]



@app.route("/")
@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/search")
def search():
    return render_template('search.html', tickets=tickets)

@app.route("/ticket")
def ticket():
    return render_template('ticket.html')

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')