"""Data models for generating OFX bank statement files."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Optional

from .standards import (
    AccountType,
    CharSet,
    Compression,
    Currency,
    Encoding,
    Language,
    OFXVersion,
    Security,
    TransactionType,
    validate_account_id,
    validate_bank_id,
    validate_branch_id,
    validate_date_range,
    validate_fit_id,
)


class ValidationError(Exception):
    """Raised when OFX data validation fails."""


@dataclass
class FinancialInstitution:
    """Financial Institution identification.

    Attributes:
        org (str): The organization name of the financial institution.
        fid (str): The financial institution ID.
    """

    org: str
    fid: str

    def __post_init__(self):
        if not self.org or len(self.org) > 60:
            raise ValidationError("Organization name must be between 1 and 60 characters")
        if not self.fid or len(self.fid) > 32:
            raise ValidationError("FID must be between 1 and 32 characters")


@dataclass
class BankAccount:
    """Bank account details.

    Attributes:
        bank_id (str): The bank's unique identifier.
        account_id (str): The account's unique identifier.
        account_type (str): The type of the bank account (e.g., checking, savings).
        branch_id (Optional[str]): Optional branch identifier.
    """

    bank_id: str
    account_id: str
    account_type: str
    branch_id: Optional[str] = None

    def __post_init__(self):
        if not validate_bank_id(self.bank_id):
            raise ValidationError("Invalid bank ID format")
        if not validate_account_id(self.account_id):
            raise ValidationError("Invalid account ID format")
        if self.branch_id and not validate_branch_id(self.branch_id):
            raise ValidationError("Invalid branch ID format")
        if not isinstance(self.account_type, AccountType):
            self.account_type = AccountType(self.account_type)


@dataclass
class Transaction:
    """Represents a bank transaction in the OFX statement.

    Attributes:
        transaction_type (TransactionType): The type of transaction (e.g., debit, credit).
        date_posted (date): The date the transaction was posted.
        amount (Decimal): The amount of the transaction.
        fit_id (str): The financial institution transaction ID.
        check_num (Optional[str]): Optional check number associated with the transaction.
        ref_num (Optional[str]): Optional reference number for the transaction.
        memo (Optional[str]): Optional memo or description of the transaction.
    """

    def __init__(
        self,
        transaction_type: TransactionType,
        date_posted: date,
        amount: Decimal,
        fit_id: str,
        check_num: Optional[str] = None,
        ref_num: Optional[str] = None,
        memo: Optional[str] = None,
    ):
        """Initialize a bank transaction."""
        if amount == Decimal("0"):
            raise ValidationError("Transaction amount cannot be zero")

        self.transaction_type = transaction_type
        self.date_posted = date_posted
        self.amount = amount
        self.fit_id = fit_id
        self.check_num = check_num
        self.ref_num = ref_num
        self.memo = memo

    def __post_init__(self):
        if not isinstance(self.transaction_type, TransactionType):
            self.transaction_type = TransactionType(self.transaction_type)
        if not validate_fit_id(self.fit_id):
            raise ValidationError("Invalid FIT ID format")
        if self.memo and len(self.memo) > 255:
            raise ValidationError("Memo must not exceed 255 characters")
        if self.check_num and len(self.check_num) > 32:
            raise ValidationError("Check number must not exceed 32 characters")
        if self.ref_num and len(self.ref_num) > 32:
            raise ValidationError("Reference number must not exceed 32 characters")


@dataclass
class Balance:
    """Account balance information.

    Attributes:
        amount (Decimal): The balance amount.
        date_as_of (date): The date as of which the balance is reported.
    """

    amount: Decimal
    date_as_of: date


@dataclass
class OFXSettings:
    """OFX document settings and metadata.

    Attributes:
        language (Language): The language used in the OFX document.
        currency (Currency): The currency used in the OFX document.
        version (int): The OFX version number.
        encoding (Encoding): The character encoding used in the OFX document.
        charset (int): The character set used in the OFX document.
        security (Security): The security level of the OFX document.
        compression (Compression): The compression method used in the OFX document.
    """

    language: Language
    currency: Currency
    version: int = 211  # OFX 2.1.1 by default
    encoding: Encoding = Encoding.UTF8
    charset: int = 1252
    security: Security = Security.NONE
    compression: Compression = Compression.NONE

    def __post_init__(self):
        if not isinstance(self.language, Language):
            self.language = Language(self.language)
        if not isinstance(self.currency, Currency):
            self.currency = Currency(self.currency)
        if not isinstance(self.encoding, Encoding):
            self.encoding = Encoding(self.encoding)
        if not isinstance(self.security, Security):
            self.security = Security(self.security)
        if not isinstance(self.compression, Compression):
            self.compression = Compression(self.compression)
        if not OFXVersion.validate(self.version):
            raise ValidationError(f"Invalid OFX version: {self.version}")
        if not CharSet.validate(self.charset):
            raise ValidationError(f"Invalid charset: {self.charset}")


@dataclass
class BankStatement:
    """Complete bank statement with transactions and metadata.

    Attributes:
        financial_institution (FinancialInstitution):
            The financial institution associated with the statement.
        bank_account (BankAccount):
            The bank account associated with the statement.
        balance (Balance):
            The balance information for the account.
        start_date (date):
            The start date of the statement period.
        end_date (date):
            The end date of the statement period.
        transactions (List[Transaction]):
            A list of transactions included in the statement.
        settings (OFXSettings):
            The OFX settings and metadata for the statement.
        credit_card_account (Optional[CreditCardAccount]):
            The credit card account associated with the statement.
    """

    financial_institution: FinancialInstitution
    bank_account: BankAccount
    balance: Balance
    start_date: date
    end_date: date
    transactions: List[Transaction] = field(default_factory=list)
    settings: OFXSettings = field(
        default_factory=lambda: OFXSettings(language=Language.ENGLISH, currency=Currency.US_DOLLAR)
    )
    credit_card_account: Optional[CreditCardAccount] = None

    def __post_init__(self):
        if not validate_date_range(self.start_date, self.end_date):
            raise ValidationError("End date must not be before start date")


@dataclass
class CreditCardAccount:
    """Credit card account details.

    Attributes:
        cash_advance_available_amount (float): The available amount for cash advances.
        cash_advance_credit_limit (float): The credit limit for cash advances.
    """

    cash_advance_available_amount: float = 0.0
    # Field for OFX 2.3
    cash_advance_credit_limit: float = 0.0
    # Field for OFX 2.3
