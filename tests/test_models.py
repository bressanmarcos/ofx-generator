from datetime import date
from decimal import Decimal

import pytest

from ofx_generator.models import (
    Balance,
    BankAccount,
    BankStatement,
    FinancialInstitution,
    OFXSettings,
    Transaction,
    ValidationError,
)
from ofx_generator.standards import AccountType, Currency, Language, TransactionType


@pytest.fixture
def valid_fi():
    return FinancialInstitution(org="Test Bank", fid="123")


@pytest.fixture
def valid_account():
    return BankAccount(
        bank_id="123",
        branch_id="0001",
        account_id="12345",
        account_type=AccountType.CHECKING,
    )


@pytest.fixture
def valid_transaction():
    return Transaction(
        transaction_type=TransactionType.CREDIT,
        date_posted=date(2024, 1, 1),
        amount=Decimal("100.00"),
        fit_id="123",
        memo="Test transaction",
    )


@pytest.fixture
def valid_balance():
    return Balance(amount=Decimal("1000.00"), date_as_of=date(2024, 1, 1))


@pytest.fixture
def valid_settings():
    return OFXSettings(language=Language.ENGLISH, currency=Currency.US_DOLLAR, version=211)


def test_financial_institution_creation():
    fi = FinancialInstitution(org="Test Bank", fid="123")
    assert fi.org == "Test Bank"
    assert fi.fid == "123"


def test_bank_account_creation():
    account = BankAccount(
        bank_id="123",
        branch_id="0001",
        account_id="12345",
        account_type=AccountType.CHECKING,
    )
    assert account.bank_id == "123"
    assert account.branch_id == "0001"
    assert account.account_id == "12345"
    assert account.account_type == AccountType.CHECKING


def test_transaction_creation():
    transaction = Transaction(
        transaction_type=TransactionType.CREDIT,
        date_posted=date(2024, 1, 1),
        amount=Decimal("100.00"),
        fit_id="123",
        memo="Test transaction",
    )
    assert transaction.transaction_type == TransactionType.CREDIT
    assert transaction.amount == Decimal("100.00")
    assert transaction.fit_id == "123"


def test_balance_creation():
    balance = Balance(amount=Decimal("1000.00"), date_as_of=date(2024, 1, 1))
    assert balance.amount == Decimal("1000.00")
    assert balance.date_as_of == date(2024, 1, 1)


def test_bank_statement_creation(
    valid_fi, valid_account, valid_transaction, valid_balance, valid_settings
):
    statement = BankStatement(
        financial_institution=valid_fi,
        bank_account=valid_account,
        transactions=[valid_transaction],
        balance=valid_balance,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        settings=valid_settings,
    )
    assert statement.financial_institution == valid_fi
    assert statement.bank_account == valid_account
    assert len(statement.transactions) == 1
    assert statement.balance == valid_balance


def test_invalid_transaction_amount():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_type=TransactionType.CREDIT,
            date_posted=date(2024, 1, 1),
            amount=Decimal("0"),  # Invalid amount (should be non-zero)
            fit_id="123",
            memo="Test transaction",
        )


def test_invalid_date_range(
    valid_fi, valid_account, valid_transaction, valid_balance, valid_settings
):
    with pytest.raises(ValidationError):
        BankStatement(
            financial_institution=valid_fi,
            bank_account=valid_account,
            transactions=[valid_transaction],
            balance=valid_balance,
            start_date=date(2024, 1, 31),  # End date before start date
            end_date=date(2024, 1, 1),
            settings=valid_settings,
        )
