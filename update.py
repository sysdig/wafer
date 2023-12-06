import requests
import sys
import os
import zipfile
from lxml import html as lxml_html
import logging as log

URL = "https://googlechromelabs.github.io/chrome-for-testing/#stable"


def install_chromedriver():
    try:
        html = requests.get(URL).text
        ext = None
        arch = None
        if sys.platform.startswith("win"):
            arch = "win"
            ext = "exe"
        elif sys.platform.startswith("linux"):
            arch = "linux"
            ext = "elf"
        elif sys.platform.startswith("darwin"):
            arch = "mac"
            ext = "macho"
        else:
            raise Exception("Unknown OS")

        xpath = f"//section[@id='stable']//tr[@class='status-ok']//th//code[contains(text(), 'chromedriver')]//ancestor::tr//th//code[contains(text(), '{arch}')]//ancestor::tr//td//code[contains(text(), 'https://')]//text()"
        root = lxml_html.fromstring(html)
        elements = root.xpath(xpath)
        print(f"Found {len(elements)} chromedriver links")

        for i in range(len(elements)):
            print(f"\t{i}. {elements[i]}")

        while True:
            index = int(input("Select chromedriver to download: "))
            if index >= 0 and index < len(elements):
                break

        url = elements[index]

        print(f"Downloading {url}")
        r = requests.get(url)
        with open("chromedriver.zip", "wb") as f:
            f.write(r.content)

        # unzip chromedriver.zip
        print("Unzipping chromedriver.zip")
        with zipfile.ZipFile("chromedriver.zip", "r") as zip_ref:
            # list files in zip
            for info in zip_ref.infolist():
                zip_ref.extract(info.filename, f"chromedriver.{ext}")

        # remove chromedriver.zip
        os.remove("chromedriver.zip")

        print("Done")
    except Exception as e:
        log.exception(e)
    except KeyboardInterrupt:
        print("Interrupted")
