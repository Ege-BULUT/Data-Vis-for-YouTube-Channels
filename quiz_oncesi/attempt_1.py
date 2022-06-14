import io
import time
import copy
import selenium
import numpy as np
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.remote.webelement
import matplotlib.pyplot as plt
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
import mpld3

#
# TODO: https://www.youtube.com/c/LordPac/videos
#     .  3 adet grafik oluşturulacak
#     .  1. Video izlenme sayısı - Video süresi                         (Video süresini çek)
#     .  2. Video izlenme sayısı - Video Başlığı uzunluğu               (Bitmek üzere)
#     . Bu grafikleri çıktı olarak göster.
#     .

PCLanguage = "en"  # "tr"

app = FastAPI()

origins = [
    "null",
    "http://localhost:63342",
    "http://localhost:8000"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"])

browser = webdriver.Chrome()
url = "https://www.youtube.com/c/BoraCanbula/videos"
# url = "https://www.youtube.com/c/LordPac/videos"

videos = []
channelName = ""
views = []
titles = []
durationsText = []
durationsSec = []


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/close", response_class=HTMLResponse)
async def close_browser():
    browser.close()
    return """
                <html>
                    <head>
                        <title>CLOSE</title>
                        <link href="/style.css" rel="stylesheet" type="text/css">
                    </head>
                    <body>
                        <h1>Data browser has successfully closed.</h1>
                    </body>
                </html>
                """


@app.get("/style.css")
async def style():
    return FileResponse("./style.css")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/selenium", response_class=HTMLResponse)
async def seleniumFun():
    global videos
    global channelName
    if len(channelName) < 1:
        link = "https://www.youtube.com/c/LordPac/videos"
        browser.get(link)
        time.sleep(2)
        videos = browser.find_elements(by=By.CLASS_NAME, value="ytd-grid-renderer")
        channelName = browser.find_elements(by=By.CLASS_NAME, value="ytd-channel-name")[0].text

    global views
    global titles
    global durationsText  # hh:mm:ss
    global durationsSec  # seconds
    views = []
    titles = []
    durationsText = []
    durationsSec = []

    titlesText = ""

    # TITLES
    for title in videos[1].find_elements(by=By.ID, value="video-title"):
        titles.append(title.text)

    # VIEWS
    count, count2 = 1, 0
    for view in videos[1].find_elements(by=By.CLASS_NAME, value="ytd-grid-video-renderer"):
        print(str(count) + ". -> " + view.text)
        global PCLanguage
        if count == 13 or (count - 13) % 24 == 0:
            number = view.text.split(" ")[0]
            if PCLanguage == "tr":
                if view.text.split(" ")[1][0] == 'B':
                    multipler = 1000
                    if "." in number:
                        number = (int(number.split(".")[0]) * 10) + int(number.split(".")[1])
                        multipler = 100
                    text = str((int(number) * multipler))
                elif view.text.split(" ")[1][0] == 'M':
                    multipler = 1000000
                    if "." in number:
                        number = (int(number.split(".")[0]) * 10) + int(number.split(".")[1])
                        multipler = 100000
                    text = str((int(number) * multipler))
                else:
                    text = number

            elif PCLanguage == "en":
                number = view.text.split(" ")[0][0:-1]
                if view.text.split(" ")[0][-1] == 'K':
                    multipler = 1000
                    if "." in number:
                        number = (int(number.split(".")[0]) * 10) + int(number.split(".")[1])
                        multipler = 100
                    text = str((int(number) * multipler))
                elif view.text.split(" ")[0][-1] == 'M':
                    multipler = 1000000
                    if "." in number:
                        number = (int(number.split(".")[0]) * 10) + int(number.split(".")[1])
                        multipler = 100000
                    text = str((int(number) * multipler))
                else:
                    text = view.text.split(" ")[0]

            views.append(int(text))
        count = count + 1

    # DURATIONS
    # ytd-thumbnail-overlay-time-status-renderer
    counter = 0
    for duration in videos[1].find_elements(by=By.CLASS_NAME, value="ytd-thumbnail-overlay-time-status-renderer"):
        if counter % 2 == 1:
            sec = timeToSec(duration.text.split(":"))
            durationsText.append(duration.text)
            durationsSec.append(copy.deepcopy(sec))
        counter = counter + 1

    print("\nDURATION TEST : ")
    for i in range(0, len(durationsText)):
        print(durationsText[i] + "(" + str(durationsSec[i]) + ")secs")

    HTMLpart = '<li class="list-item"><div>Title :</div><div>View :</div><div>Duration :</div></li>'

    print("\nREAL TEST : ")
    for i in range(0, len(views)):
        titlesText = titlesText + "<p>" + titles[i] + "</p>\n"

        HTMLpart = HTMLpart + '<li class="list-item"><div>' + titles[i] + "</div>\n" \
                                                                          "<div>" + str(
            views[i]) + " Görüntülenme </div>\n" \
                        "<div>" + durationsText[i] + "</div>\n" \
                                                     "</li>\n"

        # print(str(i + 1) + ". : " + titles[i] + "\n" + str(views[i]) + " Görüntülenme \t | (" + durationsText[i] + ")")

    HTMLpart = HTMLpart + '<li class="list-item"><div>______</div><div>_________________</div><div>____</div></li>'

    totalTime = secToTime(sum(durationsSec))

    HTMLpart = HTMLpart + '<li class="list-item"><div>TOTAL : </div>\n' \
                          "<div>" + str(sum(views)) + " Görüntülenme </div>\n" \
                                                      "<div>" + totalTime + " (" + str(
        sum(durationsSec)) + " Saniye)</div>\n" \
                             "</li>\n"

    score = '{0:,.3f}'.format(sum(views) / sum(durationsSec))
    HTMLpart = HTMLpart + "<h2>Channel Score (Views/Seconds) = [" + score + "] !</h2> "
    print("\n\nTest : " + HTMLpart + "\n\n")

    return """
                <html>
                    <head>
                        <title>YT statistics</title>
                        <link href="/style.css" rel="stylesheet" type="text/css">
                    </head>
                    <body>
                    <div class="container w-container">
                        <h1 class="heading"> """ + channelName + """ 's YouTube statistics</h1>
                        <ol id="videos" role="list" class="list">
                        """ + HTMLpart + """
                        </ol></div>
                    </div>
                    </body>
                </html>
                """


@app.get("/selenium/{ytchannel_name}", response_class=HTMLResponse)
async def selenium(ytchannel_name):
    link = "https://www.youtube.com/c/" + ytchannel_name + "/videos"
    browser.get(link)
    time.sleep(2)
    global videos
    videos = browser.find_elements(by=By.CLASS_NAME, value="ytd-grid-renderer")
    global channelName
    channelName = browser.find_elements(by=By.CLASS_NAME, value="ytd-channel-name")[0].text

    return RedirectResponse("/selenium")


@app.get("/plot/{plot}")
async def create_plot(plot: str):
    # Select a subset of the networks

    global views
    global titles
    global durationsSec  # seconds
    g = plt.figure()
    if plot == "view-duration":
        plot = sns.scatterplot(x=durationsSec, y=views)
        plot.set(title='Views - Durations(sec)', xlabel='duration (Sec)', ylabel='view')
        fig = plot.get_figure()

        # with io.BytesIO() as g_bytes:
        #    plt.savefig(g_bytes, format='png')
        #    g_bytes.seek(0)
        #    response = Response(g_bytes.getvalue(), media_type='image/png')
        # return response
        return HTMLResponse(mpld3.fig_to_html(fig))

    elif plot == "view-titlelength":
        titleLengths = []
        for title in titles:
            titleLengths.append(len(title))

        g = sns.scatterplot(x=titleLengths, y=views).set(title='Views - title lengths')

        with io.BytesIO() as g_bytes:
            plt.savefig(g_bytes, format='png')
            g_bytes.seek(0)
            response = Response(g_bytes.getvalue(), media_type='image/png')
        return response

    else:
        htmlresp = """
                <html>
                    <head>
                        <title>ERROR</title>
                    </head>
                    <body>
                        <h2>Error:</h2>
                        <h5>There is no plot named '""" + plot + """"'</h5>
                        <pre>
                        There are only
                            1. '/view-duration' plot
                            2. '/view-titlelength' plot
                        plots for now.
                        </pre>
                    </body>
                </html>
                    """
        return HTMLResponse(htmlresp, 200)


def secToTime(seconds):
    text = "00"
    hrs = int(seconds / (60 * 60))
    seconds = seconds - (hrs * (60 * 60))
    mins = int(seconds / 60)
    seconds = seconds - (mins * 60)
    text = str(seconds)
    if mins >= 1:
        text = str(mins) + ":" + text
    if hrs >= 1:
        text = str(hrs) + ":" + text

    return text


def timeToSec(arr):
    sec = 0
    multiplier = 1
    for i in range(len(arr) - 1, -1, -1):
        sec = sec + (int(arr[i]) * multiplier)
        multiplier = multiplier * 60
    return sec
