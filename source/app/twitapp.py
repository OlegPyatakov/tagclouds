import os,webbrowser,datetime
import tweepy
from app import app
from app import tagcloud
from app.utils import gettoken,process_source

# Необходимо вставить ключи для вашего twitter аккаунта
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret= ''

def post_tags_from_url(weburl):

    if hours_since_last_tweet() < 2:
        return None

    token=gettoken()
    sourcefilename = process_source(token=token,weburl=weburl)
    tags = tagcloud.get_tags_from_filename(sourcefilename=sourcefilename)
    stopwords = ' '.join([tagcloud.get_stopwords(stopwordsfilename=None),'тысяча','миллион','миллиард'])
    wordcloud = tagcloud.get_wordcloud(stopwords=stopwords)
    wordcloud.generate(tags)
    outputfilename = os.path.join(app.config['OUTPUT_FOLDER'], ''.join(['tagcloud_', token, '.png']))
    wordcloud.to_file(outputfilename)

    text = ''.join(['Главные новости в виде облака тегов на ',
                    str((datetime.datetime.utcnow()+datetime.timedelta(hours=3)).strftime('%d.%m.%Y. %H:%M')),
                    '\n',
                    '#новости #главное #tagcloudsru www.tagclouds.ru'])
    post_twitter(text=text,filename=outputfilename)
    #follow_back()


def follow_back():
    api = get_api()
    followers = api.followers_ids()
    following = api.friends_ids()
    for follower in followers:
        if follower not in following:
            api.create_friendship(follower)


def post_twitter(text=None,filename=None):
    if text==None: return None
    api = get_api()
    api.update_with_media(status=text,filename=filename)


def hours_since_last_tweet():
    api = get_api()
    try:
        last_tweet = api.user_timeline(count=1)[0]
        diff = datetime.datetime.utcnow() - last_tweet.created_at
        return diff.total_seconds() / 3600
    except:
        return 1


def get_api():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    api = tweepy.API(auth)
    return api


def authorize_app():
    auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
    webbrowser.open(auth.get_authorization_url())
    verifier = str(input('Verifier:'))
    auth.get_access_token(verifier)
    print(auth.access_token)
    print(auth.access_token_secret)
    return True

if __name__=='__main__':
    post_tags_from_url('news.yandex.ru')
    #authorize_app()

