class PlainData:
    """
    Class decorator for classes with only plain data.

    Simplifies definitions of plain data structures and provides printing
    and comparison functions for classes with only plain data.

    @PlainData
    class Example:
        int_value: int
        default_value = 23.7

    On construction of a PlainData decorated object, all arguments must be passed as keyword arguments, not positional.

    -------------------------

    The following constructs a class with two instance variables: `int_value` and `float_value`

    @PlainData
    class AnnotatedExample:
        int_value: int
        float_value: float

    The annotation is only a usage hint and does not affect the instance type or value.
    Any valid type or value can be used as an annotation.

    Using the following constructor call, each member of the object is initialised with `None`

    instance = AnnotatedExample()
    print(instance)
    >> <AnnotatedExample: int_value = None, float_value = None>

    Using the next constructor call, each member of the object is initialised with the given value

    instance AnnotatedExample(int_value=5, float_value=13.7)
    print(instance)
    >> <AnnotatedExample: int_value = 5, float_value = 13.7>

    -------------------------

    The following constructs a class with two instance variables: `int_value` and `string_value`
    Any valid type or value can be used as a default value.

    @PlainData
    class DefaultExample:
        int_value = 1536
        string_value = 'some text'

    This time, they have default values that are used on construction when no value is given

    instance = DefaultExample()
    print(instance)
    >> <DefaultExample: int_value = 1536, string_value = 'some text'>

    As before, each member of the object is initialised with the value passed in on construction

    instance = DefaultExample(int_value=5, string_value='other wordy things')
    print(instance)
    >> <DefaultExample: int_value = 5, float_value = 'other wordy things'>

    -------------------------


    """

    def __init__(self, wrapped_type):
        """
        Constructs a new PlainData class type
        """

        self.wrapped_type = wrapped_type
        self.wrapped_type_attributes = PlainData._extract_wrapped_type_attributes(self.wrapped_type)

        PlainData._override_setattr_method(self.wrapped_type)
        PlainData._override_eq_method(self.wrapped_type)
        PlainData._override_str_method(self.wrapped_type)
        PlainData._override_repr_method(self.wrapped_type)

    def __call__(self, *args, **kwargs):
        """
        Constructs a new PlainData object instance
        """

        assert not args, f"{self.wrapped_type.__name__} requires keyword argument(s) only"
        assert set(kwargs.keys()).issubset(
            set(self.wrapped_type_attributes.keys())
        ), f"{self.wrapped_type.__name__} received invalid keyword argument(s) on construction"

        instance = self.wrapped_type()

        # Initialise an internal dict to hold all plain data values for comparisons and printing
        instance._data = {}

        for key, value in self.wrapped_type_attributes.items():
            # If data member value passed in as keyword argument on instance construction
            if key in kwargs:
                setattr(instance, key, kwargs[key])
            # Else if member annotation is a type
            elif isinstance(value, type):
                setattr(instance, key, None)
            # Else member annotation is a default value
            else:
                setattr(instance, key, value)

            instance._data[key] = getattr(instance, key, None)

        # Set `_is_frozen` to True to make instance immutable
        instance._is_frozen = True

        return instance

    def __str__(self):
        return str(self.wrapped_type)

    def __repr__(self):
        return str(self)

    @property
    def __name__(self):
        return self.wrapped_type.__name__

    def get_type(self):
        return self.wrapped_type

    @staticmethod
    def _extract_annotated_attributes(wrapped_type):
        return (
            {}
            if not getattr(wrapped_type, "__annotations__", None)
            else {key: None for key, _ in wrapped_type.__annotations__.items()}
        )

    @staticmethod
    def _extract_default_attributes(wrapped_type):
        return {key: value for key, value in vars(wrapped_type).items() if not key.startswith("__")}

    @staticmethod
    def _extract_wrapped_type_attributes(wrapped_type):
        annotated_attributes = PlainData._extract_annotated_attributes(wrapped_type)
        default_attributes = PlainData._extract_default_attributes(wrapped_type)
        return annotated_attributes | default_attributes

    @staticmethod
    def _override_setattr_method(wrapped_type):
        def set_attribute(self, key, value):
            if getattr(self, "_is_frozen", False):
                raise NotImplementedError(f"Cannot set attribute on instance of class {type(self).__name__}")
            self.__dict__[key] = value

        wrapped_type.__setattr__ = set_attribute

    @staticmethod
    def _override_eq_method(wrapped_type):
        wrapped_type.__eq__ = lambda self, other: isinstance(other, self.__class__) and self._data == other._data

    @staticmethod
    def _override_str_method(wrapped_type):
        wrapped_type.__str__ = (
            lambda self: f"<{wrapped_type.__name__}: "
            + ", ".join(f"{key} = {value}" for key, value in self._data.items())
            + ">"
        )

    @staticmethod
    def _override_repr_method(wrapped_type):
        wrapped_type.__repr__ = lambda self: str(self)
