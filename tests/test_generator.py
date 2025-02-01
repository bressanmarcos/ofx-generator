import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal

import pytest

from ofx_generator.generator import OFXGenerator
from ofx_generator.models import (
    Balance,
    BankAccount,
    BankStatement,
    CreditCardAccount,
    FinancialInstitution,
    OFXSettings,
    Transaction,
)
from ofx_generator.standards import AccountType, Currency, Language, TransactionType


@pytest.fixture
def sample_statement():
    fi = FinancialInstitution(org="Test Bank", fid="123")
    account = BankAccount(
        bank_id="123",
        branch_id="0001",
        account_id="12345",
        account_type=AccountType.CHECKING,
    )
    transaction = Transaction(
        transaction_type=TransactionType.CREDIT,
        date_posted=date(2024, 1, 1),
        amount=Decimal("100.00"),
        fit_id="123",
        memo="Test transaction",
    )
    balance = Balance(amount=Decimal("1000.00"), date_as_of=date(2024, 1, 1))
    settings = OFXSettings(language=Language.ENGLISH, currency=Currency.US_DOLLAR, version=211)
    credit_card_account = CreditCardAccount(
        cash_advance_available_amount=500.00, cash_advance_credit_limit=2000.00
    )
    return BankStatement(
        financial_institution=fi,
        bank_account=account,
        transactions=[transaction],
        balance=balance,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        settings=settings,
        credit_card_account=credit_card_account,
    )


def test_generator_initialization():
    generator = OFXGenerator()
    assert generator is not None


def test_ofx_generation(sample_statement):
    generator = OFXGenerator()
    trnuid = "test-trnuid-123"
    ofx_content = generator.generate(sample_statement, trnuid)

    print("Generated OFX Content:")
    print(ofx_content)

    # Get XML content after headers
    xml_lines = ofx_content.split("\n")
    xml_content = "\n".join(xml_lines[2:])

    # Verify it's valid XML
    root = ET.fromstring(xml_content)

    # Define the namespace map
    namespaces = {"ofx": "http://ofx.net/ifx/2.0/ofx"}

    # Check basic structure with namespace
    assert root.tag == "{http://ofx.net/ifx/2.0/ofx}OFX"
    assert root.find(".//ofx:SIGNONMSGSRSV1", namespaces) is not None
    assert root.find(".//ofx:BANKMSGSRSV1", namespaces) is not None

    # Check financial institution info
    assert root.find(".//{*}FI/{*}ORG").text == "Test Bank"
    assert root.find(".//{*}FI/{*}FID").text == "123"

    # Check transaction
    transaction = root.find(".//{*}STMTTRN")
    assert transaction is not None
    assert transaction.find("{*}TRNAMT").text == "100.00"
    assert transaction.find("{*}MEMO").text == "Test transaction"

    # Check balance
    assert root.find(".//{*}LEDGERBAL/{*}BALAMT").text == "1000.00"

    # Check TRNUID
    assert root.find(".//{*}TRNUID").text == trnuid


def test_ofx_headers(sample_statement):
    generator = OFXGenerator()
    trnuid = "test-trnuid-123"
    ofx_content = generator.generate(sample_statement, trnuid)

    # Check headers
    headers = ofx_content.split("\n")
    assert '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' == headers[0]
    assert (
        '<?OFX OFXHEADER="200" VERSION="230" SECURITY="NONE" '
        'OLDFILEUID="NONE" NEWFILEUID="NONE"?>' == headers[1]
    )


def test_credit_card_account():
    account = CreditCardAccount(cash_advance_available_amount=0.0, cash_advance_credit_limit=0.0)
    assert account.cash_advance_available_amount == 0.0  # Test for new field
    assert account.cash_advance_credit_limit == 0.0  # Test for new field
