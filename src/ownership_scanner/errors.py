"""Framework-independent domain errors."""


class OwnershipScannerError(Exception):
    """Base class for expected application errors."""


class InvalidGtinError(OwnershipScannerError):
    """The supplied GTIN has an invalid shape or check digit."""


class ProductNotFoundError(OwnershipScannerError):
    """A valid GTIN is not present in the canonical dataset."""


class DataIntegrityError(OwnershipScannerError):
    """Canonical data is missing a required reference or source."""
