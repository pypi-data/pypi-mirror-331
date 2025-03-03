import argparse
from . import write_messages_sync, each_chunk
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lil_buff_writer:cli")


def main():
    parser = argparse.ArgumentParser(
        description="""
        A simple writing utility for storing and retrieving messages.
        Messages are formated as such `<name: bytes><delimiter: bytes><size: u32><content: bytes>`
                                     """,
        add_help=True,
    )

    parser.add_argument("file_name", type=str, help="The name of the file to use")
    parser.add_argument(
        "--encode",
        nargs="*",
        dest="file_names",
        type=str,
        help="The files to encode",
        required=False,
    )
    parser.add_argument(
        "--decode",
        type=str,
        dest="output_dir",
        help="Directory where the files will be decoded",
        required=False,
        const=".",
        nargs="?",
    )
    args = parser.parse_args()

    if args.file_names and args.output_dir:
        raise ValueError("Cannot encode and decode at the same time")

    if not args.file_names and not args.output_dir:
        raise ValueError("Must provide either --encode or --decode")

    if args.file_names:

        def message_stream():
            for file_name in args.file_names:
                with open(file_name, "rb") as f:
                    yield os.path.basename(file_name).encode(), f.read()

        logger.info(f"Encoding files: {args.file_names} to {args.file_name}")
        write_messages_sync(message_stream(), args.file_name)

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        with open(args.file_name, "rb") as f:
            for name, content in each_chunk(f):
                output_path = os.path.join(args.output_dir, name.decode())
                logger.info(
                    f"Decoding file: {name.decode()} from {args.file_name} to {output_path}"
                )

                with open(output_path, "wb") as of:
                    of.write(content)


if __name__ == "__main__":
    main()
