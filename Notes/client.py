from urllib.parse import urljoin, urlparse, parse_qs
import requests

ENDPOINT = "http://9vw9k2gvvcx96cvm.instance.penguin.0ops.sjtu.cn:18080"


class APIClient:
    def __init__(self, endpoint=ENDPOINT):
        self.endpoint = endpoint
        self.session = requests.Session()

    def login(self, username="tomo0", password="penguins"):
        login_url = urljoin(self.endpoint, "/login")
        response = self.session.post(
            login_url,
            data={"username": username, "password": password},
            allow_redirects=False,
        )
        if response.status_code != 302:
            raise Exception(f"Login failed: {response.status_code}")

        location = response.headers.get("Location", "")
        if not location:
            raise Exception("Location not found")

        full_url = urljoin(self.endpoint, location)
        parsed = urlparse(full_url)
        query_params = parse_qs(parsed.query)

        if "token" not in query_params:
            raise Exception("Token not found")

        self.token = query_params["token"][0]
        return True

    def get_note(self):
        if not hasattr(self, "token"):
            raise Exception("Please login first")

        note_url = urljoin(self.endpoint, "/note")
        response = self.session.get(note_url, params={"token": self.token})

        if response.status_code == 200:
            return response.text
        raise Exception(f"Failed to get note: {response.status_code} - {response.text}")


if __name__ == "__main__":
    client = APIClient()
    client.login()
    note = client.get_note()
