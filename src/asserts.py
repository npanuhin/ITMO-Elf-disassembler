from types import GeneratorType

from utils import MSG


def assert_cond(value, error_message=MSG["assert_cond"]):
    if not value:
        exit(error_message.format(value=value))


def assert_equal(value1, value2, error_message=MSG["assert_equal"]):
    if isinstance(value2, tuple) or isinstance(value2, list) or isinstance(value2, GeneratorType):
        assert_cond(
            all(value1 != check_value2 for check_value2 in value2),
            error_message.format(value1=value1, value2=value2)
        )
    else:
        assert_cond(value1 == value2, error_message.format(value1=value1, value2=value2))

    return value1


def assert_not_equal(value1, value2, error_message=MSG["assert_equal"]):
    if isinstance(value2, tuple) or isinstance(value2, list) or isinstance(value2, GeneratorType):
        assert_cond(
            all(value1 == check_value2 for check_value2 in value2),
            error_message.format(value1=value1, value2=value2)
        )
    else:
        assert_cond(value1 != value2, error_message.format(value1=value1, value2=value2))

    return value1


def assert_all_equal(value1, value2, error_message=MSG["assert_equal"]):
    for check_value1 in value1:
        assert_equal(check_value1, value2, error_message)

    return value1
