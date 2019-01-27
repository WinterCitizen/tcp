# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot, GenericRepr


snapshots = Snapshot()

snapshots['test_source_message_processor_to_bytes 1'] = b'\x01\x01,aaaaaaaa\x02\x02aaaaaaaaaaaabbbbbbbbbbbb,'

snapshots['test_source_message_processor_to_python 1'] = {
    'fields': {
        'aaaaaaaa': 'aaaa',
        'bbbbbbbb': 'bbbb'
    },
    'fields_count': 2,
    'header': 1,
    'message_number': 300,
    'sign': b',',
    'source_id': 'aaaaaaaa',
    'source_state': GenericRepr("<SourceState.ACTIVE: b'\x02'>")
}
