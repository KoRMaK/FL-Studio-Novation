from util.third_party.enum_meta_class import EnumMetaClass


class Enum(metaclass=EnumMetaClass):
    def __str__(self):
        return f"{self.__class__.__name__}.{self._name_}"

    @classmethod
    def item(cls):
        return

    def __new__(cls, value):
        for enum_item in cls:
            if value == enum_item.value:
                return enum_item
        return None
