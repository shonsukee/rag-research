import argparse
import os
from typing import List
from lib.store.context import Context

def main() -> None:
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Pineconeへのデータ格納スクリプト')
    parser.add_argument('--namespace', type=str, required=True, help='対象のネームスペース(例: switchbot, fitbit)')
    parser.add_argument('--version', type=str, required=True, choices=['latest', 'outdated'], help='バージョン(latest または outdated)')
    parser.add_argument('--method', type=str, required=True, choices=['all', 'separate'], help='抽出対象(all: 全てのURL, separate: URLごとに分ける)')
    args = parser.parse_args()

    # プロジェクトのルートディレクトリを取得
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

    # URLリストの読み込み
    url_list: List[str] = []
    file_path = os.path.join(project_root, 'dataset', args.namespace, 'url', f"{args.version}.txt")
    with open(file_path, 'r') as file:
        url_list = [line.strip() for line in file.readlines()]

    # コンテキスト抽出の実行
    context = Context(args.namespace, args.version)

    if args.method == 'all':
        context.extract(url_list)
    elif args.method == 'separate':
        context.separate(url_list)

if __name__ == "__main__":
    main()