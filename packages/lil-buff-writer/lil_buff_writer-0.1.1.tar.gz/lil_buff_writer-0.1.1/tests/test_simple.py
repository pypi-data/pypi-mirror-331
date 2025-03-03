import pytest
import lil_buff_writer


@pytest.mark.asyncio
async def test_write_and_read_messages(tmp_path):
    test_file = tmp_path / "data.bin"

    messages = [
        (b"test", b"hello"),
        (b"data", b"world"),
        (b"chunked", b"message"),
        (b"another", b""),
        (b"last", b"bye"),
    ]

    await lil_buff_writer.write_messages(messages, str(test_file))

    decoded_messages = []

    with open(test_file, "rb") as f:
        for name, content in lil_buff_writer.each_chunk(f):
            decoded_messages.append((name, content))

    assert decoded_messages == messages


@pytest.mark.asyncio
async def test_write_and_read_messages_complex(tmp_path):
    test_file = tmp_path / "data.bin"

    messages = [
        (b"test.md", b"home/dir/hello_world.txt"),
        (b"data.bin", b"world"),
        (
            b"chunked.cs",
            b"here are a bunch of messages with file paths test/output.txt",
        ),
        (b"another.py", b""),
        (b"twice.rs", b""),
        (b"", b"this is a message with no name"),
        (
            b"last.ipynb",
            b"bye this is the last message \n\n\n lots of new lines \n path/to/file.txt",
        ),
    ]

    await lil_buff_writer.write_messages(messages, str(test_file))

    decoded_messages = []

    with open(test_file, "rb") as f:
        for name, content in lil_buff_writer.each_chunk(f):
            decoded_messages.append((name, content))

    assert decoded_messages == messages


@pytest.mark.asyncio
async def test_empty_messages(tmp_path):
    test_file = tmp_path / "empty.bin"
    await lil_buff_writer.write_messages([], str(test_file))

    with open(test_file, "rb") as f:
        chunks = list(lil_buff_writer.each_chunk(f))
        assert chunks == []


@pytest.mark.asyncio
async def test_single_message(tmp_path):
    test_file = tmp_path / "single.bin"
    messages = [(b"one", b"only")]
    await lil_buff_writer.write_messages(messages, str(test_file))

    with open(test_file, "rb") as f:
        chunks = list(lil_buff_writer.each_chunk(f))
        assert len(chunks) == 1
        assert chunks[0] == (b"one", b"only")


@pytest.mark.asyncio
async def test_large_message(tmp_path):
    test_file = tmp_path / "large.bin"
    large_content = b"a" * 10**8
    messages = [(b"large", large_content)]
    await lil_buff_writer.write_messages(messages, str(test_file))

    with open(test_file, "rb") as f:
        chunks = list(lil_buff_writer.each_chunk(f))
        assert len(chunks) == 1
        assert chunks[0] == (b"large", large_content)
