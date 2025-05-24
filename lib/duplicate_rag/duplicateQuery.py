from typing import List, Tuple, Dict
import numpy as np
from lib.baseQuery import BaseQuery

class DuplicateQuery(BaseQuery):
    def __init__(self, namespace: str, prompt_dir: str):
        """
        DuplicateQueryクラスの初期化

        Args:
            namespace (str): Pineconeのネームスペース
            prompt_dir (str): プロンプトテンプレートのディレクトリパス
        """
        super().__init__(namespace, prompt_dir)

        # 複数のDBを初期化
        self.query_engines = {
            "latest_natural_language": self._initialize_pinecone("latest-lang"),
            "latest_code": self._initialize_pinecone("latest-code"),
            "outdated_natural_language": self._initialize_pinecone("outdated-lang"),
            "outdated_code": self._initialize_pinecone("outdated-code")
        }

    def _create_prompt(self, results: dict[str, str]) -> str:
        """
        プロンプトの作成

        Args:
            results (dict[str, str]): 各DBからの検索結果

        Returns:
            str: 生成されたプロンプト
        """
        return self.prompt_template.format(
            latest_natural_language=results.get("latest_natural_language", ""),
            latest_code=results.get("latest_code", ""),
            outdated_natural_language=results.get("outdated_natural_language", ""),
            outdated_code=results.get("outdated_code", ""),
            user_query=results.get("user_query", "")
        )

    def _process_nodes(self, nodes: List) -> Tuple[str, List[float]]:
        """
        ノードの処理を行う

        Args:
            nodes (List): 処理対象のノードリスト

        Returns:
            Tuple[dict[str, str], List[float]]: (処理済みコンテキスト, 類似度スコアリスト)
        """
        results = ""
        similarities = []

        for node in nodes:
            results += f"\n\nContext (score: {node.score}): \n{node.text}"
            similarities.append(node.score)

        return results, similarities

    def _fetch_pinecone_indexes(self, prompt: str) -> Tuple[dict[str, str], List[float]]:
        """
        ベクトルDBからノードを取得

        Args:
            prompt (str): ユーザの入力プロンプト

        Returns:
            Tuple[dict[str, str], List[float]]: (処理済みコンテキスト, 類似度スコアリスト)
        """
        all_results = {
            "latest_natural_language": "",
            "latest_code": "",
            "outdated_natural_language": "",
            "outdated_code": "",
            "user_query": prompt
        }
        all_similarities = []

        for db_type, engine in self.query_engines.items():
            response = engine.query(prompt)
            results, similarities = self._process_nodes(response.source_nodes)
            all_results[db_type] = results
            all_similarities.extend(similarities)

        return all_results, all_similarities

    def generate_response(self, prompt: str) -> Tuple[str, str, float]:
        """
        プロンプトに基づいてレスポンスを生成する

        Args:
            prompt (str): ユーザの入力プロンプト

        Returns:
            Tuple[str, str, float]: (レスポンス, コンテキスト, 類似度スコア)
        """
        try:
            results, similarities = self._fetch_pinecone_indexes(prompt)

            # 関連度の平均計算
            similarity = float(np.mean(similarities)) if similarities else 0.0

            # プロンプトの生成
            combined_query = self._create_prompt(results)

            # OpenAI APIの呼び出し
            chatgpt_response = self.client.chat.completions.create(
                model="o4-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a chatbot that modifies an old version of the {self.namespace} API to a new one. You must follow the relevant information from both old and new versions."
                    },
                    {
                        "role": "user",
                        "content": combined_query
                    }
                ]
            )
            response = chatgpt_response.choices[0].message.content or ""

            # コンテキストのフォーマット（user_queryを除く）
            formatted_context = "\n".join(
                f"## {key}\n{value}"
                for key, value in results.items()
                if key != "user_query"
            )

            return response, formatted_context, similarity

        except Exception as e:
            raise Exception(f"レスポンス生成中にエラーが発生しました: {str(e)}")
