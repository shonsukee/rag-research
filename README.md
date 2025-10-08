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

// (非推奨)venvでやる場合
$ python3 -m venv myenv
$ pip install -r requirements.txt
```

### インデックスの準備
#### Pinecone Indexの設定
1. Create Index押下
2. index nameの入力
    - index nameは`latest`, `deprecated`, `latest-natural-language`, `latest-code`...にすることを推奨します
3. text-embedding-3-largeを選択して，Dimensionを1536に設定
4. その他は変えずにCreate Index

> [!WARNING]
> ※ 無料だとIndexは5つまでしか設定できない

### ビルド
```
// ragという名前のimageを作成
$ docker build -t rag .
```

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
$ docker run --rm -v $(pwd):/app rag make store name=<project-name> version=<latest || deprecated> method=<all || separate> index-name=<index-name>
```
```
// switchbotの非推奨仕様をそのまま`deprecated`という名前のDBに格納するコマンド
$ docker run --rm -v $(pwd):/app rag make store name=switchbot version=deprecated method=all index-name=deprecated

// switchbotの最新仕様をコードと自然言語で分割して`latest-code`, `latest-natural-language`という名前のDBに格納するコマンド
$ docker run --rm -v $(pwd):/app rag make store name=switchbot version=latest method=separate index-name=latest

// switchbotの最新仕様, 非推奨仕様をそのまま`context`という名前のDBに格納するコマンド
$ docker run --rm -v $(pwd):/app rag make store name=switchbot version=latest method=all index-name=context
$ docker run --rm -v $(pwd):/app rag make store name=switchbot version=deprecated method=all index-name=context
```

### 自動バグ修正の適用
- プロンプトテンプレートを指定して自動バグ修正を実施
- 詳細は`/prompt`のテンプレート集を確認

```
$ docker run --rm -v $(pwd):/app rag make apr name=<project-name> types=<commits || issues || pull-requests> out=<output-directory> prompt-name=<prompt-template-file-name>
```
```
$ docker run --rm -v $(pwd):/app rag make apr name=switchbot types=commits out=./results prompt-name=llm

// switchbotのPRデータセットをtriple_latestというプロンプトに適用して`results`というディレクトリに出力
$ docker run --rm -v $(pwd):/app rag make apr name=switchbot types=pull-requests out=./results prompt-name=triple_latest
```
