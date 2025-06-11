from typing import Tuple, Optional, List, Dict
from abc import ABC, abstractmethod
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
    def __init__(self, namespace: Optional[str] = None, prompt_name: Optional[str] = None):
        """
        BaseQueryクラスの初期化

        Args:
            namespace (Optional[str]): Pineconeのネームスペース
            prompt_name (Optional[str]): プロンプトテンプレートのディレクトリパス
        """
        load_dotenv()
        self.namespace = namespace
        self.prompt_name = prompt_name
        self.client = OpenAI()
        self.query_engine = self._initialize_pinecone()
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
        if not self.prompt_name:
            raise ValueError("prompt_nameが指定されていません")

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
    def _process_nodes(self, nodes: List) -> Tuple[Dict[str, str], float]:
        """
        ノードの処理を行う抽象メソッド

        Args:
            nodes (List): 処理対象のノードリスト

        Returns:
            Tuple[Dict[str, str], float]: (処理済みコンテキスト, 類似度スコア)
        """
        pass
