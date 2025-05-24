import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class SearchConfig:
    dir_name: str
    per_page: int = 100
    max_results: int = 1000

def get_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is not set in environment variables")
    return token
