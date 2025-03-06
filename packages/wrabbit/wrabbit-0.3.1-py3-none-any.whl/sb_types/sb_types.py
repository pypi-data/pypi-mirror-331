class NodeType:
    type_ = None

    def __init__(self, optional=False, **kwargs):
        self.optional = optional

    def is_optional(self):
        return self.optional

    def to_optional(self):
        self.optional = True

    def to_required(self):
        self.optional = False

    def serialize(self):
        if self.optional:
            return [
                "null",
                self._dict
            ]
        else:
            return self._dict

    @property
    def _dict(self):
        return self.type_


class CompositeType(list, NodeType):
    def serialize(self):
        if self.optional:
            return [
                "null",
                *self._dict
            ]
        else:
            return self._dict

    @property
    def _dict(self):
        return self


class EnumType(NodeType):
    type_ = "enum"

    def __init__(self, name: str, symbols: list, **kwargs):
        self.name = name
        self.symbols = symbols
        super().__init__(**kwargs)

    @property
    def _dict(self):
        return {
            "type": self.type_,
            "name": self.name,
            "symbols": self.symbols
        }


class ArrayType(NodeType):
    type_ = "array"

    def __init__(self, items: list, **kwargs):
        self.items = items
        super().__init__(**kwargs)

    @property
    def _dict(self):
        return {
            "type": self.type_,
            "items": self.items,
        }


class RecordType(NodeType):
    type_ = "record"

    def __init__(self, fields: list, name: str, **kwargs):
        self.fields = fields
        self.name = name
        super().__init__(**kwargs)

    @property
    def _dict(self):
        return {
            "type": self.type_,
            "name": self.name,
            "fields": self.fields,
        }


class StringType(NodeType):
    type_ = "string"


class FileType(NodeType):
    type_ = "File"


class DirectoryType(NodeType):
    type_ = "Directory"


class IntegerType(NodeType):
    type_ = 'int'


class FloatType(NodeType):
    type_ = 'float'


class BooleanType(NodeType):
    type_ = 'boolean'

