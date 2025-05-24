from typing import Tuple, Optional, List
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

    @abstractmethod
    def _process_nodes(self, nodes: List) -> Tuple[dict[str, str], float]:
        """
        ノードの処理を行う抽象メソッド

        Args:
            nodes (List): 処理対象のノードリスト

        Returns:
            Tuple[str, List[float]]: (処理済みコンテキスト, 類似度スコアリスト)
        """
        pass
