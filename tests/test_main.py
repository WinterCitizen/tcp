import socket

import pytest
from main import LISTENERS_PORT, SOURCES_PORT, TCPServer
from tests.utils import IOStreamDummy
from messages import SourceMessageProcessor, SourceState


@pytest.fixture
def source_message_data():
    return dict(
        header=1,
        message_number=300,
        source_id='a'*8,
        source_state=SourceState.ACTIVE.value,
        fields_count=2,
        fields=dict(
            aaaaaaaa='aaaa',
            bbbbbbbb='bbbb'),
        sign=b',')


@pytest.fixture
def source_message_content():
    return b'\x01\x01,aaaaaaaa\x02\x02aaaaaaaaaaaabbbbbbbbbbbb,'


@pytest.mark.asyncio
async def test_source_message_processor_to_bytes(
        source_message_data, snapshot):
    processor = SourceMessageProcessor(None)
    content = processor.to_bytes(source_message_data)

    snapshot.assert_match(content)


@pytest.mark.asyncio
async def test_source_message_processor_to_python(
        source_message_content, snapshot):
    stream = IOStreamDummy(SOURCES_PORT, source_message_content)
    processor = SourceMessageProcessor(stream)

    message = await processor.get_message()
    data = processor.to_python(message)

    snapshot.assert_match(data)
