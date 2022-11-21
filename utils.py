import hashlib
import json
import logging
import os
import traceback
from enum import Enum
from bs4 import BeautifulSoup
import requests
from joblib import Parallel, delayed
from sqlalchemy import create_engine, insert

from db_model import FileInfo


class Market(Enum):
    BAZAAR = 1
    MYKET = 2


def get_download_link(pkg_name: str) -> str:
    headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
    }

    body = {
        "properties": {
            "language": 2,
            "clientVersionCode": 1100301,
            "androidClientInfo": {
                "sdkVersion": 21,
                "cpu": "x86,armeabi-v7a,armeabi",
            },
            "clientVersion": "11.3.1",
            "isKidsEnabled": False,
        },
        "singleRequest": {
            "appDownloadInfoRequest": {
                "downloadStatus": 1,
                "packageName": pkg_name,
                "referrers": [],
            },
        },
    }

    response = requests.post("https://api.cafebazaar.ir/rest-v1/process/AppDownloadInfoRequest",
                             data=json.dumps(body),
                             headers=headers, )

    response_json = response.json()
    return f"https://appcdn.cafebazaar.ir/apks/{response_json['singleReply']['appDownloadInfoReply']['token']}"


def save_apk_to_file(pkg_name: str, market: Market):
    if market == Market.BAZAAR:
        url = get_download_link(pkg_name)
    else:
        url = f"https://myket.ir/get/app?packageName={pkg_name}"
    response = requests.get(url)
    with open(f"{pkg_name}.apk", "wb") as f:
        f.write(response.content)


def get_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def download_calculate_sha_and_save(path: str, market: Market):
    with open(path) as f:
        pkgs = f.readlines()
        for line in pkgs:
            process(line, market)


def download_calculate_sha_and_save_parallel(path: str, market: Market):
    with open(path) as f:
        pkgs = f.readlines()
        f.close()
    Parallel(n_jobs=6)(delayed(process)(line.strip(), market) for line in pkgs)


def process(line: str, market: Market):
    logging.warning(f"Processing {line}")
    try:
        save_apk_to_file(line, market)
        sha = get_sha256(f"./{line}.apk")
        engine = create_engine(f"sqlite:///db/sha.db", future=True)
        stmt = insert(FileInfo).values(pkg_name=line, sha256=sha)
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(stmt)
            conn.close()
    except Exception:
        logging.error(f"Error on {line}")
    finally:
        try:
            os.remove(f"./{line}.apk")
        except:
            pass

def is_available():
    with open("diff.txt") as f:
        diff = f.readlines()
        f.close()
    for pkg_name in diff:
        req = requests.get(f"https://cafebazaar.ir/app/{pkg_name}")
        soup = BeautifulSoup(req.content, "html.parser")
        error = soup.find("div", {"data-status": "500"})
        try:
            banned = soup.find("h2", {
                "class": "fs-12 AppSubtitles__error"}).text == "این برنامه به علت عدم رعایت قوانین کافه بازار از حالت " \
                                                            "انتشار خارج شده است "
        except AttributeError:
            banned = None
        paid = soup.find("div", {"fs-12 AppSubtitles__item"})
        if error is None and banned is None and paid is None:
            print("available")
            with open("diff_cleaned.txt", "a+") as f:
                f.write(pkg_name)
        if error is not None:
            print("error")
        if banned is not None:
            print("banned")
        if paid is not None:
            print("paid")

if __name__ == '__main__':
    is_available()
    # download_calculate_sha_and_save_parallel("cafebazaar_apps.txt", Market.BAZAAR)
    # download_calculate_sha_and_save_parallel("myket_apps.txt", Market.MYKET)
