from flask import Blueprint, request, redirect, session, url_for
from skraggle.p2p.models import TwitterConnection
from skraggle.config import db
import tweepy
import os
from skraggle.base_helpers.responser import DataResponse

twitterconnect = Blueprint("twitterconnect", __name__, template_folder="templates")

auth = tweepy.OAuthHandler(
    os.getenv("TWITTER_APP_KEY"),
    os.getenv("TWITTER_SECRET_KEY"),
    os.getenv("TWITTER_CALLBACK_URL"),
)


def get_auth_url(auth):
    try:
        print("HERE")
        redirect_url = auth.get_authorization_url()
        return redirect_url

    except Exception as e:
        return str(e)


@twitterconnect.route("/connect", methods=["GET"])
def get_AccessToken():
    auth_url = get_auth_url(auth)
    session["request_token"] = auth.request_token["oauth_token"]
    return redirect(auth_url)


@twitterconnect.route("/callback")
def callback():
    verifier = request.args.get("oauth_verifier")
    token = session["request_token"]
    auth.request_token = {"oauth_token": token, "oauth_token_secret": verifier}
    print(verifier, token)
    try:
        auth.get_access_token(verifier)
        key = auth.access_token
        secret = auth.access_token_secret
        twitter_data = {
            "user_id": dict(session).get("profile", None).get("id"),
            "twitter_key": key,
            "twitter_secret": secret,
        }
        connect_twitter = TwitterConnection(**twitter_data)
        db.session.add(connect_twitter)
        db.session.commit()
        return "Successfully"
    except Exception as e:
        print("Error! Failed to get access token.")
    return "hello"


@twitterconnect.route("/share", methods=["POST"])
def share_twitter():
    post = request.form["post"]
    user_id = dict(session).get("profile", None).get("id")
    user = TwitterConnection.query.filter_by(user_id=user_id).first()
    if user:
        auth.set_access_token(user.twitter_key, user.twitter_secret)
        api = tweepy.API(auth)
        api.update_status(post)
        resp = DataResponse(True, "Feed Posted Successfully")
        return resp.status()
    else:
        resp = DataResponse(False, "User not yet Connected his twitter account")
        return resp.status()
