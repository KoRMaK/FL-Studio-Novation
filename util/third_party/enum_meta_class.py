"""
Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 Python Software Foundation;
All Rights Reserved

- Note
Inspired by the EnumMeta metaclass in the python standard library.
Similarities in approach can be found in the `__new__` method.
"""
from util.enum_item import EnumItem


class EnumMetaClass(type):
    def __new__(mcs, name, bases, attributes):
        # Extracts the non dunder methods from attributes list in order
        # to create the enum items
        enum_map = {}
        for attribute_name, attribute_value in attributes.items():
            if not attribute_name.startswith("__"):
                enum_map[attribute_name] = attribute_value

        for attribute_name in enum_map.keys():
            attributes.pop(attribute_name)

        # Creates derived enum class
        enum_class = super().__new__(mcs, name, bases, attributes)

        class EnumClassItem(EnumItem):
            pass

        enum_class.Item = EnumClassItem

        enum_item_map = {}

        # Adds enum items to derived enum class
        for attribute_name, attribute_value in enum_map.items():
            enum_item = enum_class.Item(mcs, attribute_name, attribute_value)
            setattr(enum_class, attribute_name, enum_item)
            enum_item_map[attribute_name] = enum_item

        enum_class.enum_item_map = enum_item_map

        return enum_class

    def __str__(cls):
        return f"<enum '{cls.__name__}'>"

    def __iter__(self):
        self.enum_map_iter = iter(getattr(self, "enum_item_map", {}).values())
        return self.enum_map_iter

    def __next__(self):
        self.enum_map_iter = next(self.enum_map_iter)
        return self.enum_map_iter
