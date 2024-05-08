import random

from pylms.python_utils import first_not_none, require_not_none
from pytest import raises, fixture
from random import randint

OBJECTS = [1, 2, "str1", "str2", 3.4, 4.3, ["A", "b"], [3, 7.9]]


@fixture
def not_none_var():
    return OBJECTS[randint(0, len(OBJECTS) - 1)]


class TestFirstNotNone:
    error_message = "At least one parameter must be not None"

    @staticmethod
    def _other_var(not_none_var):
        temp = OBJECTS[:]
        temp.remove(not_none_var)
        return temp[randint(0, len(temp) - 1)]

    @fixture
    def any_number_of_none(self):
        return [None for _ in range(randint(1, 5))]

    @fixture
    def more_than_one_none(self):
        return [None for _ in range(randint(2, 5))]

    def test_raises_value_error_if_no_parameter(self):
        with raises(ValueError, match=self.error_message):
            first_not_none()

    def test_raises_value_error_if_only_none_parameter(self):
        with raises(ValueError, match=self.error_message):
            first_not_none(None)

    def test_raises_value_error_if_only_none_parameters(self, more_than_one_none):
        with raises(ValueError, match=self.error_message):
            first_not_none(*more_than_one_none)

    def test_return_first_not_none_parameter(self, not_none_var, any_number_of_none):
        other_var = self._other_var(not_none_var)

        assert first_not_none(not_none_var) is not_none_var
        assert first_not_none(not_none_var, other_var) is not_none_var
        assert first_not_none(*any_number_of_none, not_none_var) is not_none_var
        assert first_not_none(*any_number_of_none, not_none_var, other_var) is not_none_var
        assert first_not_none(*any_number_of_none, not_none_var, *any_number_of_none, other_var) is not_none_var


class TestRequireNotNone:
    message: str = "This is the expected message"

    def test_return_object_if_not_none(self, not_none_var):
        assert require_not_none(not_none_var, self.message) == not_none_var

    def test_raises_value_error_with_specified_message_if_none(self):
        with raises(ValueError, match=self.message):
            require_not_none(None, self.message)
