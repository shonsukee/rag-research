import logging
import os

from lib.baseQuery import BaseQuery
from lib.ioManager import IOManager

class APRManager:
    def __init__(self):
        pass

    def read_file(self, file_path: str) -> str:
        """
        プロンプトファイルを読み込む

        Args:
            file_path (str): ファイルパス

        Returns:
            str: ファイルの内容
        """
        with open(file_path, 'r') as file:
            return file.read()

    def process_single_file(
        self,
        query: BaseQuery,
        file_path: str,
        output_dir: str,
        data_type: str,
        filename: str
    ) -> None:
        """
        単一ファイルの処理を実行する

        Args:
            query (BaseQuery): クエリオブジェクト
            file_path (str): 入力ファイルパス
            output_dir (str): 出力ディレクトリ
            data_type (str): データタイプ
            filename (str): ファイル名
            language (str): 言語
        """
        # プロンプトの作成
        results = {}
        results["user_query"] = self.read_file(file_path)
        language = file_path.split("/")[-1].split(".")[-1]
        keys = query._fetch_vars()

        if query.prompt_name == "llm":
            results["link"] = query._fetch_links()
        else:
            for key in keys:
                if key == "user_query":
                    continue

                fetch_nodes = query._fetch_pinecone_indexes(key, results["user_query"])

                # リランキングを実施
                reranked_nodes = query.rerank(fetch_nodes, results["user_query"])
                if reranked_nodes is None:
                    logging.warning(f"No nodes found for key: {key} in {query.namespace}")
                    return

                results[key] = query._process_nodes(reranked_nodes)

        prompt = query._create_prompt(results)

        # 結果保存先ディレクトリ作成
        new_file_name = filename.split(".")[0]
        new_dir_path = f"{output_dir}/{query.prompt_name}/{query.namespace}/{data_type}/{new_file_name}"
        os.makedirs(new_dir_path, exist_ok=True)

        # APRの適用
        logging.info(f"Processing file: {new_file_name} in {data_type} for {query.namespace}")
        for idx in range(1, 6):
            response = query.generate_response(prompt)
            if '```' not in response:
                response = f"```{language}\n{response}\n```"

            IOManager().save_results(
                new_dir_path,
                idx,
                prompt,
                response
            )
            print(f"idx: {idx}-finish.")

    def process_data_type(
        self,
        query: BaseQuery,
        data_type: str,
        output_dir: str
    ) -> None:
        """
        特定のデータタイプのファイルを処理する

        Args:
            query (BaseQuery): クエリオブジェクト
            data_type (str): データタイプ
            output_dir (str): 出力ディレクトリ

        Raises:
            ValueError: ネームスペースが指定されていない場合
        """
        directory_path = f"./dataset/{query.namespace}/{data_type}/"
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            self.process_single_file(
                query,
                file_path,
                output_dir,
                data_type,
                filename
            )
        logging.info(f"Finished processing {data_type} files for namespace {query.namespace}")
