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
$ git clone https://github.com/shonsukee/bachelor-research

$ python3 -m venv myenv

$ pip install -r requirements.txt
```

### ベクトルDBへの格納
- [Pinecone](https://app.pinecone.io/)で作成したインデックスに格納する

```
$ make store name=<project-name> version=<latest || outdated> method=<all || separate>

$ make store name=switchbot version=outdated method=all
```



### 自動バグ修正
```
$ make llm name=switchbot types=commit out=./result/llm prompt-dir=lib/llm

$ make rag name=switchbot types=commit out=./result/rag prompt-dir=lib/rag

$ make duplicate name=switchbot types=commit out=./result/duplicate prompt-dir=lib/duplicate_rag
```



## 実装方針メモ
- それぞれの手法にプロンプトを用意して，抽出先のDBをコマンドで指定することで実現
