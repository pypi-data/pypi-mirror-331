import requests


def download(url):
    r = requests.get(url)
    return r.content


def download_to_file(url, path, mode=0o644):
    with open(path, "wb") as f:
        f.write(download(url))
