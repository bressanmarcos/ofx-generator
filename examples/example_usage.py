#!/usr/bin/env python3

import os
import sys

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date  # noqa: E402
from decimal import Decimal  # noqa: E402

from ofx_generator.generator import OFXGenerator  # noqa: E402
from ofx_generator.models import (  # noqa: E402
    Balance,
    BankAccount,
    BankStatement,
    CreditCardAccount,
    FinancialInstitution,
    OFXSettings,
    Transaction,
    ValidationError,
)
from ofx_generator.standards import AccountType, Currency, Language, TransactionType  # noqa: E402

try:
    # Create credit card account details
    credit_card_account = CreditCardAccount(
        cash_advance_available_amount=1000.00, cash_advance_credit_limit=5000.00
    )

    # Create the statement data
    fi = FinancialInstitution(org="Example Bank", fid="000")

    account = BankAccount(
        bank_id="000",
        branch_id="0000-0",
        account_id="000000000",
        account_type=AccountType.CHECKING,
    )

    transactions = [
        Transaction(
            transaction_type=TransactionType.PAYMENT,
            date_posted=date(2025, 1, 30),
            amount=Decimal("-100.00"),
            fit_id="202501300000",
            check_num="000",
            ref_num="000",
            memo="Payment to Vendor",
        ),
        Transaction(
            transaction_type=TransactionType.CREDIT,
            date_posted=date(2025, 1, 22),
            amount=Decimal("500.00"),
            fit_id="202501220000",
            check_num="000",
            ref_num="000",
            memo="Salary Payment",
        ),
    ]

    balance = Balance(amount=Decimal("1000.00"), date_as_of=date(2025, 1, 31))

    settings = OFXSettings(
        language=Language.PORTUGUESE,
        currency=Currency.BRAZILIAN_REAL,
        version=211,  # Using OFX 2.1.1
    )

    statement = BankStatement(
        financial_institution=fi,
        bank_account=account,
        transactions=transactions,
        balance=balance,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
        settings=settings,
        credit_card_account=credit_card_account,  # Include credit card account
    )

    # Generate the OFX
    generator = OFXGenerator()
    trnuid = "1001"  # Use the trnuid from the OFX file
    ofx_content = generator.generate(statement, trnuid)

    # Write to file
    with open("new.ofx", "w", encoding="utf-8") as f:
        f.write(ofx_content)

except ValidationError as e:
    print(f"Validation error: {e}")
