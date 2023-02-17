
# 載入套件
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
import configparser
import numpy as np
import cv2


# 建立 APP
app = Flask(__name__)

# LINE 聊天機器人的基本資料
curpath = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(curpath,"config.ini")

config = configparser.ConfigParser()
config.read(filename)

line_bot_api = LineBotApi(config.get("line-bot", "channel_access_token"))
handler = WebhookHandler(config.get("line-bot", "channel_secret"))

hexDict = {0:"0", 1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"A", 11:"B", 12:"C", 13:"D", 14:"E", 15:"F"}

# 接收 LINE 的資訊並回覆
@app.route("/callback", methods=["POST"])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)
    try:
        signature = request.headers["X-Line-Signature"]
        handler.handle(body, signature)
        tk = json_data["events"][0]["replyToken"]
        msgType = json_data["events"][0]["message"]["type"]
        msgID = json_data["events"][0]["message"]["id"]
        if msgType == "image":
            t = 0
            image_content = line_bot_api.get_message_content(msgID)
            t = 1
            img_name = msgID + ".jpg"
            t = 2
            path = "./" + img_name
            t = 3
            with open(path, "wb") as fd:
                for chunk in image_content.iter_content():
                    fd.write(chunk)
            t = 4
            img = cv2.imread(path)
            t = 5
            shape = img.shape
            t = 6
            #shape = image_content.shape
            height = shape[0]
            t = 7
            width = shape[1]
            t = 8
            colorDict = {}
            t = 9
            for i in range(height):
                for j in range(width):
                    b, g, r = img[i, j]
                    t = 10
                    t = str(b)+str(g)+str(r)
                    b = hexDict[b//16]+hexDict[b%16]
                    t = 11
                    t = str(b)+str(g)+str(r)
                    g = hexDict[g//16]+hexDict[g%16]
                    t = 12
                    t = str(b)+str(g)+str(r)
                    r = hexDict[r//16]+hexDict[r%16]
                    t = 13
                    t = str(b)+str(g)+str(r)
                    hex_code = r + g + b
                    t = 14
                    t = hex_code
                    if hex_code in hexDict:
                        colorDict[hex_code] += 1
                        t = 15
                    else:
                        colorDict[hex_code] = 1
                        t = 16
            t = 17
            text_message = ""
            if len(colorDict.keys()) > 5:
                for i in range(5):
                    maxNum = 0
                    for j in colorDict.keys():
                        time = colorDict[j]
                        if time > maxNum:
                            maxNum = time
                            choose = j
                    text_message = text_message + "#" + choose + "\n"
            else:
                for i in colorDict.keys():
                    text_message = text_message + "#" + i + "\n"
            text_message = TextSendMessage(text=text_message)
        else:
            msgText = json_data["events"][0]["message"]["text"]
            text_message = TextSendMessage(text="Rain Bot 不善言詞，只能複誦您的話……\n\n\n\n"+msgText)
        line_bot_api.reply_message(tk,text_message)    
    except:
        print(t)
    return "OK"

if __name__ == "__main__":
    app.run()
