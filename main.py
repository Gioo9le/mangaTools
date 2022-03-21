import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests as rs
from bs4 import BeautifulSoup
from mangaDownloader import downloadManga
from zipfile import ZipFile

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/list-manga", response_class=HTMLResponse)
async def list(request: Request, manga: str):
    headers = {
        "authority": "www.mangaworld.in",
        "content-length": "0",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "accept": "*/*",
        "csrf-token": "jZPvBBBI-yheICNeBxWz9SAjeoxNC45L5bOY",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "origin": "https://www.mangaworld.in",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.mangaworld.in/api/mangas/search?keyword=one%20piece",
        "accept-language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": "_ga=GA1.2.142776608.1618357355; connect.sid=s%3AsmphmELloT6ij0e2lWOkfa9_IF9GCpx2.BWWDobqYaHMoRqT9NfAT%2BU%2Fou7HxdiCRdZFGvU8oKJ8; __gads=ID=98c1b2b2e29ceec4-2257471738c8004d:T=1622553613:RT=1622553613:S=ALNI_MYuMPNxFaBLOkxI19TLHlcXZtOgGg; _csrf=chXN0Iwn7JwC308MTgYDNPai; BB_plg=pm; _gid=GA1.2.1578755777.1629189856; AdskeeperStorage=%7B%220%22%3A%7B%22svspr%22%3A%22https%3A%2F%2Fwww.mangaworld.in%2Farchive%3Fkeyword%3Donepiece%22%2C%22svsds%22%3A2%2C%22TejndEEDj%22%3A%22dMPbgOUGd%22%7D%2C%22C1120654%22%3A%7B%22page%22%3A1%2C%22time%22%3A1629215936611%7D%2C%22C831615%22%3A%7B%22page%22%3A1%2C%22time%22%3A1629213641708%7D%7D; _gat_gtag_UA_93961448_2=1",
    }

    params = (("keyword", manga),)

    response = rs.post(
        "https://www.mangaworld.in/api/mangas/search", headers=headers, params=params
    )
    dictManga = [
        {
            "name": resManga["title"],
            "author": resManga["author"],
            "img": resManga["imageT"],
            "url": f'https://www.mangaworld.in/manga/{resManga["linkId"]}/{resManga["slug"]}',
        }
        for resManga in response.json()["data"]
    ]
    print(dictManga)
    print(manga)
    res = rs.get("https://www.mangaworld.in/archive?keyword=one%20piece")
    pageSoup = BeautifulSoup(res.content)
    print([manga["href"] for manga in pageSoup.find_all("a", class_="manga-title")])

    return templates.TemplateResponse(
        "list.html", {"request": request, "name": manga, "mangas": dictManga}
    )


@app.get("/download_volumes", response_class=FileResponse)
async def download_volumes(
    request: Request, start_volume: int, end_volume: int, url: str
):
    volumeNames, mangaName = downloadManga(start_volume, end_volume, url)
    with ZipFile(f"static/{mangaName}/compressed.zip", "a") as zipped:
        for volume in volumeNames:
            zipped.write(volume)

    return FileResponse(f"static/{mangaName}/compressed.zip")
