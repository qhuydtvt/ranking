

from agents import desktop_agents
from random import choice
import requests

def random_headers():
    return {'User-Agent': choice(desktop_agents),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

r = requests.get('https://www.usnews.com/best-colleges/university-of-chicago-1774',headers=random_headers())
print(r.text)