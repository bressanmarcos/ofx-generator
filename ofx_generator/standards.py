"""
OFX standard definitions and validation functions.

This module implements the Open Financial Exchange (OFX) specification version 2.1.1,
providing type safety and validation for OFX data structures.
"""

from datetime import date
from enum import Enum


class TransactionType(str, Enum):
    """
    OFX transaction types for banking transactions.

    Reference: OFX 2.1.1 spec - Section 11.3.1.1 (TRNTYPE)
    """

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    INTEREST = "INT"
    DIVIDEND = "DIV"
    FEE = "FEE"
    SERVICE_CHARGE = "SRVCHG"
    DEPOSIT = "DEP"
    ATM = "ATM"
    POINT_OF_SALE = "POS"
    TRANSFER = "XFER"
    CHECK = "CHECK"
    PAYMENT = "PAYMENT"
    CASH = "CASH"
    DIRECT_DEPOSIT = "DIRECTDEP"
    DIRECT_DEBIT = "DIRECTDEBIT"
    REPEATING_PAYMENT = "REPEATPMT"
    OTHER = "OTHER"


class AccountType(str, Enum):
    """
    OFX bank account types.

    Reference: OFX 2.1.1 spec - Section 11.3.1.2 (BANKACCTTYPE)
    """

    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    MONEY_MARKET = "MONEYMRKT"
    CREDIT_LINE = "CREDITLINE"
    CERTIFICATE_OF_DEPOSIT = "CD"


class Language(str, Enum):
    """
    OFX language codes using ISO 639-2 alpha-3 format.

    Reference: OFX 2.1.1 spec - Section 7.2 (LANGUAGE)
    """

    ENGLISH = "ENG"
    PORTUGUESE = "POR"
    SPANISH = "SPA"
    FRENCH = "FRA"
    GERMAN = "DEU"
    ITALIAN = "ITA"


class Currency(str, Enum):
    """
    Currency codes in ISO 4217 format.

    Reference: OFX 2.1.1 spec - Section 3.2.1 (CURDEF/CURRENCY)
    """

    US_DOLLAR = "USD"
    BRAZILIAN_REAL = "BRL"
    EURO = "EUR"
    BRITISH_POUND = "GBP"


class Security(str, Enum):
    """
    OFX security level types.

    Reference: OFX 2.1.1 spec - Section 2.2 (SECURITY)
    """

    NONE = "NONE"
    TYPE1 = "TYPE1"


class Encoding(str, Enum):
    """
    OFX character encoding types.

    Reference: OFX 2.1.1 spec - Section 2.1.2 (ENCODING)
    """

    ASCII = "USASCII"
    UTF8 = "UTF8"


class Compression(str, Enum):
    """
    OFX compression methods.

    Reference: OFX 2.1.1 spec - Section 2.1.3 (COMPRESSION)
    """

    NONE = "NONE"


class OFXVersion:
    """
    OFX version validator.
    Only supports OFX 2.1.1 and above for modern compatibility.
    """

    SUPPORTED_VERSIONS = {
        211,  # OFX 2.1.1 (current version)
    }

    @classmethod
    def validate(cls, version: int) -> bool:
        """Check if version is supported."""
        return version in cls.SUPPORTED_VERSIONS


class CharSet:
    """
    OFX character set validator.

    Reference: OFX 2.1.1 spec - Section 2.1.2 (CHARSET)
    """

    VALID_CHARSETS = {1252}  # Windows-1252 for Latin alphabet

    @classmethod
    def validate(cls, charset: int) -> bool:
        """Validate if the given charset code is supported."""
        return charset in cls.VALID_CHARSETS


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate date range for statement transactions.

    Reference: OFX 2.1.1 spec - Section 11.4.2.1 (DTSTART/DTEND)
    """
    return end_date >= start_date


def validate_bank_id(bank_id: str) -> bool:
    """
    Validate bank identifier format.

    Reference: OFX 2.1.1 spec - Section 11.3.1.2 (BANKID)
    """
    return bool(bank_id and bank_id.isalnum() and len(bank_id) <= 9)


def validate_branch_id(branch_id: str) -> bool:
    """
    Validate branch identifier format.

    Reference: OFX 2.1.1 spec - Section 11.3.1.2 (BRANCHID)
    """
    return bool(branch_id and len(branch_id) <= 22)


def validate_account_id(account_id: str) -> bool:
    """
    Validate account identifier format.

    Reference: OFX 2.1.1 spec - Section 11.3.1.2 (ACCTID)
    """
    return bool(account_id and len(account_id) <= 22)


def validate_fit_id(fit_id: str) -> bool:
    """
    Validate Financial Institution Transaction ID format.

    Reference: OFX 2.1.1 spec - Section 11.4.2.2 (FITID)
    """
    return bool(fit_id and len(fit_id) <= 255)
