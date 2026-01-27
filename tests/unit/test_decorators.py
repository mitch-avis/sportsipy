from sportsipy.decorators import float_property_decorator, int_property_decorator


class _IntDecoratorExample:
    def __init__(self, value):
        self._value = value

    @int_property_decorator
    def value(self):
        return self._value


class _IntDecoratorFactoryExample:
    def __init__(self, value):
        self._value = value

    @int_property_decorator()
    def value(self):
        return self._value


class _FloatDecoratorExample:
    def __init__(self, value):
        self._value = value

    @float_property_decorator
    def value(self):
        return self._value


def test_int_property_decorator_converts_and_handles_invalid():
    assert _IntDecoratorExample("7").value == 7
    assert _IntDecoratorExample("bad").value is None
    assert _IntDecoratorExample(None).value is None


def test_int_property_decorator_factory_path():
    assert _IntDecoratorFactoryExample("3").value == 3
    assert _IntDecoratorFactoryExample("").value is None


def test_float_property_decorator_converts_and_handles_invalid():
    assert _FloatDecoratorExample("3.5").value == 3.5
    assert _FloatDecoratorExample("bad").value is None
    assert _FloatDecoratorExample(None).value is None
