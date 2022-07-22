import hashlib
import json
import logging
import traceback

import requests


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
                "sdkVersion": 22,
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


def save_apk_to_file(pkg_name: str):
    url = get_download_link(pkg_name)
    response = requests.get(url)
    with open(f"{pkg_name}.apk", "wb") as f:
        f.write(response.content)


def get_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def download_calculate_sha_and_save():
    with open("apps.txt") as f:
        pkgs = f.readlines()
        for line in pkgs:
            stripped_line = line.strip()
            print(f"Processing {stripped_line}")
            try:
                save_apk_to_file(stripped_line)
                sha = get_sha256(f"./{stripped_line}.apk")
                with open("sha_list.txt", "a+") as output:
                    output.write(f"{sha}\n")
            except Exception:
                print(f"Error on {stripped_line}")
                logging.error(traceback.format_exc())


if __name__ == '__main__':
    download_calculate_sha_and_save()
