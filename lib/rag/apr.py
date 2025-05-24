import os
from lib.rag import ragQuery
from lib.aprManager import APRManager
from lib.ioManager import IOManager

def main():
    print("running...")
    args = IOManager().parse_arguments()

    # プロンプトディレクトリが指定されていない場合は、現在のディレクトリを使用
    prompt_dir = args.prompt_dir or os.path.dirname(os.path.abspath(__file__))
    query = ragQuery(namespace=args.namespace, prompt_dir=prompt_dir)

    for data_type in args.data_types:
        APRManager().process_data_type(
            query,
            args.namespace,
            data_type,
            args.output_dir
        )

if __name__ == "__main__":
    main()
