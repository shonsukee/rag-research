from typing import Tuple, Optional
from abc import ABC, abstractmethod
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.vector_stores.pinecone import PineconeVectorStore
import os

class BaseQuery(ABC):
    def __init__(self, namespace: Optional[str] = None, prompt_dir: Optional[str] = None):
        """
        BaseQueryクラスの初期化

        Args:
            namespace (Optional[str]): Pineconeのネームスペース
            prompt_dir (Optional[str]): プロンプトテンプレートのディレクトリパス
        """
        load_dotenv()
        self.namespace = namespace
        self.prompt_dir = prompt_dir
        self.client = OpenAI()
        self.query_engine = self._initialize_pinecone()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """
        プロンプトテンプレートをファイルから読み込む

        Returns:
            str: プロンプトテンプレート
        """
        try:
            if self.prompt_dir:
                prompt_path = Path(self.prompt_dir) / "prompt.md"
            else:
                prompt_path = Path('.') / "prompt.md"

            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"プロンプトテンプレートの読み込みに失敗しました: {str(e)}")

    def _initialize_pinecone(self, index_name: str = "rag-research") -> RetrieverQueryEngine:
        """
        Pineconeの初期化とクエリエンジンの設定

        Returns:
            RetrieverQueryEngine: 設定済みのクエリエンジン
        """
        try:
            # NOTE: ベクトルDBの名前指定
            pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
            pinecone_index = pc.Index(index_name)

            vector_store = PineconeVectorStore(
                pinecone_index=pinecone_index,
                add_sparse_vector=True,
                namespace=self.namespace
            )

            index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
            vector_retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=20
            )

            response_synthesizer = get_response_synthesizer()
            return RetrieverQueryEngine(
                retriever=vector_retriever,
                response_synthesizer=response_synthesizer,
                node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.0)],
            )
        except Exception as e:
            raise Exception(f"Pineconeの初期化に失敗しました: {str(e)}")

    @abstractmethod
    def _create_prompt(self, results: dict[str, str], user_query: str) -> str:
        """
        プロンプトの作成

        Args:
            results (str): コンテキスト情報
            user_query (str): ユーザークエリ

        Returns:
            str: 生成されたプロンプト
        """
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> Tuple[str, str, float]:
        """
        プロンプトに基づいてレスポンスを生成する
        """
        pass

    # @abstractmethod
    # def _process_nodes(self, nodes: List) -> Tuple[str, List[float]]:
    #     """
    #     ノードの処理を行う抽象メソッド

    #     Args:
    #         nodes (List): 処理対象のノードリスト

    #     Returns:
    #         Tuple[str, List[float]]: (処理済みコンテキスト, 類似度スコアリスト)
    #     """
    #     pass

    # def query_index(self, user_query: str) -> Tuple[str, str, float]:
    #     """
    #     ユーザー入力に関連するインデックスを検索する関数

    #     Args:
    #         user_query (str): ユーザが修正したいコード

    #     Returns:
    #         Tuple[str, str, float]: (LLMからの回答, コンテキスト, 関連度の平均値)
    #     """
    #     try:
    #         # クエリ結果から関連ノードを取得
    #         response = self.query_engine.query(user_query)
    #         related_nodes = response.source_nodes

    #         # ノードの処理（サブクラスで実装）
    #         context, similarities = self._process_nodes(related_nodes)

    #         # 関連度の平均計算
    #         similarity = float(np.mean(similarities)) if len(similarities) > 0 else 0.0

    #         # プロンプトの生成
    #         combined_query = self._create_prompt(context, user_query)

    #         # OpenAI APIの呼び出し
    #         chatgpt_response = self.client.chat.completions.create(
    #             model="o4-mini",
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": f"You are a chatbot that modifies an old version of the {self.namespace} API to a new one. Relevant information must be followed."
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": combined_query
    #                 }
    #             ]
    #         )
    #         response = chatgpt_response.choices[0].message.content or ""

    #         return response, context, similarity

    #     except Exception as e:
    #         raise Exception(f"クエリ処理中にエラーが発生しました: {str(e)}")

