# OFX Generator

This repository provides a Python library for generating OFX (Open Financial Exchange) files. It includes data models, formatters, and a generator to create OFX 2.3 XML documents according to the OFX specification.

## How to Use

### Example: Generating an OFX File

1. **Create a Bank Statement**: Define the financial institution, bank account, transactions, balance, and settings.

   ```python
   from datetime import date
   from decimal import Decimal
   from ofx_generator.models import (
       Balance, BankAccount, BankStatement, CreditCardAccount, FinancialInstitution, OFXSettings, Transaction
   )
   from ofx_generator.standards import AccountType, Currency, Language, TransactionType

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
       version=211,
   )
   credit_card_account = CreditCardAccount(
       cash_advance_available_amount=1000.00,
       cash_advance_credit_limit=5000.00
   )
   statement = BankStatement(
       financial_institution=fi,
       bank_account=account,
       transactions=transactions,
       balance=balance,
       start_date=date(2025, 1, 1),
       end_date=date(2025, 1, 31),
       settings=settings,
       credit_card_account=credit_card_account
   )
   ```

2. **Generate the OFX File**: Use the `OFXGenerator` to create the OFX content and write it to a file.

   ```python
   from ofx_generator.generator import OFXGenerator

   generator = OFXGenerator()
   trnuid = "1001"
   ofx_content = generator.generate(statement, trnuid)

   with open("output.ofx", "w", encoding="utf-8") as f:
       f.write(ofx_content)
   ```
