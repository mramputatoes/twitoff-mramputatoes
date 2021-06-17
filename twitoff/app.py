""" 
Main app/routing file for Twitoff.

The file that holds the function 'create_app'
to collect out modules and hold our flask app
"""
from os import getenv
from .twitter import add_or_update_user
from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .predict import predict_user

def create_app():
    # initilizes our application
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URL"] = getenv('DATABASE_URL')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    DB.init_app(app)
    

    @app.route("/")
    def root():
        """This will be presented when we visit '<BASE_URL>/ '"""
        users = User.query.all()  # SQL equivalent: `SELECT * FROM user;`
        return render_template("base.html", title='Home', users=users)

    # @app.route('/populate')
    # def populate():
    #     add_or_update_user("mica")
    #     add_or_update_user("jackblack")
    #     add_or_update_user("elonmusk")
    #     add_or_update_user("matthewmercer")
    #     return "All have been populate" #render_template("base.html", title="Home", users=User.query.all())

    @app.route("/compare", methods=["POST"])
    def compare():
        """This will be presented when we visit '<BASE_URL>/compare '"""
        user0, user1 = sorted(
            [request.values["user0"], request.values["user1"]])

        if user0 == user1:
            message = "Cannot compare users to themselves!"
        else:
            prediction = predict_user(
                user0, user1, request.values["tweet_text"])

            message = "'{}' is more likely to be said by {} than {}".format(
                request.values["tweet_text"],
                user1 if prediction else user0,
                user0 if prediction else user1
            )

        return render_template("prediction.html", title="prediction", message=message)
    
    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values["user_name"]
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = f"User {name} successfully added!"

            tweets = User.query.filter(User.name == name).one().tweet
        except Exception as e:
            message = f"Error adding {name}: {e}"
            tweets = []

        return render_template("user.html", title=name, tweets=tweets, message=message)    

    @app.route("/reset")
    def reset():
        DB.drop_all()
        DB.create_all()
        return "The DB has been reset!"

    @app.route("/update")
    def update():
        users = User.query.all()
        for user in users:
            add_or_update_user(user)
        return "All the users have been updated!"
    

    
    return app
    

# def insert_example_users(): #You need to comment out this code after running once.
#     """
#     Will get error if ran twice because of duplicate primary keys
#     Not real data - just to play with
#     """
    
#     micaburton = User(id=1, name="MicaBurton")
#     elonmusk = User(id=2, name="ElonMusk")
#     # Test Twee that went no where
#     # mbtweet0 = Tweet(id=3, text = 'This is Mica Burton!', user=micaburton)
    
#     DB.session.add(micaburton)
#     DB.session.add(elonmusk)
#     # Test Tweet that went nowhere
#     # DB.session.add(mbtweet0)
#     DB.session.commit()
