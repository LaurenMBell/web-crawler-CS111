import requests
from urllib.parse import urlparse


class RequestGuard:
    def __init__(self, url):
        self.domain = self.get_domain(url)
        self.forbidden = self.parse_robots()

    def can_follow_link(self, url):
        if self.domain not in url:
            return False

        parsed_url = urlparse(url)
        path = parsed_url.path

        for forbidden_path in self.forbidden:
            if path.startswith(forbidden_path):
                return False

        return True

    def make_get_request(self, url, use_stream =  False):
        if self.can_follow_link(url):
            return requests.get(url, stream = use_stream)
        return None

    def parse_robots(self):
        r_url = f"{self.domain}/robots.txt"
        try:
            response = requests.get(r_url)
            response.raise_for_status()
        except requests.RequestException:
            return []

        forbidden = []
        lines = response.text.split('\n')
        for line in lines:
            if line.startswith('Disallow:'):
                path = line.split(': ')[1].strip()
                forbidden.append(path)

        return forbidden

    def get_domain(self, url):
        p_url = urlparse(url)
        return f"{p_url.scheme}://{p_url.netloc}"
