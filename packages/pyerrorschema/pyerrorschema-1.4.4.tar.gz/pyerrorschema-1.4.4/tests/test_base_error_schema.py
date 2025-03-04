import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pyerrorschema import ErrorSchema


class TestErrorSchema:
    def test_basic_error_creation(self):
        """Test basic error creation with different factory methods."""
        # Test file error
        file_err = ErrorSchema.file_error(msg="Test file error")
        assert file_err.type == "file_error"
        assert file_err.msg == "File error: test file error"

        # Test database error
        db_err = ErrorSchema.database_error(msg="Test database error")
        assert db_err.type == "database_error"
        assert db_err.msg == "Database error: test database error"

