# lil_buff_writer

A simple writing utility for storing and retrieving messages.

Messages are formated as such `<name: bytes><delimiter: bytes><size: u32><content: bytes>`
This archive format aims to be light weight and easy to use.

Instead of writing out many files, you can pack them into one file.
Writing out a stream of messages to a single blob allows you to write to a single destination instead of searching for files later.


## Features
- Write messages to a file with labeled names and content.
- Parse each of the messages from a stream.

## Installation
```sh
pip install lil_buff_writer
```

## Usage

### Writing Messages

Using Python

```python
from lil_buff_writer import write_messages

messages = [(b"greeting", b"Hello, World!"), (b"farewell", b"Goodbye!")]
await write_messages(messages, "messages.dat")
```

Using the Command Line

```bash
python -m lil_buff_writer test.bin --encode file0.txt file1.md ...
```


### Reading Messages

Using Python

```python
from lil_buff_writer import read_messages

with open("messages.dat", "rb") as f:
    for name, content in read_messages(f):
        print(f"{name.decode()}: {content.decode()}")
```

Using the Command Line

```bash
python -m lil_buff_writer test.bin --decode [output_dir]
```

## License
Apache-2.0