import logging
from typing import Optional, List
import string
from abc import ABC
from dotenv import load_dotenv
from llama_index.core.postprocessor.llm_rerank import LLMRerank
from llama_index.core.schema import NodeWithScore
from openai import OpenAI
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, get_response_synthesizer, Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
import os

class BaseQuery(ABC):
    def __init__(self, namespace: Optional[str] = None, prompt_name: Optional[str] = None):
        """
        BaseQueryクラスの初期化

        Args:
            namespace (Optional[str]): Pineconeのネームスペース
            prompt_name (Optional[str]): プロンプトテンプレートのディレクトリパス
        """
        if namespace is None:
            raise ValueError("namespaceが指定されていません")
        if prompt_name is None:
            raise ValueError("prompt_nameが指定されていません")

        load_dotenv()
        self.namespace = namespace
        self.prompt_name = prompt_name
        self.client = OpenAI()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """
        プロンプトテンプレートをファイルから読み込む

        Returns:
            str: プロンプトテンプレート

        Raises:
            ValueError: prompt_nameがNoneの場合
            FileNotFoundError: プロンプトファイルが見つからない場合
            Exception: その他のエラー
        """
        try:
            prompt_path = './lib/prompt/' + self.prompt_name + '.md'
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {prompt_path}")
        except Exception as e:
            raise Exception(f"プロンプトテンプレートの読み込みに失敗しました: {str(e)}")

    def _initialize_pinecone(self, index_name: str = "rag-research") -> RetrieverQueryEngine:
        """
        Pineconeの初期化とクエリエンジンの設定

        Args:
            index_name (str): Pineconeのインデックス名

        Returns:
            RetrieverQueryEngine: 設定済みのクエリエンジン

        Raises:
            ValueError: 環境変数が設定されていない場合
            Exception: その他のエラー
        """
        try:
            api_key = os.environ.get("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY環境変数が設定されていません")

            pc = Pinecone(api_key=api_key)
            pinecone_index = pc.Index(index_name)

            # Embeddingモデルの設定
            embed_model = OpenAIEmbedding(
                model="text-embedding-3-large",
                embed_batch_size=100
            )
            Settings.embed_model = embed_model

            vector_store = PineconeVectorStore(
                pinecone_index=pinecone_index,
                add_sparse_vector=True,
                namespace=self.namespace
            )

            index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
            vector_retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=60
            )

            response_synthesizer = get_response_synthesizer()
            return RetrieverQueryEngine(
                retriever=vector_retriever,
                response_synthesizer=response_synthesizer,
                node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.0)],
            )
        except Exception as e:
            raise Exception(f"Pineconeの初期化に失敗しました: {str(e)}")

    def _fetch_vars(self) -> List[str]:
        """
        プロンプトテンプレートから変数を取得する

        Returns:
            List[str]: プロンプトテンプレートの変数リスト
        """
        return [v[1] for v in string.Formatter().parse(self.prompt_template) if v[1] is not None]

    def _create_prompt(self, results: dict[str, str]) -> str:
        """
        プロンプトの作成

        Args:
            results (Dict[str, str]): コンテキスト情報を含む辞書

        Returns:
            str: 生成されたプロンプト

        Raises:
            KeyError: 必要なキーがresultsに存在しない場合
            ValueError: プロンプトテンプレートのフォーマットに失敗した場合
        """
        try:
            # 必要な変数が全て存在するか確認
            missing_vars = [var for var in self._fetch_vars() if var not in results]
            if missing_vars:
                raise KeyError(f"プロンプトテンプレートに必要な変数が不足しています: {missing_vars}")

            return self.prompt_template.format(**results)
        except KeyError as e:
            raise KeyError(f"プロンプト生成に必要なキーが存在しません: {str(e)}")
        except Exception as e:
            raise ValueError(f"プロンプトの生成に失敗しました: {str(e)}")

    def generate_response(self, prompt: str) -> str:
        """
        プロンプトに基づいてレスポンスを生成する

        Args:
            prompt (str): 生成されたプロンプト

        Returns:
            str: 生成されたレスポンス
        """
        try:
            logging.info("Generate response by o4-mini...")
            chatgpt_response = self.client.chat.completions.create(
                model="o4-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a chatbot that modifies an old version of the {self.namespace} API to a new one. Relevant information must be followed."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            response = chatgpt_response.choices[0].message.content or ""
            return response

        except Exception as e:
            raise Exception(f"クエリ処理中にエラーが発生しました: {str(e)}")

    def _process_nodes(self, nodes: List) -> str:
        """
        ノードの処理を行う抽象メソッド

        Args:
            nodes (List): 処理対象のノードリスト

        Returns:
            str: 処理済みのノードテキスト
        """
        node_prompt = ""

        for idx, node in enumerate(nodes, 1):
            if idx != 1:
                node_prompt += "\n\n"
            node_prompt += f"【Context No.{idx}】\n[similarity: {node.score}]\n{node.text}"

        return node_prompt

    def _fetch_pinecone_indexes(self, index_name: str, user_query: str) -> List[NodeWithScore]:

        """
        Pineconeインデックスからデータを取得する

        Args:
            index_name (str): Pineconeのインデックス名
            user_query (str): ユーザークエリ

        Returns:
            str: 取得したデータのテキスト
        """
        if '_' in index_name:
            index_name = index_name.replace('_', '-')

        query_engine = self._initialize_pinecone(index_name)
        response = query_engine.query(user_query)
        return response.source_nodes

    def rerank(self, nodes: List, query: str) -> List[NodeWithScore] | None:
        """
        TODO: _fetch_pinecone_indexesの結果を受けて実施
        ノードを再ランク付けする

        Args:
            nodes (List): 処理対象のノードリスト

        Returns:
            str: 再ランク付けされたノードのテキスト
        """
        ranker = LLMRerank(
            choice_batch_size=5, top_n=60, llm=LlamaOpenAI(model="gpt-4o")
        )

        if not nodes:
            return None

        return ranker.postprocess_nodes(
            nodes, query_str=query
        )

    def _fetch_links(self) -> str:
        """
        datasetからリンクを取得する

        Returns:
            str: 取得したリンクのテキスト
        """
        links = []
        directory_path = f"./dataset/{self.namespace}/url"
        for filename in os.listdir(directory_path):
            language = filename.split(".")[-1]
            if language == "txt":
                with open(f"{directory_path}/{filename}", "r", encoding="utf-8") as file:
                    content = file.read()
                    links.append(content)
        return "\n".join(links)
