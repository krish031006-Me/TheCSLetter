""" The purpose of this file is to fetch data from various sites such as-
    Wikipedia - to get the intro or defination about the topic.
    Geeks for geeks and The Medium for the rest of the resources such as articles and all but we are going to use RSS feeds for this."""

# importing the libraries-
import requests
import os
import feedparser
from cs50 import SQL
from topics import categories
from datetime import datetime
from copy import deepcopy
import random
from emoji import emojize
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
from urllib.parse import quote # this module is to let special characters escape    
# for email sending 
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# setting for consistent results
DetectorFactory.seed = 0

# global email and password for the email using environment variables 
senderEmail = os.environ.get("NEWSLETTER_EMAIL")
password = os.environ.get("APP_PASSWORD")

# function inside of which the newsletter would be created
def newsletter(user_id):
    print(f"The letter this time is called by {user_id}") # this line is for a bit of error checking using terminal
    
    # initialising the database
    db = SQL("sqlite:///users.db")

    # getting the categories choosen by the user
    choosen = db.execute("SELECT categories FROM users WHERE id = ?", user_id)
    if not choosen: # if choosen is empty
        return None
    # if the user is subscribed or has choosen categories
    else:
        # calling a function to have a topic choosen to create the newsletter on-
        try:
            topic, category, sub_topics = topic_chooser(choosen, user_id, db)
            print(topic)
        except TypeError: # if topic_chooser returns None
            print("Topic_chooser is returning None")
            return None
        
        # initialising content variables
        contentGfg = None
        contentMedium = None
        contentDev = None

        # the urls for the medium and Dev.to
        urlMedium = f"https://medium.com/feed/tag/{quote(topic.replace(' ', '-'))}"
        urlDev = f"https://dev.to/feed/tag/{quote(topic.replace(' ', '').lower())}"

        # calling their specific functions
        articleMedium = helperFeed(urlMedium, topic, category, db, user_id, sub_topics, attempt = 0, MAX = 3)
        articleDev = helperFeed(urlDev, topic, category, db, user_id, sub_topics, attempt = 0, MAX = 3)
        
        # calling the wikipedia function
        page = wiki(topic)
        # a bit of error checking-
        title = page['title'] if page else "Title not available."
        summary = page['summary'] if page else "Summary not available."

        # calling prepare for diff articles
        if articleMedium:
            contentMedium = prepare(articleMedium)
        if articleDev:
            contentDev = prepare(articleDev)

        # creating the final draft and then returning it
        # my custom message
        wink, smile= emojize(":winking_face:"), emojize(":smiling_face_with_smiling_eyes:") # the emojis 
        start_msg = f"Howdy fellow coder, Here is another newsletter on {topic} <br> Hope you like it!!{smile}"
        end_msg = f"So this was it for today see you next time at the frequency you choose{wink}"
        today = (datetime.today().strftime("%Y-%m-%d %H:%M:%S")) # today's date

        # gradually adding content to the para
        format_para = f"""
            {title}
            </p>{today}</p>
            <p>{start_msg}</p>
            {summary}          
        """
        if contentGfg:
            format_para += f"""
                <h3>{contentGfg["article_title"]}</h3>
                <p>{contentGfg["para"]}</p>
                <p>you can read the actual article from <span><a href = '{contentGfg["article_link"]}'>here.</a></span></p>
            """
        if contentDev:
            format_para += f"""
            <h3>{contentDev["article_title"]}</h3>
            <p>{contentDev["para"]}</p>
            <p>you can read the actual article from <span><a href = '{contentDev["article_link"]}'>here.</a></span></p>
        """
        if contentMedium:
            format_para += f"""
            <h3>{contentMedium["article_title"]}</h3>
            <p>{contentMedium["para"]}</p>
            <p>you can read the actual article from <span><a href = '{contentMedium["article_link"]}'>here.</a></span></p>
        """
        
        # adding the endmsg
        format_para += f"<p>{end_msg}</p>"

        # Calling the sendEmail function
        email, status = sendEmail(title, format_para, user_id, db)
        # only inserting in table when status was returned True i.e email was sent
        if status == True: 
            # Updating the database-
            count = db.execute("SELECT COUNT(*) AS count FROM recepient WHERE recepient_id = ?", user_id)
            length = count[0]["count"]
            db.execute("INSERT INTO recepient (recepient_id, email_id, email) VALUES(?, ?, ?)", user_id, length + 1, email)
        else: # email not sent for some reason
            return None
        
        return {
            "para": format_para,
            "title": title,
        }

# function to choose the topic for today
def topic_chooser(choosen, user_id, db):
    ''' sorting out the fields choosen by the user'''
    # creating a deepcopy of fields
    fields = deepcopy(categories)
    # getting the keys of the list
    keys = [list(row.keys())[0] for row in categories]
    # the categories to remove i.e those that aren't selected by the user
    to_remove = [element for element in keys if element not in choosen[0]["categories"]]
    # removing those fields
    for row in fields[:]: # here we are iterating over a shallow copy of fields and removing from the original one
        if list(row.keys())[0] in to_remove:
            fields.remove(row)
        else:
            pass

    # getting today's day in numeric
    today = datetime.today() # instance of today 
    weekday = today.weekday() # the weekday

    # fetching details from topics_covered to make sure do we have a categories selected for this week
    details = db.execute("SELECT status, for_week, topics_covered FROM topics_covered WHERE id = ?", user_id) 
    if not details: # if user has it's first letter 
        db.execute("INSERT INTO topics_covered (id, status, for_week, topics_covered, links) VALUES (?, 'pending', NULL, NULL, NULL)", user_id)
        status, for_week, sent = 'pending', None, None
    else:
        status, for_week, sent = details[0]["status"], details[0]["for_week"], details[0]["topics_covered"]
    
    # calling choose_category making sure we have categories for this week
    if for_week != None and status == 'done':
        for_week = for_week.split(',')
        selected = [element.strip() for element in for_week]
    elif status == 'pending' and for_week == None:
        selected = choose_category(fields)
        db.execute("UPDATE topics_covered SET status = 'done', for_week = ? WHERE id = ?", ','.join(selected), user_id)
    else:
        selected = choose_category(fields)
        # updating the categories and status
        db.execute("UPDATE topics_covered SET status = 'done', for_week = ? WHERE id = ?", ','.join(selected), user_id)

    # getting the name of that category
    if weekday >= len(selected):
        category_name = selected[-1]
    else:
        category_name = selected[weekday]

    # storing the sub-topics 
    for row in fields:
        if list(row.keys())[0] == category_name:
            sub_topics = [element for element in row[category_name]]
            length = len(sub_topics)    

    # sorting out categories and getting the actual sub topics-
    if not sent:
        sent = []
    else:
        sent = [s.strip() for s in sent.split(',')]
    already = [] # empty list 
    for element in sent:
        try:
            result = element.split(":")[1].strip()
            already.append(result)
        except IndexError:
            return None 
        
    # getting the topics to be actually sent-
    if length == 0:
        return None

    # reset if all topics are used inside 
    if len(already) == length:
        db.execute("UPDATE topics_covered SET topics_covered = NULL WHERE id = ?", user_id)
        already = []

    remaining = [t for t in sub_topics if t not in already] # topics that haven't been sent yet
    if not remaining:
        return None
    # choosing one out of them
    topic = random.choice(remaining)

    # storing the topic to keep a track of all the things that have been sent
    store_format = f"{category_name}: {topic}"
    db.execute("""UPDATE topics_covered SET topics_covered = 
               CASE
                    WHEN topics_covered IS NULL OR topics_covered = '' THEN ?
               ELSE
                    topics_covered || ',' || ?
               END WHERE id = ?""", store_format, store_format, user_id)
    if all(x is not None for x in (topic, category_name, sub_topics)):
        return topic, category_name, sub_topics
    else:
        return None

# this is the function to get all the intro  content for the newsletter using wikipedia API 
def wiki(topic):
    # error checking
    if topic == None:
        return
    
    # shaping topics for the queries
    topic = topic.lower().replace(" ", "_")
    # the url with topic  
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"

    '''THis below is a header whose purpose is to store the meta data sent to the server during an API call'''
    headers = {
        "User-Agent": "MyNewsletterBot/1.0 (https://yourdomain.com/contact)"
    }

    # using the actual API
    response = requests.get(url, headers=headers)

    # a bit of error checking
    if response.status_code != 200:
        print(f"Failed to fetch: {response.status_code}")
        return None
    
    # converting data recieved into json
    try:
        data = response.json()
    except ValueError:
        print("Invalid JSON received")
        return None

    # Handle cases like disambiguation or missing page
    if "extract" not in data:
        print(f"No summary available for: {topic}")
        return {
            "title": data.get("title", topic),
            "summary": "Summary not available."
        }

    return {
        "title": data.get("title", topic),
        "summary": data.get("extract", "Summary not available.")
    }

# this function is used to access contents from RSS feeds for article information-
def helperFeed(url, topic, category, db, user_id, sub_topics, attempt, MAX):
    # error checking for topic if it's None
    if topic == None:
        return 
    
    # getting articles from the medium
    feed = feedparser.parse(url)
    # checking if we got no articles regarding this topic
    if not feed.entries:
        # getting the index
        index = sub_topics.index(topic)
        # checking if the topic isn't the last sub-topic
        if index == len(sub_topics) - 1:
            # storing the first topic
            topic = sub_topics[0]
        else:
            # storing the last topic 
            topic = sub_topics[index + 1]
        # calling the function recursively
        if attempt >= MAX:
            return None
        return helperFeed(url, topic, category, db, user_id, sub_topics, attempt + 1, MAX)

    # getting a unique article
    article = None
    for entry in feed.entries:
        article = check_article(entry, db, user_id)
        if article:
            break

    # updating the database with the new link
    db.execute("""UPDATE topics_covered SET links = 
                    CASE 
                        WHEN links IS NULL OR links = '' THEN ?
                        ELSE links || ',' || ? 
                    END
                WHERE id = ?""", article["link"], article["link"], user_id)
    print(f"Fetched {len(feed.entries)} articles for topic: {topic}")

    return article

"""
This is function to request for RSS feed of Geeks For Geeks but they didn't let my requests pass through so i couldn't make it work........

# this function is for feed parsing of geeks for geeks
def gfgFeed(topic, db, user_id):
    url = "https://www.geeksforgeeks.org/feed/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch GFG feed: {e}")
        return None

    whole = feedparser.parse(response.text)

    if not whole.entries:
        print("GFG feed returned no entries after custom fetch!")
        return None

    print(f"Fetched {len(whole.entries)} articles from GFG feed.")
    article = None
    usableKeys = keywords.get(topic.lower(), [])
    if not usableKeys:
        usableKeys.append(topic)

    for entry in whole.entries:
        title, summary = entry.get("title", ""), entry.get("summary", "") or entry.get("description", "")
        if any(keyword.lower() in title.lower() for keyword in usableKeys) or \
           any(keyword.lower() in summary.lower() for keyword in usableKeys):
            article = check_article(entry, db, user_id)
            if article:
                break

    if article:
        link = article["link"]
        db.execute("
            UPDATE topics_covered SET links =
                CASE
                    WHEN links IS NULL OR links = '' THEN ?
                    ELSE links || ',' || ?
                END
            WHERE id = ?", link, link, user_id)
    return article"""

# the purpose of this function is to check if the article has been used before or not  
def check_article(entry, db, user_id):

    # getting the links that are already used     
    used_links = db.execute("SELECT links FROM topics_covered WHERE id = ?", user_id)
    links = []
    if used_links and used_links[0].get("links"):
        links = [l.strip() for l in used_links[0]["links"].split(',') if l.strip()]

    # getting the link of the entry recieved
    entry_link = getattr(entry, "link", "")

    # checking if the entry has been repeated before
    if not entry_link or entry_link in links:
        return None
    
    # getting the title, summary of the entry
    title = entry.get("title", "")
    summary = entry.get("summary", "") or entry.get("description", "")
    # error checking for summary
    if not summary and "content" in entry and entry.content:
        summary = entry.content[0].get("value", "")
    if not summary:
        summary = "No summary available for this topic."

    text = f"{title} {summary}"
    # checking if the language is English
    if not isEng(text):
        return None
    
    return {
        "link": entry_link,
        "title": entry.get("title", ""),
        "summary": summary.strip()
    }

# the sole purpose of this function is to choose 7 categories at a random from the list of categories for a week
def choose_category(fields):

    # choosing 7 categories at random out of all
    keys = [list(row.keys())[0] for row in fields]
    if len(keys) < 7:
        return keys
    return random.sample(keys, k = 7)

# this function has to create a nice fomatted hmtl para for our template to process
def prepare(article):

    # getting the start of the article
    start = "" 
    # getting the summary from the article
    content = article.get("summary")
    # parsing the content for any html
    if content:
        content = BeautifulSoup(content, "html.parser").get_text()
    start = content[:200] # the first 200 characters
    # returning the details
    return {
        "para": start,
        "article_title": article["title"],
        "article_link": article["link"],
    }

# to check if article is in english or not
def isEng(text):
    try:
        return detect(text) == 'en'
    except:
        return False
    
# this function is to send the email to the recipient 
def sendEmail(subject, body, userId, db):
    
    # fetching the user email
    emailRow = db.execute("SELECT email FROM users WHERE id = ?", userId)
    if not emailRow:
        print("User doesn't have a email in database")
        return None
    recieveEmail = emailRow[0]["email"]

    # creating the email
    msg = MIMEMultipart("alternative")
    msg["From"] = senderEmail
    msg["To"] = recieveEmail
    msg["Subject"] = subject
    # attaching the body of the email to the msg
    msg.attach(MIMEText("Please enable HTML to view this email", "plain"))
    msg.attach(MIMEText(body, "html"))

    # setting up the connection
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls() # upgrades the channel using TLS for security
        server.login(senderEmail, password) # login in the account
        server.sendmail(senderEmail, recieveEmail, msg.as_string()) # sending the email
    # the return statement
    return f"{subject}\n{body}", True
