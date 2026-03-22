import sys
import os

# Allow importing from the project root without a running app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import User


def test_user_password_hashing():
    """Unit test: set_password hashes the password and check_password verifies it correctly."""
    user = User(username="localtest")
    user.set_password("mysecretpassword")

    # The hash should not be the plain-text password
    assert user.password_hash != "mysecretpassword"
    assert user.password_hash is not None

    # Correct password should pass
    assert user.check_password("mysecretpassword") is True

    # Wrong password should fail
    assert user.check_password("wrongpassword") is False
