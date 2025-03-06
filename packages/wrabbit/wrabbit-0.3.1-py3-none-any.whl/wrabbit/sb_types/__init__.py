import yaml
from wrabbit.specification.node import (
    NodeType,
    EnumType,
    ArrayType,
    StringType,
    FileType,
    DirectoryType,
    FloatType,
    IntegerType,
    BooleanType,
    RecordType,
    CompositeType,
)


def represent_serializable_object(dumper, data):
    temp = data.serialize()
    if isinstance(temp, list):
        return dumper.represent_sequence('tag:yaml.org,2002:seq', temp)
    if isinstance(temp, dict):
        return dumper.represent_mapping('tag:yaml.org,2002:map', temp)
    if isinstance(temp, str):
        return dumper.represent_scalar('tag:yaml.org,2002:str', temp)


yaml.add_representer(EnumType, represent_serializable_object)
yaml.add_representer(ArrayType, represent_serializable_object)
yaml.add_representer(StringType, represent_serializable_object)
yaml.add_representer(FileType, represent_serializable_object)
yaml.add_representer(DirectoryType, represent_serializable_object)
yaml.add_representer(FloatType, represent_serializable_object)
yaml.add_representer(IntegerType, represent_serializable_object)
yaml.add_representer(BooleanType, represent_serializable_object)
yaml.add_representer(RecordType, represent_serializable_object)
yaml.add_representer(CompositeType, represent_serializable_object)
