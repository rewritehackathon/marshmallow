import json

from flask import render_template,url_for,flash,redirect,jsonify,request,g,session,current_app
from datetime import datetime
from appFolder import app,db
from flask_login import login_user, current_user, logout_user, login_required
import requests
from time import gmtime, strftime
import boto3
from appFolder.Neighbours import KnnRecommender


@app.route("/",  methods=['GET','POST'])
@app.route("/chat")
def chat():
    return render_template('chat.html', title='home')


@app.route("/chatbot", methods=['GET','POST'])
def chatbot():
    content = request.args.get('feed')
    cur_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    aws_access_key = "AKIAQOO5GPVPAGT76Z7C"
    aws_secret_key = "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"
    lex = boto3.client('lex-runtime', region_name = "us-west-2", aws_access_key_id = aws_access_key, aws_secret_access_key = aws_secret_key)
    lex_response = lex.post_text(botName='Insurance', botAlias = 'insurance', userId = "Suji", inputText = content)
    username = "Chatbot"
    print(lex_response)
    try:
        if 'message' in lex_response:
            msg = lex_response['message']
            feed = '''<article class="media content-section"> <img class="rounded-circle article-img" src="static/profile_pics/default.png"> <div class="media-body"> <div class="article-metadata"> <a class="mr-2" href="#">'''+ username +'''</a> <small class="text-muted">'''+ cur_time +'''</small> </div> <p class="article-content">'''+ msg +'''</p> </div> </article>'''
            return feed
        else:
            print('###########')
            print(lex_response['slots'])
            session['response'] = lex_response['slots']
            msg = "Thank You"
            feed = '''<article class="media content-section"> <img class="rounded-circle article-img" src="static/profile_pics/default.png"> <div class="media-body"> <div class="article-metadata"> <a class="mr-2" href="#">'''+ username +'''</a> <small class="text-muted">'''+ cur_time +'''</small> </div> <p class="article-content">'''+ msg +'''</p> </div> </article>'''
            return feed
    except:
        msg = "Sorry, How may I help you?"
        feed = '''<article class="media content-section"> <img class="rounded-circle article-img" src="static/profile_pics/default.png"> <div class="media-body"> <div class="article-metadata"> <a class="mr-2" href="#">'''+ username +'''</a> <small class="text-muted">'''+ cur_time +'''</small> </div> <p class="article-content">'''+ msg +'''</p> </div> </article>'''
        return feed


@app.route("/getresponse", methods=['GET','POST'])
def getResponse():
    #a = session['response']
    #print(session['response'])
    json_str = '{"Name": "Suji", "business_entity": 3, "company_name": "Zoho", "experience": "8","industry_type": "3", "revenue": "200", "zipcode": "85291","active_owners": "5", "parttime": "4", "fulltime": "200", "payroll": "400","locations": "2"}'
    #json.dumps(session['response'])
    #knn = KnnRecommender("C://Users//Ganesh Kumar//Downloads//study_genie-master//study_genie-master//appFolder//CompaniesandInsurances.csv", json_str)
    knn = KnnRecommender("appFolder/CompaniesandInsurances.csv", json_str)
    result = knn._parse_json()
    print('yayyy!!!')
    r = json.loads(result)
    b = ''
    print('success!!!')
    for key in r.keys():
        for k in r[key].keys():
            if(r[key][k]['price'] != 0.0 and r[key][k]['risk'] != 0.0):
                print(str(k) + ':' + str(r[key][k]))
                b = b + '<li style="margin-left: 20px">' + str(k) + ':' + str(r[key][k]) + '</li>'
    #b = '<dl><dt>value 1</dt><li style="margin-left: 20px">sub 1</li></dl>'
    return b


@app.route("/addFeed", methods=['GET','POST'])
def addFeed():
    cur_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    content = request.args.get('feed')
    username = "User"
    feed = '''<article class="media content-section"> <img class="rounded-circle article-img" src="static/profile_pics/default.png"> <div class="media-body"> <div class="article-metadata"> <a class="mr-2" href="#">'''+ username +'''</a> <small class="text-muted">'''+ cur_time +'''</small> </div> <p class="article-content">'''+ content +'''</p> </div> </article>'''
    return feed
