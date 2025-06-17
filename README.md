# RAG
REST API誤用を対象としたRAGの自動修正ツールです．

## 機能
- REST API仕様をベクトルDBへ格納
- 単純なLLMを利用した自動修正
- RAGによる自動修正
- DB拡張RAGによる自動修正

## 使用方法
### 初期化
```
$ git clone https://github.com/shonsukee/rag-research.git

$ python3 -m venv myenv

$ pip install -r requirements.txt
```

### インデックスの準備
#### Pinecone Indexの設定
1. Create Index押下
2. index nameの入力
3. text-embedding-3-smallを選択して，Dimensionを1536に設定
4. その他は変えずにCreate Index

> [!WARNING]
> ※ 無料だとIndexは5つまでしか設定できない

#### コンテキスト格納コマンド
> [!NOTE]
> `/dataset`にプロバイダ名と仕様URLをあらかじめ格納しておく！
> fitbit, switchbotは対応済み

- [Pinecone](https://app.pinecone.io/)に作成したインデックスへ格納する

- all
    - URLから取得した情報をそのままDBへ格納する
- separate
    - URLから取得した情報をコード片と自然言語に分割する
    - その後，指定されたバージョンのDBへ格納する
```
$ make store name=<project-name> version=<latest || outdated> method=<all || separate> index-name=<index-name>
```
switchbotの非推奨仕様をそのままcontextという名前のDBに格納するコマンド
```
$ make store name=switchbot version=outdated method=all index-name=context
```

### 自動バグ修正の適用
- プロンプトテンプレートを指定して自動バグ修正を実施
- 詳細は`/prompt`のテンプレート集を確認
```
$ make apr name=<project-name> types=<commit || issue || pull-request> out=<output-directory> prompt-name=<prompt-template-file-name>
```
```
$ make apr name=switchbot types=commit out=./result/llm prompt-name=llm
```
