class LockError(Exception):
    """Base class for all exceptions raised by padlock."""


class LockAcquisitionError(LockError):
    """Raised when a lock could not be acquired."""
