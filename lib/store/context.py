import logging
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup, Tag
from typing import List
import re
import html2text
from llama_index.core import Document

from lib.store.pineconeIndex import PineconeIndex
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class Context:
    """
    仕様情報を抽出するクラス
    このクラスは、指定されたURLから仕様情報を抽出します。
    """

    def __init__(self, namespace: str, version: str):
        """
        コンテキスト抽出クラスの初期化

        Args:
            namespace (str): 対象のネームスペース（例：'switchbot', 'fitbit'）
            version (str): バージョン（'latest' または 'outdated'）
        """
        load_dotenv()
        self.pinecone_index = PineconeIndex(namespace)
        self.version = version

    def extract(self, url_list: List[str], index_name: str = "rag-research") -> None:
        """
        URLからスクレイピングし, テキストを抽出してPineconeに格納

        Args:
            url_list (List[str]): URLのリスト
            index_name (str): Pinecone DBのindex名
        """
        # 各URLからスクレイピングを行う
        content = []

        md_converter = html2text.HTML2Text()
        md_converter.ignore_links = False

        for url in url_list:
            try:
                html = requests.get(url).text
                soup = BeautifulSoup(html, "html.parser")

                tag = 'article'
                raw_context = soup.find(tag)

                if not raw_context or not isinstance(raw_context, Tag):
                    logging.warning(f"{url}: <{tag}>タグが見つかりませんでした。")
                    raw_context = self.extract_with_browser(url)

                # Markdownテキストの整形
                markdown_text = md_converter.handle(str(raw_context))
                while ' \n' in markdown_text:
                    markdown_text = re.sub(r' \n', '\n', markdown_text)
                markdown_text = re.sub(r'\n\n', '\n', markdown_text)

                content.append(markdown_text.strip())

            except Exception as e:
                print(f"{url}: \n<{tag}>タグが見つかりませんでした。\n")
                print(f"{e}")

        documents = [Document(text=t) for t in content]
        # ドキュメントをファイルに書き出す
        # output_dir = f"./dataset/context/{self.version}"
        # os.makedirs(output_dir, exist_ok=True)

        # for i, doc in enumerate(documents):
        #     output_path = os.path.join(output_dir, f"document_{i}.txt")
        #     with open(output_path, "w", encoding="utf-8") as f:
        #         f.write(doc.text)

        # Pineconeに格納
        self.pinecone_index.store(documents, index_name)

    def extract_with_browser(self, url: str) -> str:
        """
        Selenium を使って HTML 形式の仕様を抽出

        Args:
            url (str): URL

        Returns:
            str: 抽出されたHTML。失敗した場合は空文字列
        """

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            print(driver.page_source)
            element = driver.find_element(By.TAG_NAME, "article")
            html = element.get_attribute("innerHTML")
            if not html:
                logging.warning(f"{url}: <article>タグが見つかりませんでした。")
                return ""

            return html
        except Exception as e:
            logging.warning(f"{url}: Seleniumで抽出できませんでした: {e}")
            return ""


    def separate(self, url_list: List[str]) -> None:
        """
        URLからスクレイピングし, コードブロックと自然言語を分割してPineconeに格納

        Args:
            url_list (List[str]): URLのリスト

        Note:
            自然言語は'{version}-lang'、コードブロックは'{version}-code'のネームスペースに格納されます
        """
        natural_languages: List[str] = []
        code_blocks: List[str] = []

        for url in url_list:
            try:
                html = requests.get(url).text
                soup = BeautifulSoup(html, "html.parser")
                article = soup.find('article')

                if not article or not isinstance(article, Tag):
                    logging.warning(f"{url}: <article>タグが見つかりませんでした。")
                    html = self.extract_with_browser(url)
                    if html:
                        article = BeautifulSoup(html, "html.parser")
                    else:
                        continue

                # コードを抽出して自然言語と分離
                for pre in article.find_all(['pre']):
                    code_blocks.append(pre.get_text())
                    pre.extract()

                # 残りの自然言語をMD形式で抽出
                md_converter = html2text.HTML2Text()
                md_converter.ignore_links = False
                markdown_text = md_converter.handle(str(article))

                # Markdownテキストの整形
                while ' \n' in markdown_text:
                    markdown_text = re.sub(r' \n', '\n', markdown_text)
                markdown_text = re.sub(r'\n\n', '\n', markdown_text)
                natural_languages.append(markdown_text.strip())

            except Exception as e:
                logging.error(f"{url}: 取得中にエラーが発生しました: {e}")

        # ドキュメントの作成
        n_documents = [Document(text=t) for t in natural_languages]
        c_documents = [Document(text=t) for t in code_blocks]

        # 出力ディレクトリの作成
        output_dir = f"./dataset/context/{self.version}"
        os.makedirs(output_dir, exist_ok=True)

        # 自然言語テキストの保存
        # for i, doc in enumerate(n_documents):
        #     output_path = os.path.join(output_dir, f"n_document_{i}.txt")
        #     with open(output_path, "w", encoding="utf-8") as f:
        #         f.write(doc.text)
        #     logging.info(f"自然言語ドキュメント{i}を保存: {doc.text[:100]}...")

        # コードブロックの保存
        # for i, doc in enumerate(c_documents):
        #     output_path = os.path.join(output_dir, f"c_document_{i}.txt")
        #     with open(output_path, "w", encoding="utf-8") as f:
        #         f.write(doc.text)
        #     logging.info(f"コードブロック{i}を保存: {doc.text[:100]}...")

        # Pineconeに格納
        self.pinecone_index.store(n_documents, f"{self.version}-lang")
        self.pinecone_index.store(c_documents, f"{self.version}-code")
