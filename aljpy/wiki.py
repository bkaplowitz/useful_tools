import pandas as pd
import requests


def wikitable(page, idx=0, **kwargs):
    r = requests.get(f"https://en.wikipedia.org/wiki/{page}")
    return pd.read_html(r.content, attrs={"class": "wikitable"}, **kwargs)[idx]
