import os
from typing import Tuple, List
from lib.baseQuery import BaseQuery

class LLMQuery(BaseQuery):
    def _process_nodes(self):
        pass

    def _create_prompt(self, results: dict[str, str]) -> str:
        """
        プロンプトの作成

        Args:
            results (dict[str, str]): コンテキスト情報

        Returns:
            str: 生成されたプロンプト
        """
        return self.prompt_template.format(
            link=results["link"],
            user_query=results["user_query"]
        )

    def _fetch_links(self, namespace: str | None) -> str:
        """
        datasetからリンクを取得する

        Args:
            namespace (str | None): ネームスペース

        Returns:
            str: リンク
        """
        if namespace is None:
            return ""

        links = []
        directory_path = f"./dataset/{namespace}/url"
        for filename in os.listdir(directory_path):
            language = filename.split(".")[-1]
            if language == "txt":
                with open(f"{directory_path}/{filename}", "r", encoding="utf-8") as file:
                    content = file.read()
                    links.append(content)
        return "\n".join(links)

    def generate_response(self, prompt: str) -> Tuple[str, str, float]:
        """
        プロンプトに基づいてレスポンスを生成する

        Args:
            prompt (str): ユーザの入力プロンプト

        Returns:
            Tuple[str, str, float]: (レスポンス, -, 0)
        """
        try:
            links = self._fetch_links(self.namespace)
            results = {
                "link": links,
                "user_query": prompt
            }
            combined_query = self._create_prompt(results)
            print("Create prompt...")
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
            print("Generate response by o4-mini...")
            response = chatgpt_response.choices[0].message.content or ""
            return response, links, 0

        except Exception as e:
            raise Exception(f"クエリ処理中にエラーが発生しました: {str(e)}")
