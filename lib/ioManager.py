import argparse
import os
from pathlib import Path

class IOManager:
    def __init__(self):
        pass

    def parse_arguments(self) -> argparse.Namespace:
        """
        コマンドライン引数を解析する

        Returns:
            argparse.Namespace: 解析された引数。以下の属性を含む：
                - namespace: 対象のnamespace
                - data_types: 処理するデータタイプのリスト
                - output_dir: 出力先ディレクトリ（デフォルト: './result/'）
                - prompt_name: プロンプトテンプレートのディレクトリパス
        """
        parser = argparse.ArgumentParser(description='RAG処理を実行するスクリプト')
        parser.add_argument('--namespace', type=str, required=True, help='対象のnamespace')
        parser.add_argument('--data-types', type=str, nargs='+', required=True, help='処理するデータタイプのリスト')
        parser.add_argument('--output-dir', type=str, default='./result/', help='出力先ディレクトリ')
        parser.add_argument('--prompt-name', type=str, help='プロンプトテンプレートのディレクトリパス')
        return parser.parse_args()

    def save_results(
        self,
        dir_path: str,
        idx: int,
        prompt: str,
        response: str,
    ) -> None:
        """
        結果をファイルに保存する

        Args:
            dir_path (str): 出力ディレクトリパス
            idx (int): インデックス
            prompt (str): プロンプト
            response (str): レスポンス

        Raises:
            OSError: ディレクトリの作成やファイルの書き込みに失敗した場合
        """
        try:
            # 出力ディレクトリが存在しない場合は作成
            Path(dir_path).mkdir(parents=True, exist_ok=True)

            output_path = f"{dir_path}/{idx}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("# User Query\n")
                f.write(prompt)
                f.write("\n\n# Response\n")
                f.write(response or "None")
        except OSError as e:
            raise OSError(f"ファイルの保存に失敗しました: {str(e)}")
