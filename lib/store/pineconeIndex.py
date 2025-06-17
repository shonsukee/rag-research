from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core import Document
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
import logging
import os
import sys
from typing import List

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

class PineconeIndex:
    """
    コンテキストをPineconeに格納するクラス
    このクラスは、Pineconeにドキュメントを格納します。
    """

    def __init__(self, namespace) -> None:
        # ログレベルの設定
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        api_key = os.environ.get('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PineconeのAPIキーが見つかりません。'.env'ファイルにPINECONE_API_KEYを設定してください。")

        self.pc = Pinecone(api_key=api_key)
        self.namespace = namespace

    def store(self, documents: List[Document], index_name: str) -> None:
        """
        ドキュメントをPineconeに格納する

        Args:
            documents (List[Document]): 格納するドキュメントのリスト
            index_name (str): Pineconeのインデックス名
        """
        try:
            pinecone_index = self.pc.Index(index_name)
            Settings.chunk_size = CHUNK_SIZE
            Settings.chunk_overlap = CHUNK_OVERLAP

            # Embeddingモデルの設定
            embed_model = OpenAIEmbedding(
                model="text-embedding-3-small",
                embed_batch_size=100
            )
            Settings.embed_model = embed_model

            vector_store = PineconeVectorStore(
                pinecone_index=pinecone_index,
                namespace=self.namespace
            )

            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            VectorStoreIndex.from_documents(
                documents=documents, storage_context=storage_context
            )

            logging.info(f"ドキュメントをPineconeの'{index_name}'インデックスに格納しました！")
        except Exception as e:
            logging.error(f"ドキュメントの格納中にエラーが発生しました: {e}")

