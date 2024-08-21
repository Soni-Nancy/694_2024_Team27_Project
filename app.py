from flask import Flask, request,render_template
from fetch_code import *
from relational_fetch import *



app = Flask(__name__)

# Set the path to the templates folder
templates_path = r"E:\\Downloads\\Twitter-Search-Engine-main sparsh\\Twitter-Search-Engine-main\\templates\\"

@app.route("/home",methods=["GET"])
def home():    
    if request.method == "GET":
        return render_template('homepage.html')

@app.route("/home/searched_results",methods=["POST"])
def searched():
    if request.method=="POST":
        input=request.form["text"]
        if input[0]=='@':
            return GET_USERS(input[1:])
        elif input[0]=='#':
            return GET_HASH(input[1:])
        else:
            return GET_TWEETS(input)
            

@app.route("/home/searched_results/tweet/<id>")
def Quoted(id):
    test=Non_Relational()
    strt=time.time()
    lists=test.get_by_tweet_id(id)
    end=time.time()
    exec=f"{end-strt:.10f}"
    return render_template('tweetpage_(1).html', data = lists[:min(len(lists),50)], range=1 ,time=exec, flag="Database",title = "Main ID",)


@app.route("/home/user_tweets/<id>")
def get_user_tweets(id):
    test=Non_Relational()
    str=time.time()
    lists=test.get_by_user(id)
    end=time.time()
    exec=f"{end-str:.10f}"
    return render_template('tweetpage_(1).html', data = lists,range=len(lists),time=exec, flag="Database",title = "User",)

@app.route("/home/searched_results/retweets_users/<id>")
def get_retweets(id):
    test=Non_Relational()
    strt=time.time()
    lists=test.get_retweets(id)
    end=time.time()
    exec=f"{end-strt:.10f}"
    return render_template('retweetpage_(1).html',data=lists,time=exec,flag="Database",title="Retweet")

@app.route("/home/Top_20_handles")
def top_users():
    test=SearchEngine_postgre()
    strt=time.time()
    l=test.most_popular_users()
    end=time.time()
    exec=f"{end-strt:10f}"
    return render_template('userpage_(1).html', data = l, time=exec, flag="Database",title = "Top Handles",)

@app.route("/home/Top_20_tweets")
def top_tweets():
    test=Non_Relational()
    strt=time.time()
    l=test.top_tweets()
    end=time.time()
    exec=f"{end-strt:10f}"
    return render_template('toptweetspage.html', data = l, range=20,time=exec, flag="Database",title = "Top Tweets",)

def GET_USERS(input):
    test = SearchEngine_postgre()
    str_time = time.time()
    lists = test.search_user(input)
    end_time = time.time()
    exec_time = f"{end_time - str_time:.10f}"
    return render_template('userpage_(1).html', data=lists, time=exec_time, flag="Database", title=input)

def GET_TWEETS(input):
    test = Non_Relational()
    str_time = time.time()
    lists = test.get_tweets(input)
    end_time = time.time()
    exec_time = f"{end_time - str_time:.10f}"
    return render_template('tweetpage_(1).html', data=lists, time=exec_time, range=len(lists), flag="Database", title=input)

def GET_HASH(input):
    test = Non_Relational()
    str_time = time.time()
    lists = test.get_hashtags(input)
    end_time = time.time()
    exec_time = f"{end_time - str_time:.10f}"
    return render_template('hashtagpage_(1).html', data=lists, time=exec_time, range=len(lists), flag="Database", title=input)
    

if __name__=='__main__':
    app.run(debug=True)