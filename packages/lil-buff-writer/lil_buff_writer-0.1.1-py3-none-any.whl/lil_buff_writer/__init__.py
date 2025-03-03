from typing import Iterable, Tuple, AsyncIterable
import logging

logger = logging.getLogger("lil_buff_writer")

try:
    import aiofiles
except ImportError:
    logger.error("async file writing requires aiofiles")


async def write_message_stream(
    messages: AsyncIterable[Tuple[bytes, bytes]],
    file_name: str,
    delimiter: bytes = b"/",
):
    """
    Write messages to a file in the following format:
    <name: bytes><delimiter: bytes><size: u32><content: bytes>

    name is a label for the message
    content is the actual message

    :param messages: An async iterable of tuples containing the name and content of the message
    :param file_name: The name of the file to write the messages to
    """
    buffer = bytearray()
    async for name, content in messages:
        buffer.extend(name)
        buffer.extend(delimiter)
        buffer.extend(len(content).to_bytes(4, "little"))
        buffer.extend(content)

    async with aiofiles.open(file_name, "wb") as f:
        await f.write(buffer)


async def write_messages(
    messages: Iterable[Tuple[bytes, bytes]], file_name: str, delimiter: bytes = b"/"
):
    """
    Write messages to a file in the following format:
    <name: bytes><delimiter: bytes><size: u32><content: bytes>

    name is a label for the message
    content is the actual message

    :param messages: An iterable of tuples containing the name and content of the message
    :param file_name: The name of the file to write the messages to
    """
    buffer = bytearray()
    for name, content in messages:
        buffer.extend(name)
        buffer.extend(delimiter)
        buffer.extend(len(content).to_bytes(4, "little"))
        buffer.extend(content)

    async with aiofiles.open(file_name, "wb") as f:
        await f.write(buffer)


def write_messages_sync(
    messages: Iterable[Tuple[bytes, bytes]], file_name: str, delimiter: bytes = b"/"
):
    buffer = bytearray()
    for name, content in messages:
        buffer.extend(name)
        buffer.extend(delimiter)
        buffer.extend(len(content).to_bytes(4, "little"))
        buffer.extend(content)

    with open(file_name, "wb") as f:
        f.write(buffer)


def each_chunk(stream, delimiter: bytes = b"/") -> Iterable[Tuple[bytes, bytes]]:
    """
    Read messages from a stream in the following format:
    <name: bytes><delimiter: bytes><size: u32><content: bytes>

    :param stream: The stream to read from
    :return: An iterable of tuples containing the name and content of the message
    """
    buffer = b""

    while True:
        chunk = stream.read(4096)
        if not chunk:
            break
        buffer += chunk

        while delimiter in buffer:
            name, buffer = buffer.split(delimiter, 1)

            if len(buffer) < 4:
                # Ensure we have at least 4 bytes for size
                buffer += stream.read(4 - len(buffer))
                if len(buffer) < 4:
                    logger.error("Malformed data")
                    return  # Malformed data

            size = int.from_bytes(buffer[:4], "little")
            buffer = buffer[4:]

            while len(buffer) < size:
                try:
                    chunk = stream.read(size - len(buffer))
                    if not chunk:
                        return  # Incomplete message
                    buffer += chunk
                except Exception as e:
                    logger.error(f"Error reading message: {e}")
                    return

            yield name, buffer[:size]
            buffer = buffer[size:]
