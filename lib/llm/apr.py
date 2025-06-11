import os
from lib.llm import LLMQuery
from lib.aprManager import APRManager
from lib.ioManager import IOManager

def main():
    print("running...")
    args = IOManager().parse_arguments()

    # プロンプトディレクトリが指定されていない場合は、現在のディレクトリを使用
    prompt_name = args.prompt_name or os.path.dirname(os.path.abspath(__file__))
    query = LLMQuery(namespace=args.namespace, prompt_name=prompt_name)

    for data_type in args.data_types:
        APRManager().process_data_type(
            query,
            args.namespace,
            data_type,
            args.output_dir
        )

if __name__ == "__main__":
    main()