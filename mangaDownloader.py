import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
from PyPDF2 import PdfFileMerger
from mangaSplitter import strip_manga
import json


def downloadManga(
    startVolume=0, endVolume=1, url="https://www.mangaworld.io/manga/1708/one-piece/"
) -> tuple:
    r = requests.get(url, allow_redirects=True)
    # print(r.content)

    soup = BeautifulSoup(r.content, "html.parser")
    volumes = soup.find_all("div", class_="volume-element")
    mangaName = soup.find_all("h1", class_="name bigger")[0].contents[0]
    print(mangaName)
    volumeNames = []
    for i in volumes:
        volumeName = (
            i.div.p.contents[1] if len(i.div.p.contents) == 2 else i.div.p.string
        )
        print(volumeName)
        volumeNumber = int(volumeName.lstrip("Volume "))
        if volumeNumber > endVolume or volumeNumber < startVolume:
            continue
        chapters = i.find_all("div", class_="chapter")
        chaptersPdf = []
        chaptersStripPdf = []
        for j in chapters:
            print(j.a["href"] + " " + j.a["title"])
            chapterLink = j.a["href"]

            test = requests.get(j.a["href"] + "/1", allow_redirects=False)
            chapter = BeautifulSoup(test.content, "html.parser")
            print(chapter.find_all(id="page")[0].img["src"])
            templateImageLink = (
                chapter.find_all(id="page")[0]
                .img["src"]
                .rstrip("1.jpg")
                .rstrip("1.png")
            )
            print(templateImageLink)
            pagesImages = []
            pageNum = 1
            img = requests.get(
                templateImageLink + str(pageNum) + ".jpg", allow_redirects=False
            )
            if img.status_code != 200:
                img = requests.get(
                    templateImageLink + str(pageNum) + ".png", allow_redirects=False
                )
            os.makedirs("manga/" + j.a["title"], exist_ok=True)
            while img.status_code == 200:
                open("manga/" + j.a["title"] + "/" + str(pageNum) + ".jpg", "wb").write(
                    img.content
                )
                try:
                    image = Image.open(
                        "manga/" + j.a["title"] + "/" + str(pageNum) + ".jpg"
                    )
                    im = image.convert("RGB")
                except:
                    pass
                pagesImages.append(im)
                pageNum += 1
                img = requests.get(
                    templateImageLink + str(pageNum) + ".jpg", allow_redirects=False
                )
                if img.status_code != 200:
                    img = requests.get(
                        templateImageLink + str(pageNum) + ".png", allow_redirects=False
                    )
            pagesImages[0].save(
                "manga/" + j.a["title"] + "/total" + ".pdf",
                save_all=True,
                append_images=pagesImages[1:],
            )
            chaptersPdf.append("manga/" + j.a["title"] + "/total" + ".pdf")
            chaptersStripPdf.append("manga/" + j.a["title"] + "/totalStrips" + ".pdf")
            strip_manga(j.a["title"], pageNum - 1)

        merger = PdfFileMerger()
        chaptersPdf.reverse()
        for pdf in chaptersPdf:
            merger.append(pdf)
        os.makedirs(f"manga/{mangaName}/", exist_ok=True)
        os.makedirs(f"static/{mangaName}/", exist_ok=True)
        merger.write(f"manga/{mangaName}/" + volumeName + ".pdf")
        merger.write(f"static/{mangaName}/" + volumeName + ".pdf")
        merger.close()

        mergerStrip = PdfFileMerger()
        chaptersStripPdf.reverse()
        for pdf in chaptersStripPdf:
            mergerStrip.append(pdf)

        mergerStrip.write(f"manga/{mangaName}/" + volumeName + " strip.pdf")
        mergerStrip.write(f"static/{mangaName}/" + volumeName + " strip.pdf")
        volumeNames.append(f"static/{mangaName}/" + volumeName + ".pdf")
        volumeNames.append(f"static/{mangaName}/" + volumeName + " strip.pdf")

    return volumeNames, mangaName


if __name__ == "__main__":
    downloadManga()
