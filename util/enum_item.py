from util.third_party.dynamic_class_attribute import DynamicClassAttribute


class EnumItem:
    def __init__(self, enum_class_name, name, value):
        self.enum_class_name = enum_class_name
        self._name_ = name
        self._value_ = value

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.value == other.value
        if isinstance(other, type(self.value)):
            return self.value == other
        return False

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.value < other.value
        if isinstance(other, type(self.value)):
            return self.value < other
        return False

    def __gt__(self, other):
        if isinstance(other, type(self)):
            return self.value > other.value
        if isinstance(other, type(self.value)):
            return self.value > other
        return False

    def __le__(self, other):
        return not (self > other)

    def __ge__(self, other):
        return not (self < other)

    def __and__(self, other):
        if isinstance(other, type(self)):
            return self.value & other.value
        return self.value & other

    def __or__(self, other):
        if isinstance(other, type(self)):
            return self.value | other.value
        return self.value | other

    def __xor__(self, other):
        if isinstance(other, type(self)):
            return self.value ^ other.value
        return self.value ^ other

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self._name_)

    def __repr__(self):
        return f"<{self.enum_class_name}.{self.name}: '{self}'>"

    @DynamicClassAttribute
    def name(self):
        """The name of the Enum member."""
        return self._name_

    @DynamicClassAttribute
    def value(self):
        """The value of the Enum member."""
        return self._value_
