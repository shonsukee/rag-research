# RAG
IoT のREST API誤用を対象としたRAGの自動修正ツールです．

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




### 自動バグ修正
```
$ make llm name=switchbot types=commit out=./result/llm prompt-dir=lib/llm

$ make rag name=switchbot types=commit out=./result/rag prompt-dir=lib/rag

$ make duplicate name=switchbot types=commit out=./result/duplicate prompt-dir=lib/duplicate_rag
```



## 実装方針メモ
- DBから抽出する数は今後2, 3...と変化するためそれに対応できるようにしたい
- ただ，プロンプトが異なるから全てのパターンに対して実装しなければいけなさそう
結論
- baseQueryにはDBからの取得メソッドを書いて
- それぞれのQuery内でループを回し，呼び出す感じにしよ