from flask import Flask, render_template, url_for, request, session, jsonify
from flask_session import Session
import flask
import sys
import json
import boto3
import quickstart
import os
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import base64
import decimal
from boto3.dynamodb.conditions import Key, Attr
from ML_Vision_NLP import getEventFromImage
from ML_Vision_NLP import parseImage

AWS_KEY = 'AKIAI4O2XF25JG6TC5UQ'
AWS_SECRET = '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'
REGION = 'us-east-1'

dynamodb = boto3.resource('dynamodb',aws_access_key_id=AWS_KEY,aws_secret_access_key=AWS_SECRET,region_name=REGION)
table = dynamodb.Table('Test')

CLIENT_SECRETS_FILE = "client_secret_Calendar.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

app = flask.Flask( __name__,static_url_path="/static" )
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

def readAll():

    print("All events:")

    response = table.scan(
        TableName= 'Test'
        )

    dict = {'key': {'location': 'madison'}}
    for i in response['Items']:
        print(i['Key'], ":", i['desc'])
        dict.update({i['Key']: {'desc': i['desc'], 'date-time': i['date-time'], 'location': i['location']}})

    return dict


@app.route("/")
def index():
    response = table.scan()
    dict = readAll()
    return render_template("index.html", data= dict, api_data=dict, event_data=response)


@app.route('/post_video', methods = ['GET', 'POST'])
def post_video():
    jsdata = request.form['picPath']
    if (jsdata):
        stuff = jsdata.split(",")[1]
        image = base64.b64decode(stuff + "====")
        event_dict = getEventFromImage(image)
        for item in event_dict.items():
            print(item)

        if "name" in event_dict:
            name = event_dict["name"]
        else:
            name = "n/a"

        if "location" in event_dict:
            location = event_dict["location"]
        else:
            location = "n/a"

        if "date-time" in event_dict:
            date_time = event_dict["date-time"]
        else:
            date_time = "n/a"

        if "description" in event_dict:
            desc = event_dict["description"]
        else:
            desc = "n/a"

        return render_template("manual_entry.html",
            event_name=name,
            event_description=desc,
            event_location=location,
            event_date_time=date_time)

    else:
        response = table.scan()
        dict = readAll()
        return render_template("index.html", data= dict, api_data=dict, event_data=response)

@app.route("/video", methods=["GET", "POST"])
def video():
    return render_template("video.html")

@app.route("/submit", methods=["POST"])
def post_to_db():
    response = table.put_item(
       Item={
            "Key": request.form['name'],  # Key = Event Name
            'location': request.form['location'],
            'date-time': request.form['date-time'],
            'desc': request.form['description']
        }
    )
    print("Posted to DB")
    response = table.scan()
    dict = readAll()
    return render_template("index.html", data= dict, api_data=dict, event_data=response)

@app.route("/manual_entry", methods=["GET", "POST"])
def to_manual():
    return render_template("manual_entry.html")

@app.route("/photo_entry", methods=["GET", "POST"])
def to_photo():
    return render_template("photo_entry.html")

@app.route("/manual_find", methods=["GET", "POST"])
def to_manual_find():
    return render_template("manual_find.html")

@app.route("/photo_find", methods=["GET", "POST"])
def to_photo_find():
    return render_template("photo_find.html")

@app.route("/manual_entry/photo", methods=["GET", "POST"])
def photo_to_manual():
    image = request.files['photo'].read()
    event_dict = getEventFromImage(image)

    for item in event_dict.items():
        print(item)

    if "name" in event_dict:
        name = event_dict["name"]
    else:
        name = "n/a"

    if "location" in event_dict:
        location = event_dict["location"]
    else:
        location = "n/a"

    if "date-time" in event_dict:
        date_time = event_dict["date-time"]
    else:
        date_time = "n/a"

    if "description" in event_dict:
        desc = event_dict["description"]
    else:
        desc = "n/a"

    return render_template("manual_entry.html",
        event_name=name,
        event_description=desc,
        event_location=location,
        event_date_time=date_time)

@app.route("/manual_find/photo", methods=["GET", "POST"])
def photo_to_manual_find():
    image = request.files['photo'].read()
    event_dict = getEventFromImage(image)

    for item in event_dict.items():
        print(item)

    if "name" in event_dict:
        name = event_dict["name"]
    else:
        name = "n/a"

    if "location" in event_dict:
        location = event_dict["location"]
    else:
        location = "n/a"

    if "date-time" in event_dict:
        date_time = event_dict["date-time"]
    else:
        date_time = "n/a"

    if "description" in event_dict:
        desc = event_dict["description"]
    else:
        desc = "n/a"

    for key in quickstart.m:
        if key in date_time:
            month = quickstart.month_string_to_number(key)

    for i in quickstart.d:
        if i in date_time:
            day = i
        else:
            day = '01'

    formatted_date_time = '2019' + month + day

    return render_template("manual_find.html",
        event_name=name,
        event_description=desc,
        event_location=location,
        event_date_time=date_time)

@app.route("/search", methods=["GET", "POST"])
def find_in_db():
    # PUT CODE HERE FOR FINDING IN DATABASE
    print("************")
    print("find_in_db()")
    print("************")
    response = table.scan()
    dict = readAll()
    return render_template("index.html", event_data=response, data=dict)

@app.route('/clear', methods=["GET", "POST"])
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          quickstart.print_index_table())

@app.route('/test', methods=["GET", "POST"])
def test_api_request():
 # revoke()
  #clear_credentials()
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  event = {
    'summary': request.form['name'],
    'location': request.form["location"],
    'description': request.form['description'],
    'start': {
      'date': '2019-05-28',
    },
    'end': {
      'date': '2019-05-28',
    },
  }

  event = service.events().insert(calendarId='primary', body=event).execute()
  '''
  events_result = service.events().list(calendarId='primary',
                                            maxResults=1, singleEvents=True,
                                            orderBy='startTime').execute()
  '''
  #files = drive.files().list().execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = quickstart.credentials_to_dict(credentials)

  response = table.put_item(
     Item={
          "Key": request.form['name'],  # Key = Event Name
          'location': request.form['location'],
          'date-time': request.form['date-time'],
          'desc': request.form['description']
      }
  )

  response = table.scan()
  dict = readAll()
  return render_template("index.html", event_data=response, data=dict)


@app.route('/authorize', methods=["GET", "POST"])
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback', methods=["GET", "POST"])
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = quickstart.credentials_to_dict(credentials)

  dict = readAll()
  response = table.scan()
  return flask.render_template("index.html",data=dict,event_data=response)


@app.route('/revoke', methods=["GET", "POST"])
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + quickstart.print_index_table())
  else:
    return('An error occurred.' + quickstart.print_index_table())

if __name__ == ' __main__':
    #app.debug = True
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run(host='0.0.0.0',port=178)
