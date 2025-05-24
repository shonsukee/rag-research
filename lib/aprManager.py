import os

from lib.baseQuery import BaseQuery
from lib.ioManager import IOManager

class APRManager:
    def __init__(self):
        pass

    def read_prompt_file(self, file_path: str) -> str:
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
        namespace: str,
        data_type: str,
        filename: str,
        language: str
    ) -> None:
        """
        単一ファイルのRAG処理を実行する

        Args:
            query (Query): RAGクエリオブジェクト
            file_path (str): 入力ファイルパス
            output_dir (str): 出力ディレクトリ
            namespace (str): ネームスペース
            data_type (str): データタイプ
            filename (str): ファイル名
            language (str): 言語
        """
        prompt = self.read_prompt_file(file_path)
        if not prompt:
            return

        # 結果保存先ディレクトリ作成
        new_file_name = filename.split(".")[0]
        new_dir_path = f"{output_dir}/{namespace}/{data_type}/{new_file_name}"
        os.makedirs(new_dir_path, exist_ok=True)

        # RAGの適用
        print(f"----- No. {new_file_name} ----")
        # for idx in range(1, 6):
        for idx in range(1, 2):
            response, context, similarity = query.generate_response(prompt)
            IOManager().save_results(
                new_dir_path,
                idx,
                prompt,
                response,
                similarity,
                context,
                language
            )
            print(f"idx: {idx}-finish.")

    def process_data_type(
        self,
        query: BaseQuery,
        namespace: str,
        data_type: str,
        output_dir: str
    ) -> None:
        """
        特定のデータタイプのファイルを処理する

        Args:
            query (Query): RAGクエリオブジェクト
            namespace (str): ネームスペース
            data_type (str): データタイプ
            output_dir (str): 出力ディレクトリ
        """
        directory_path = f"./dataset/{namespace}/{data_type}/"
        for filename in os.listdir(directory_path):
            language = filename.split(".")[-1]
            file_path = os.path.join(directory_path, filename)
            self.process_single_file(
                query,
                file_path,
                output_dir,
                namespace,
                data_type,
                filename,
                language
            )
        print("complete: ", data_type)
