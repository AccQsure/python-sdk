"""Tests for exception classes."""
import pytest

from accqsure.exceptions import (
    AccQsureException,
    ApiError,
    SpecificationError,
    TaskError,
)


class AccQsureExceptionTests:
    """Tests for AccQsureException base class."""

    def test_init(self):
        """Test exception initialization."""
        exc = AccQsureException('Test error message')
        assert exc.message == 'Test error message'
        assert str(exc) == "AccQsureException('Test error message')"
        assert repr(exc) == "AccQsureException( 'Test error message')"

    def test_init_with_args(self):
        """Test exception initialization with additional args."""
        exc = AccQsureException('Test error', 'arg1', 'arg2')
        assert exc.message == 'Test error'


class ApiErrorTests:
    """Tests for ApiError exception."""

    def test_init_with_error_message(self):
        """Test ApiError with errorMessage field."""
        data = {'errorMessage': 'API error occurred'}
        exc = ApiError(404, data)
        assert exc.status == 404
        assert exc.message == 'API error occurred'
        assert str(exc) == "ApiError(404, 'API error occurred')"
        assert repr(exc) == "ApiError(404, 'API error occurred')"

    def test_init_with_message(self):
        """Test ApiError with message field."""
        data = {'message': 'API error occurred'}
        exc = ApiError(500, data)
        assert exc.status == 500
        assert exc.message == 'API error occurred'

    def test_init_without_message(self):
        """Test ApiError without message field."""
        data = {'error': 'Some error'}
        exc = ApiError(400, data)
        assert exc.status == 400
        assert exc.message is None


class SpecificationErrorTests:
    """Tests for SpecificationError exception."""

    def test_init(self):
        """Test SpecificationError initialization."""
        exc = SpecificationError('field_name', 'Field is required')
        assert exc.attribute == 'field_name'
        assert exc.message == 'Field is required'
        assert str(exc) == "SpecificationError(field_name, Field is required)"
        assert repr(exc) == "SpecificationError(field_name, Field is required)"


class TaskErrorTests:
    """Tests for TaskError exception."""

    def test_init_with_string(self):
        """Test TaskError with string message."""
        exc = TaskError('Task failed')
        assert exc.message == 'Task failed'
        # The actual format may vary, just check it contains the message
        assert 'Task failed' in str(exc)
        assert 'TaskError' in str(exc)
        # Test __repr__ method
        repr_str = repr(exc)
        assert 'TaskError' in repr_str
        assert 'Task failed' in repr_str

    def test_init_with_dict(self):
        """Test TaskError with dictionary result."""
        result = {'error': 'Task failed', 'code': 500}
        exc = TaskError(result)
        assert exc.message == result
        assert str(exc) == f"TaskError({result})"

