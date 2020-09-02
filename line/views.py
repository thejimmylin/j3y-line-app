from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, FollowEvent, UnfollowEvent, TextSendMessage
from .models import QNA, Follower


# This creates a line bot instance mapped to your line channel.
LINE_CHANNEL_ACCESS_TOKEN = 'xeO+6MXpdUrllz8dLEjIuNfET1Pf7jmMDb6vzTkQVpcz/37Bi9xARkhbe3yFqlgOqsjaWXLT5dkvLZkLjMwAUFxypjxCKh1/iEY6uKIJfKr22ZAHrKIyvPOPuhdy6GLPiLjjB4lV60v/eeGlt9KovgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'cdfd566a2c3a81568dbf8b609eeeb955'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if isinstance(event, FollowEvent):
                react_follow(event)
            if isinstance(event, UnfollowEvent):
                react_unfollow(event)
            if isinstance(event, MessageEvent):
                react_message(event)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def react_follow(event):
    """this describes how the bot reacts when a follow event occurs.
    A follow event looks like this.
    e = {
        "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
        "type": "follow",
        "mode": "active",
        "timestamp": 1462629479859,
        "source": {
            "type": "user",
            "userId": "U4af4980629..."
        }
    }
    """
    user_id = event.source.user_id
    if Follower.objects.filter(user_id=user_id).exists():
        if Follower.objects.filter(user_id=user_id).count() != 1:
            line_bot_api.reply_message(
                reply_token=event.reply_token,
                messages=TextSendMessage(text='你是問題分子！我盯上你了')
            )
        else:
            f = Follower.objects.get(user_id=user_id)
            if f.state == 'unfollow':
                f.state = 'follow'
                f.save()
                line_bot_api.reply_message(
                    reply_token=event.reply_token,
                    messages=TextSendMessage(text='猴～你偷封鎖我，抓到了！')
                )
            elif f.state == 'follow':
                line_bot_api.reply_message(
                    reply_token=event.reply_token,
                    messages=TextSendMessage(text='一直追蹤一直爽欸')
                )
            else:
                f.state = 'follow'
                f.save()
                line_bot_api.reply_message(
                    reply_token=event.reply_token,
                    messages=TextSendMessage(text='你是誰？外星人？')
                )
    else:
        profile = line_bot_api.get_profile(user_id)
        f = Follower()
        f.user_id = user_id
        f.display_name = profile.display_name
        f.picture_url = profile.picture_url
        f.status_message = profile.status_message
        f.timestamp = event.timestamp
        f.state = 'follow'
        f.save()
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=TextSendMessage(text=f'哦～{profile.display_name}，你追蹤了我，我們永遠是朋友了，ㄏㄏ')
        )

def react_unfollow(event):
    """this describes how the bot reacts when an unfollow event occurs.
    An unfollow event looks like this.
    e = {
    "type": "unfollow",
    "mode": "active",
    "timestamp": 1462629479859,
    "source": {
        "type": "user",
        "userId": "U4af4980629..."
        }
    }
    """
    user_id = event.source.user_id
    if Follower.objects.filter(user_id=user_id).exists():
        if Follower.objects.filter(user_id=user_id).count() != 1:
            pass
        else:
            f = Follower.objects.get(user_id=user_id)
            if f.state != 'unfollow':
                f.state = 'unfollow'
                f.save()

def react_message(event):
    """this describes how the bot reacts when an message event occurs.
    A message event looks like this.
    e = {
        "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
        "type": "message",
        "mode": "active",
        "timestamp": 1462629479859,
        "source": {
            "type": "user",
            "userId": "U4af4980629..."
        },
        "message": {
            "id": "325708",
            "type": "text",
            "text": "Hello, world! (love)",
            "emojis": [
                {
                    "index": 14,
                    "length": 6,
                    "productId": "5ac1bfd5040ab15980c9b435",
                    "emojiId": "001",
                }
            ]
        }
    }
    """
    sentence = event.message.text
    if sentence.lower().replace(' ','')[:7] == 'j3ycode':
        answers = ['叫我嗎？']
        if sentence.lower().replace(' ','')[:12] == 'j3ycode你學了什麼':
            answers += [str(list(QNA.objects.filter(learned_from=event.source.user_id).values('question', 'answer')))]
        elif sentence.lower().replace(' ','')[:14] == 'j3ycode你到底學了什麼':
            answers += [str(list(QNA.objects.values()))]
        elif count_words('我說', sentence) == 1 and count_words('你說', sentence) == 1:
            if sentence.index('我說') < sentence.index('你說'):
                qna = QNA()
                qna.question = sentence[sentence.index('我說') + 2:sentence.index('你說')]
                qna.answer = sentence[sentence.index('你說') + 2:]
                qna.learned_from = event.source.user_id
                qna.save()
                answers += ['哦～學起來了。']
            else:
                answers += ['太難了，我太難了。']
        else:
            answers += ['太難了，我太難了。']
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=[
                TextSendMessage(text=answer) for answer in answers
            ],
        )
    else:
        read_db_and_act(event, sentence)

def count_words(words, sentence):
    return len(sentence.split(words)) - 1

def read_db_and_act(event, sentence):
    n = QNA.objects.filter(learned_from=event.source.user_id).filter(question=sentence).count()
    if n == 1:
        answer = QNA.objects.filter(learned_from=event.source.user_id).get(question=sentence).answer
    elif n > 1:
        answer = QNA.objects.filter(learned_from=event.source.user_id).filter(question=sentence)[n-1].answer
    else:
        answer = ''
    if answer:
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=TextSendMessage(text=answer),
        )
