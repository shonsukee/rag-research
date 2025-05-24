from typing import Tuple, List

import numpy as np
from lib.baseQuery import BaseQuery

class ragQuery(BaseQuery):
    def _process_nodes(self, nodes: List) -> Tuple[dict[str, str], float]:
        """
        標準的なRAGのノード処理

        Args:
            nodes (List): 処理対象のノードリスト

        Returns:
            Tuple[str, List[float]]: (処理済みコンテキスト, 類似度スコアリスト)
        """
        results = {
            "context": "",
            "user_query": ""
        }
        similarities = []

        for idx, node in enumerate(nodes):
            results["context"] += f"""\nContext number {idx+1} (score: {node.score}): \n{node.text}"""
            similarities.append(node.score)

        similarity = float(np.mean(similarities)) if len(similarities) > 0 else 0.0

        return results, similarity

    def _fetch_pinecone_indexes(self, prompt: str) -> Tuple[dict[str, str], float]:
        """
        ベクトルDBからノードを取得

        Args:
            prompt (str): ユーザの入力プロンプト

        Returns:
            RetrieverQueryEngine: 切り替え後のクエリエンジン
        """
        index_name = "rag-research"
        self.query_engine = self._initialize_pinecone(index_name)
        response = self.query_engine.query(prompt)
        related_nodes = response.source_nodes
        results, similarity = self._process_nodes(related_nodes)
        results["user_query"] = prompt

        return results, similarity

    def generate_response(self, prompt: str) -> Tuple[str, str, float]:
        """
        プロンプトに基づいてレスポンスを生成する

        Args:
            prompt (str): ユーザの入力プロンプト

        Returns:
            Tuple[str, str, float]: (レスポンス, コンテキスト, 類似度スコア)
        """
        try:
            results, similarity = self._fetch_pinecone_indexes(prompt)
            combined_query = self._create_prompt(results)
            chatgpt_response = self.client.chat.completions.create(
                model="o4-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a chatbot that modifies an old version of the {self.namespace} API to a new one. Relevant information must be followed."
                    },
                    {
                        "role": "user",
                        "content": combined_query
                    }
                ]
            )
            response = chatgpt_response.choices[0].message.content or ""
            return response, results["context"], similarity

        except Exception as e:
            raise Exception(f"クエリ処理中にエラーが発生しました: {str(e)}")

    def _create_prompt(self, results: dict[str, str]) -> str:
        """
        プロンプトの作成

        Args:
            results (str): コンテキスト情報
            user_query (str): ユーザークエリ
        """

        return self.prompt_template.format(
            context=results["context"],
            user_query=results["user_query"]
        )