
# 載入套件
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import random
import json
import configparser
from sklearn.cluster import KMeans
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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
rgbDict = {"0":0, "1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "A":10, "B":11, "C":12, "D":13, "E":14, "F":15}

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
            image_content = line_bot_api.get_message_content(msgID)
            img_name = msgID + ".jpg"
            path = "./" + img_name
            with open(path, "wb") as fd:
                for chunk in image_content.iter_content():
                    fd.write(chunk)
            img = cv2.imread(path)
            shape = img.shape
            height = shape[0]//300
            width = shape[1]//300
            colorList = []
            for i in range(300):
                for j in range(300):
                    b, g, r = img[i*height, j*width]
                    colorList.append([b, g, r])
            clu_center = KMeans(n_clusters = 5, n_init = 10).fit(colorList).cluster_centers_
            text_message = "這些顏色送給您："

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_title("Color Chart", fontsize = 30, y = 0.8)
            plt.axis("off")
            n = 0
            for i in clu_center:
                b = round(i[0], 0)
                g = round(i[1], 0)
                r = round(i[2], 0)
                b = hexDict[b//16]+hexDict[b%16]
                g = hexDict[g//16]+hexDict[g%16]
                r = hexDict[r//16]+hexDict[r%16]
                hex_code = r + g + b
                rect = patches.Rectangle(
                    (n-0.6, 1),
                    0.8,
                    0.8,
                    color = "#" + hex_code,
                    fill = True)
                ax.add_patch(rect)
                plt.text(n-0.6,0.5,"#" + hex_code,{"fontsize":12})
                text_message = text_message + "\n#" + hex_code
                n += 1  
            plt.text(1.8,-0.2,"_Created by Rain Bot_",{"fontsize":8}, verticalalignment = "center", horizontalalignment = "center", color = "grey")
            ax.axis("equal")
            fig.savefig(msgID + ".png")
            
            UPLOAD_FOLDER = "1CE4SfvSIdzjBlUhdk-8Av80Nwc4oZl7q"
            SCOPES = ["https://www.googleapis.com/auth/drive"]
            SERVICE_ACCOUNT_FILE = "core-parsec-377012-bf54595b7c83.json"
            creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build("drive", "v3", credentials=creds)
            filename = msgID + ".png"
            media = MediaFileUpload(filename)
            file = {"name": filename, "parents": [UPLOAD_FOLDER]}
            file_id = service.files().create(body=file, media_body=media).execute()
            url = "https://drive.google.com/uc?export=view&id=" + str(file_id["id"])
            img_message = ImageSendMessage(original_content_url=url, preview_image_url=url)
            text_message = TextSendMessage(text=text_message)
            ad = str(random.randint(1, 5)) + ".json"
            flex_message = json.load(open(ad,"r",encoding="utf-8"))
            text_message = [text_message, img_message, flex_message]
        else:
            if msgType == "text":
                msg = json_data["events"][0]["message"]["text"]
                if msg == "使用說明":
                    text_message = [TextSendMessage(text="請上傳長寬分別大於 300 像素的 jpg 圖檔，Rain Bot 立刻為您解析它的配色"), TextSendMessage(text="提醒您如果拋出較為棘手的難題，Rain Bot 可能會舉白旗投降喔")]
                else:
                    text_message = TextSendMessage(text="Rain Bot 只對圖片感興趣喔！")
            else:
                text_message = TextSendMessage(text="Rain Bot 只對圖片感興趣喔！")
        line_bot_api.reply_message(tk,text_message)
    except:
        if json_data["events"][0]["type"] != "follow":
            text_message = TextSendMessage(text="真是抱歉，這張美麗的圖片考倒 Rain Bot 了")
            line_bot_api.reply_message(tk,text_message)
        print("error")
    return "OK"

if __name__ == "__main__":
    app.run()