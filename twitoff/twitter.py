""" Retreive and request tweets from DS API """
import requests
import spacy
from .models import DB, User, Tweet


nlp = spacy.load("my_model")

def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector

# Add and updates tweets
def add_or_update_user(username):
    """
    Add and updates the user with Twitter handle 'username"
    to our database
    """
    try:
        DB.create_all()
        r = requests.get(
            f"https://lambda-ds-twit-assist.herokuapp.com/user/{username}")
        user = r.json()
        user_id = user["twitter_handle"]["id"]
        db_user = (User.query.get(user_id)) or User(id=user_id, name=username)
        # This adds the db_user to our database
        DB.session.add(db_user)

        tweets = user["tweets"]
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet["full_text"])
            db_tweet = Tweet(
                id=tweet["id"],
                text=tweet["full_text"],
                user=db_user,
                vect=tweet_vector)
            db_user.tweet.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print('Error Processing {}: {}'.format(username, e))

    else:
        DB.session.commit()