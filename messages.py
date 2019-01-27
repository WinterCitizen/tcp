from enum import Enum
from funcy import post_processing
from functools import reduce


class SourceState(Enum):
    IDLE = b'\x01'
    ACTIVE = b'\x02'
    RECHARGE = b'\x03'


class SourceMessageProcessor:
    HEADER_BYTES = 1
    MESSAGE_NUMBER_BYTES = 2
    SOURCE_ID_BYTES = 8
    SOURCE_STATE_BYTES = 1
    FIELDS_COUNT_BYTES = 1
    FIELD_NAME_BYTES = 8
    FIELD_VALUE_BYTES = 4
    SIGN_BYTES = 1

    def __init__(self, stream):
        self.stream = stream

    async def __get_fields(self, stream, fields_count):
        result = []
        for _ in range(self.__bytes_to_int(fields_count)):
            key = await stream.read_bytes(self.FIELD_NAME_BYTES)
            value = await stream.read_bytes(self.FIELD_VALUE_BYTES)

            result.append([key, value])

        return result

    def __bytes_to_int(self, value):
        return int.from_bytes(value, byteorder='big')

    def __int_to_bytes(self, value):
        if value < 256:
            return value.to_bytes(1, 'big')
        elif value < 256 * 256:
            return value.to_bytes(2, 'big')
        else:
            raise ValueError('Passed integer is too big')

    def __decode_ascii(self, value):
        return value.decode('ascii')

    def __encode_ascii(self, value):
        return value.encode('ascii')

    @post_processing(dict)
    def __fields_to_dict(self, fields):
        for key, value in fields:
            yield self.__decode_ascii(key), self.__decode_ascii(value)

    @post_processing(list)
    def __dict_to_fields(self, data):
        for key, value in data.items():
            yield self.__encode_ascii(key), self.__encode_ascii(value)

    def __xor(self, a, b):
        return a ^ b

    def sign(self, content):
        int_signature = reduce(self.__xor, content)

        return self.__int_to_bytes(int_signature)

    def signature_valid(self, content, signature):
        return reduce(self.xor, content) == signature

    def to_python(self, data):
        return dict(
            header=self.__bytes_to_int(data['header']),
            message_number=self.__bytes_to_int(data['message_number']),
            source_id=self.__decode_ascii(data['source_id']),
            source_state=SourceState(data['source_state']),
            fields_count=self.__bytes_to_int(data['fields_count']),
            fields=self.__fields_to_dict(data['fields']),
            sign=data['sign'],
        )

    def __flatten_fields(self, fields):
        for key, value in fields:
            yield key
            yield value

    def __join_data(self, data):
        return b''.join([
            data['header'],
            data['message_number'],
            data['source_id'],
            data['source_state'],
            data['fields_count'],
            b''.join(self.__flatten_fields(data['fields'])),
        ])

    def validate_signature(self, data):
        data = data.copy()

        sign = data.pop('sign')
        content = self.__join_data(data)

        if not self.signature_valid(content, sign):
            raise ValueError('Signature is invalid')

    async def get_message(self):
        header = await self.stream.read_bytes(self.HEADER_BYTES)
        message_number = (
            await self.stream.read_bytes(self.MESSAGE_NUMBER_BYTES))
        source_id = await self.stream.read_bytes(self.SOURCE_ID_BYTES)
        source_state = await self.stream.read_bytes(self.SOURCE_STATE_BYTES)
        fields_count = await self.stream.read_bytes(self.FIELDS_COUNT_BYTES)
        fields = await self.__get_fields(self.stream, fields_count)
        sign = await self.stream.read_bytes(self.SIGN_BYTES)

        return dict(
            header=header,
            message_number=message_number,
            source_id=source_id,
            source_state=source_state,
            fields_count=fields_count,
            fields=fields,
            sign=sign,
        )

    def to_bytes(self, data):
        data = dict(
            header=self.__int_to_bytes(data['header']),
            message_number=self.__int_to_bytes(data['message_number']),
            source_id=self.__encode_ascii(data['source_id']),
            source_state=data['source_state'],
            fields_count=self.__int_to_bytes(data['fields_count']),
            fields=self.__dict_to_fields(data['fields']),
        )
        content = self.__join_data(data)
        signature = self.sign(content)

        return b''.join([content, signature])
