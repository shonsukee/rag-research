from config import SearchConfig, get_github_token
from api import GitHubAPIClient
from fileManager import FileManager
from searchProcessor import SearchQueryProcessor
from queries import search_queries

def main():
    config = SearchConfig(dir_name="pull-requests")
    token = get_github_token()

    api_client = GitHubAPIClient(token)
    file_manager = FileManager(config.dir_name)
    processor = SearchQueryProcessor(api_client, file_manager)

    for query in search_queries:
        print(f"\nProcessing query: {query}")
        processor.process_query(query, config)

if __name__ == "__main__":
    main()
