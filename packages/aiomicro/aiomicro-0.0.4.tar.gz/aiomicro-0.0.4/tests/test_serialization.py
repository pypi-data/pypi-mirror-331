import pytest
from mia.rpc.message import PickleSerializer, JsonSerializer
from mia.exceptions import RpcMessageError


@pytest.fixture
def pickle_serializer():
    return PickleSerializer()


@pytest.fixture
def json_serializer():
    return JsonSerializer()


def test_pickle_serialization(pickle_serializer):
    test_data = {"key": "value", "number": 42}
    serialized = pickle_serializer.serialize(test_data)
    deserialized = pickle_serializer.deserialize(serialized)
    assert deserialized == test_data


def test_json_serialization(json_serializer):
    test_data = {"key": "value", "number": 42}
    serialized = json_serializer.serialize(test_data)
    deserialized = json_serializer.deserialize(serialized)
    assert deserialized == test_data


def test_serialization_error_handling(pickle_serializer):
    class UnserializableObject:
        def __getstate__(self):
            raise TypeError("Cannot serialize")

    with pytest.raises(TypeError):
        pickle_serializer.serialize(UnserializableObject())
