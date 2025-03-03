import os

from blue_options import string
from blue_objects import file, README

from vancouver_watching import NAME, VERSION, ICON, REPO_NAME


content = {
    "time-series": {
        "url": "https://kamangir-public.s3.ca-central-1.amazonaws.com/vanwatch-cache-2024-02-28-21-04-19-26236.tar.gz",
        "thumbnail": f"https://kamangir-public.s3.ca-central-1.amazonaws.com/2024-01-06-20-39-46-73614/2024-01-06-20-39-46-73614-2X.gif?raw=true&random={string.random()}",
    },
    "last build": {
        "url": f"https://kamangir-public.s3.ca-central-1.amazonaws.com/test_vancouver_watching_ingest/animation.gif?raw=true&random={string.random()}",
        "thumbnail": f"https://kamangir-public.s3.ca-central-1.amazonaws.com/test_vancouver_watching_ingest/animation.gif?raw=true&random={string.random()}",
    },
}

items = [
    "[{}]({}) [![image]({})]({})".format(
        title,
        item["url"],
        item["thumbnail"],
        item["url"],
    )
    for title, item in content.items()
]


def build():
    return README.build(
        items=items,
        path=os.path.join(file.path(__file__), ".."),
        ICON=ICON,
        NAME=NAME,
        VERSION=VERSION,
        REPO_NAME=REPO_NAME,
    )
