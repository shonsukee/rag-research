import logging
from lib import BaseQuery
from lib.aprManager import APRManager
from lib.ioManager import IOManager

def main():
    logging.info("Starting APR processing...")
    args = IOManager().parse_arguments()

    query = BaseQuery(namespace=args.namespace, prompt_name=args.prompt_name)

    for data_type in args.data_types:
        APRManager().process_data_type(
            query,
            data_type,
            args.output_dir
        )

if __name__ == "__main__":
    main()