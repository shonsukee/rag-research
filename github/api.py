import requests
from urllib.parse import quote
from typing import Optional, Dict
from config import SearchConfig

class GitHubAPIClient:
    def __init__(self, token: str):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}"
        }

    def search(self, query: str, config: SearchConfig, page: int) -> Optional[Dict]:
        encoded_query = quote(query)
        url = self._build_search_url(encoded_query, config)
        full_url = f"{url}&per_page={config.per_page}&page={page}"
        response = requests.get(full_url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed query: {query} | Status: {response.status_code}")
            return None

    def _build_search_url(self, encoded_query: str, config: SearchConfig) -> str:
        if config.dir_name == "pull-requests":
            return f"https://api.github.com/search/issues?q={encoded_query}+is:pr+is:closed"
        elif config.dir_name == "issues":
            return f"https://api.github.com/search/issues?q={encoded_query}+is:issue+is:closed"
        else:
            return f"https://api.github.com/search/{config.dir_name}?q={encoded_query}"
