"""
OFX data formatting protocols and default implementations.

This module provides interfaces and default implementations for formatting
dates and amounts according to OFX specification requirements.
"""

from datetime import date
from decimal import Decimal
from typing import Protocol


class DateFormatter(Protocol):
    """
    Protocol defining date formatting for OFX files.

    Implementations should convert dates to the OFX required format: YYYYMMDD

    Reference: OFX 2.1.1 spec - Section 3.2.8.1 (Date and DateTime)
    """

    def format(self, value: date) -> str:
        """
        Format a date object to OFX date string.

        Args:
            value: The date to format

        Returns:
            String in YYYYMMDD format

        Example:
            >>> formatter.format(date(2024, 1, 31))
            '20240131'
        """
        pass


class AmountFormatter(Protocol):
    """
    Protocol defining amount formatting for OFX files.

    Implementations should convert decimal amounts to valid OFX numeric strings.
    Negative values must be prefixed with a minus sign.

    Reference: OFX 2.1.1 spec - Section 3.2.8.2 (Monetary Amounts)
    """

    def format(self, value: Decimal) -> str:
        """
        Format a decimal amount to OFX amount string.

        Args:
            value: The decimal amount to format

        Returns:
            String representation of the amount with optional minus sign

        Example:
            >>> formatter.format(Decimal('-123.45'))
            '-123.45'
        """
        pass


class DefaultDateFormatter:
    """
    Default implementation of DateFormatter using YYYYMMDD format.

    Uses strftime to format dates in the required OFX format.
    """

    def format(self, value: date) -> str:
        """
        Format date as YYYYMMDD.

        Args:
            value: Date to format

        Returns:
            Date string in YYYYMMDD format
        """
        return value.strftime("%Y%m%d")


class DefaultAmountFormatter:
    """
    Default implementation of AmountFormatter using simple string conversion.

    Converts Decimal amounts to strings, preserving the minus sign for negative values
    and decimal places.
    """

    def format(self, value: Decimal) -> str:
        """
        Format decimal with 2 decimal places.

        Args:
            value: Decimal amount to format

        Returns:
            String representation of the amount
        """
        return f"{value:.2f}"


def format_datetime(value: date) -> str:
    """Format datetime in OFX format (YYYYMMDD)."""
    return value.strftime("%Y%m%d")


def format_ofx_header():
    return (
        '<?OFX OFXHEADER="200" VERSION="230" SECURITY="NONE" '
        'OLDFILEUID="NONE" NEWFILEUID="NONE"?>\n'
    )
