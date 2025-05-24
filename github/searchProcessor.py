from api import GitHubAPIClient
from fileManager import FileManager
from config import SearchConfig

class SearchQueryProcessor:
    def __init__(self, api_client: GitHubAPIClient, file_manager: FileManager):
        self.api_client = api_client
        self.file_manager = file_manager

    def process_query(self, query: str, config: SearchConfig):
        results = []
        page = 1

        while True:
            data = self.api_client.search(query, config, page)
            if not data or 'items' not in data or not data['items']:
                break

            print(f"Page {page}: {len(data['items'])} items")
            results += [item['html_url'] for item in data['items']]
            page += 1

            if len(results) >= config.max_results:
                print("Hit GitHub search limit (1000 items)")
                break

        if results:
            safe_name = query.split(" ")[-1] if " " in query else query.split("/")[-1]
            number = self.file_manager.get_next_file_number() + 1
            file_name = f"{number}-{safe_name}.txt"
            self.file_manager.save_results(results, file_name)
