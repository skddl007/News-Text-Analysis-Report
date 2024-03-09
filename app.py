from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from newspaper import Article
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import psycopg2
import json
from random import randint
from nltk.corpus import stopwords
from authlib.integrations.flask_client import OAuth
from collections import Counter
import matplotlib.pyplot as plt
from google_auth_oauthlib.flow import Flow
from gevent.pywsgi import WSGIServer
from io import BytesIO
import base64
import requests


def run_flask():
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    http_server.serve_forever()
    

def connect_to_database():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

# Path to the client secrets file
client_secrets_file = "client_secret_143941895939-leieb5islecnelgh4qup9hiel28d8pmc.apps.googleusercontent.com.json"

app = Flask(__name__, static_folder='text project 1/static')
mail = Mail(app)
oauth = OAuth(app)

# Scopes define the level of access you are requesting from the user
scopes = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid']

# Redirect URI for the OAuth flow
redirect_uri = 'http://127.0.0.1:5000/callback'

# Create the OAuth flow object
flow = Flow.from_client_secrets_file(client_secrets_file, scopes=scopes, redirect_uri=redirect_uri)

app.secret_key = 'This is secret'

# github
app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GITHUB_CLIENT_ID'] = "ff2a9c4a4abf7eb1cc8a"
app.config['GITHUB_CLIENT_SECRET'] = "389817d58b1c506cd1684ac45c83ea0a526c89b6"

github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# GitHub admin usernames for verification
github_admin_usernames = ["skddl007", "atmabodha"]

# Password for accessing history
ADMIN_PASSWORD = "Sandeep123"

# OTP generation for email verification
otp = None

# Sender's name for the email
sender_name = "Sandeep Kumar"

# List of admin email addresses
admin_emails = ["su-23036@sitare.org", "saneeipk@gmail.com", "kushal@sitare.org"]

# PostgreSQL database connection details
DB_NAME = "flask_data_g20i"
DB_USER = "sandeep"
DB_PASSWORD = "AEhUuwFOp0jMBchnfdd98U81VU6oSGzE"
DB_HOST = "dpg-cnmb5qen7f5s73d6d8rg-a"

# Flask-Mail configuration
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'saneeipk@gmail.com'  # Update with your Gmail email
app.config['MAIL_PASSWORD'] = 'vtraaffusxqpruyp'  # Update with your Gmail password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Initialize NLTK stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Function to count stop words in text
def count_stop_words(text):
    words = text.split()
    stop_words_count = sum(1 for word in words if word.lower() in stop_words)
    return stop_words_count

def extract_keywords(article_text):
    # Tokenize the text into words
    words = word_tokenize(article_text.lower())

    # Remove stop words
    # stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words and word.isalnum()]

    # Get the frequency distribution of words
    word_freq = Counter(filtered_words)

    # Get the most common words as keywords
    keywords = [word for word, i in word_freq.most_common(10)]

    return keywords

def extract_text_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text, article.title, article.publish_date,
    except Exception as e:
        return str(e), None, None,

def create_table():
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news_data (
                id SERIAL PRIMARY KEY,
                url VARCHAR(255),
                article_name TEXT,
                article_keywords TEXT,
                text TEXT,
                num_sentences INTEGER,
                num_words INTEGER,
                upos_count JSONB,
                stop_words_count INTEGER,
                published_date DATE
            )
        """)
        conn.commit()
    except psycopg2.Error as e:
        print("Error creating table:", e)
    finally:
        if conn:
            conn.close()

# Call create_table function to ensure the table exists
create_table()

def word_count(lst):
    lst1 = ['!',',','.','?','-','"',':',';','/','_','[',']','(',')','{','}','|','@','%','$']
    count = 0
    for i in lst:
        if i not in lst1:
            count += 1
    return count


def save_to_database(url, article_name, article_keywords, text, num_sentences, num_words, upos_count, stop_words_count, published_date):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("INSERT INTO news_data (url, article_name, article_keywords, text, num_sentences, num_words, upos_count, stop_words_count, published_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (url, article_name, json.dumps(article_keywords), text, num_sentences, num_words, json.dumps(upos_count), stop_words_count, published_date))
    conn.commit()
    conn.close()

def get_history_from_database():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT * FROM news_data")
    data = cur.fetchall()
    conn.close()
    return data


@app.route('/')
def index():
    return render_template('index.html')

def generate_plot_and_save(labels, values):
    plt.bar(labels, values, color='red')
    plt.xlabel('Ratios')
    plt.ylabel('Values')
    plt.title('Parts of Speech Ratios')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()  # Close the plot to prevent interference with subsequent plots
    buffer.seek(0)

    # Encode the bytes buffer as a base64 string
    graph_data = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return graph_data


@app.route('/submit', methods=['POST'])
def submit():
    url = request.form['url']
    try:
        article_text, article_title, published_date = extract_text_from_url(url)

        num_sentences = len(sent_tokenize(article_text))
        words = word_tokenize(article_text)
        num_words = word_count(words)
        upos_tags = nltk.pos_tag(word_tokenize(article_text), tagset='universal')

        upos_count = {}
        for word, pos in upos_tags:
            if pos in upos_count:
                upos_count[pos] += 1
            else:
                upos_count[pos] = 1

        stop_words_count = count_stop_words(article_text)
        article_keywords = extract_keywords(article_text)

        if upos_count.get('PRON', 0) == 0:
            adjective_pronoun_ratio = upos_count.get('ADJ', 0) / 1
        else:
            adjective_pronoun_ratio = upos_count.get('ADJ', 0) / upos_count['PRON']

        if upos_count.get('ADJ', 0) == 0:
            adverb_adjective_ratio = upos_count.get('ADV', 0) / 1
        else:
            adverb_adjective_ratio = upos_count.get('ADV', 0) / (upos_count['ADJ'] + 1)
        
        if adjective_pronoun_ratio > adverb_adjective_ratio:
            writing_style = "Descriptive writing style that focuses on providing information about objects, people, and concepts."
        elif adverb_adjective_ratio > adjective_pronoun_ratio:
            writing_style = "Expressive and nuanced writing style that explores contributing to the depth and complexity of narrative."
        else:
            writing_style = "The text does not exhibit a clear dominant writing style based on the provided ratios."

        graph_data = generate_plot_and_save(['Adjective/Pronoun', 'Adverb/Adjective'],
                                            [adjective_pronoun_ratio, adverb_adjective_ratio])

        save_to_database(url, article_title, article_keywords, article_text, num_sentences, num_words, upos_count, stop_words_count, published_date)
        
        return render_template('dashboard.html', num_sentences=num_sentences, num_words=num_words,
                                   upos_count=upos_count, stop_words_count=stop_words_count,
                                   article_keywords=article_keywords, article_text=article_text,
                                   article_title=article_title, published_date=published_date,
                                   writing_style=writing_style, image_url=graph_data)
    except Exception as e:
        return str(e)

    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('history'))
        else:
            return "Invalid password. Please try again."
    return render_template('index.html')

@app.route('/otp_login', methods=['GET', 'POST'])
def otp_login():
    if request.method == 'POST':
        global otp
        user_otp = request.form['otp']
        email = session.get('email')
        if otp and otp == int(user_otp) and email in admin_emails:
            session['logged_in'] = True
            return redirect(url_for('history'))
        else:
            return "You are not admin."
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/history')
def history():
    if 'logged_in' in session:
        data = get_history_from_database()
        return render_template('history.html', data=data, logged_in=True)
    else:
        return redirect(url_for('login'))

@app.route('/send_otp', methods=["POST"])
def send_otp():
    global otp
    email = request.form['email']
    otp = randint(100000, 999999)
    msg = Message(subject='OTP', sender=('Sandeep Kumar', app.config["MAIL_USERNAME"]), recipients=[email])
    msg.body = f'Your OTP is: {otp}'
    try:
        mail.send(msg)
        session['email'] = email
        return render_template('index.html', otp_sent=True)
    except Exception as e:
        return str(e)
    
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    try:
        github = oauth.create_client('github')
        token = github.authorize_access_token()
        session['github_token'] = token
        resp = github.get('user').json()
        print(f"\n{resp}\n")
        # print(type(repr))
        # data=get_history_from_database()
        # return render_template("history.html",data=data)
        logged_in_username = resp.get('login')
        if logged_in_username in github_admin_usernames:
            data = get_history_from_database()
            return render_template("history.html", data=data)
        else:
            return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))

    
# Logout route for GitHub
@app.route('/logout/github')
def github_logout():
    session.clear()
    # session.pop('github_token', None)()
    print("logout")
    # return redirect(url_for('index'))
    return redirect(url_for('index'))


# To Google login
@app.route('/index')
def google():
    if 'google_token' in session:
        # User is already authenticated, redirect to a protected route
        return redirect(url_for('protected'))
    else:
        # User is not authenticated, render the ggl.html template
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return redirect(authorization_url)
# Callback route for handling OAuth response
@app.route('/callback')
def callback():
    # Handle the callback from the Google OAuth flow
    flow.fetch_token(code=request.args.get('code'))
    session['google_token'] = flow.credentials.token

    # Redirect to the protected route or another page
    return redirect(url_for('protected'))

# Protected route accessible only to authenticated users

@app.route('/protected')
def protected():
    if 'google_token' in session:
        # User is authenticated
        # Get the user's email from the Google API
        userinfo = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': f'Bearer {session["google_token"]}'})
        email = userinfo.json().get('email')

        # Check if the user's email is in the allowed list
        if email in admin_emails:
            data = get_history_from_database()
            return render_template("history.html", data=data)
        else:
            # User is not authorize
            return redirect(url_for('index'))
    else:
        # User is not authenticated
        return redirect(url_for('index'))


if __name__ == '__main__':
    run_flask()

