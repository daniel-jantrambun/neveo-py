import requests


def download(name: str, url: str) -> None:
    """ Download a file and save it locally"""
    filename = "downloads/{}".format(name)
    r = requests.get(url, allow_redirects=True)
    open(filename, "wb").write(r.content)
