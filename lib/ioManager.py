import argparse

class IOManager:
    def __init__(self):
        pass

    def parse_arguments(self) -> argparse.Namespace:
        """
        コマンドライン引数を解析する

        Returns:
            argparse.Namespace: 解析された引数
        """
        parser = argparse.ArgumentParser(description='RAG処理を実行するスクリプト')
        parser.add_argument('--namespace', type=str, required=True, help='対象のnamespace')
        parser.add_argument('--data-types', type=str, nargs='+', required=True, help='処理するデータタイプのリスト')
        parser.add_argument('--output-dir', type=str, default='./result/', help='出力先ディレクトリ')
        parser.add_argument('--prompt-dir', type=str, help='プロンプトテンプレートのディレクトリパス')
        return parser.parse_args()

    def save_results(
        self,
        dir_path: str,
        idx: int,
        prompt: str,
        response: str,
        similarity: float,
        context: str,
        language: str
    ) -> None:
        """
        結果をファイルに保存する

        Args:
            dir_path (str): 出力ディレクトリパス
            idx (int): インデックス
            prompt (str): プロンプト
            response (str): レスポンス
            similarity (float): 類似度スコア
            context (str): 関連コンテキスト
            language (str): 言語
        """
        output_path = f"{dir_path}/{idx}.md"
        with open(output_path, "w") as f:
            f.write("# User Query\n")
            f.write(f"```{language}\n")
            f.write(prompt)
            f.write("\n```\n\n")
            f.write("# Response\n")
            f.write(f"```{language}\n")
            f.write(response or "None")
            f.write("\n```\n\n")
            f.write("# Similarity Score\n")
            f.write(str(similarity))
            f.write("\n\n")
            f.write("# Relevant Context\n")
            f.write(context)
