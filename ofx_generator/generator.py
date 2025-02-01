import xml.etree.ElementTree as ET
from typing import Optional

from .formatters import (
    AmountFormatter,
    DateFormatter,
    DefaultAmountFormatter,
    DefaultDateFormatter,
    format_datetime,
    format_ofx_header,
)
from .models import Balance, BankAccount, BankStatement, CreditCardAccount


class OFXGenerator:
    """Generates OFX 2.3 XML documents according to the specification."""

    def __init__(
        self,
        date_formatter: Optional[DateFormatter] = None,
        amount_formatter: Optional[AmountFormatter] = None,
    ) -> None:
        """Initialize with optional custom formatters."""
        self.date_formatter = date_formatter or DefaultDateFormatter()
        self.amount_formatter = amount_formatter or DefaultAmountFormatter()

    def generate(self, statement: BankStatement, trnuid: str) -> str:
        """Generate OFX response document from bank statement data."""
        ofx = self._create_ofx_element()
        self._add_signon_response(ofx, statement)
        self._add_bank_statement(ofx, statement, trnuid)
        return self._generate_output(ofx)

    def _create_ofx_element(self) -> ET.Element:
        """Create OFX root element with required XML namespaces."""
        return ET.Element(
            "OFX",
            {
                "xmlns": "http://ofx.net/ifx/2.0/ofx",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            },
        )

    def _add_signon_response(self, ofx: ET.Element, statement: BankStatement) -> None:
        """Build SIGNONMSGSRSV1 aggregate for statement response."""
        signon = ET.SubElement(ofx, "SIGNONMSGSRSV1")
        sonrs = ET.SubElement(signon, "SONRS")

        status = ET.SubElement(sonrs, "STATUS")
        ET.SubElement(status, "CODE").text = "0"
        ET.SubElement(status, "SEVERITY").text = "INFO"

        ET.SubElement(sonrs, "DTSERVER").text = format_datetime(statement.end_date)
        ET.SubElement(sonrs, "LANGUAGE").text = statement.settings.language

        fi = ET.SubElement(sonrs, "FI")
        ET.SubElement(fi, "ORG").text = statement.financial_institution.org
        ET.SubElement(fi, "FID").text = statement.financial_institution.fid

    def _add_bank_statement(self, ofx: ET.Element, statement: BankStatement, trnuid: str) -> None:
        """Build BANKMSGSRSV1 aggregate containing statement data."""
        bank_msgs = ET.SubElement(ofx, "BANKMSGSRSV1")
        stmt_trnrs = ET.SubElement(bank_msgs, "STMTTRNRS")
        ET.SubElement(stmt_trnrs, "TRNUID").text = trnuid

        status = ET.SubElement(stmt_trnrs, "STATUS")
        ET.SubElement(status, "CODE").text = "0"
        ET.SubElement(status, "SEVERITY").text = "INFO"

        stmt_rs = ET.SubElement(stmt_trnrs, "STMTRS")
        ET.SubElement(stmt_rs, "CURDEF").text = statement.settings.currency

        self._add_account_info(stmt_rs, statement.bank_account)
        self._add_transactions(stmt_rs, statement)
        self._add_balance(stmt_rs, statement.balance)
        self._add_credit_card_info(ofx, statement.credit_card_account)

    def _add_account_info(self, stmt_rs: ET.Element, account: BankAccount) -> None:
        """Add bank account information to statement response."""
        bank_acct_from = ET.SubElement(stmt_rs, "BANKACCTFROM")
        ET.SubElement(bank_acct_from, "BANKID").text = account.bank_id
        ET.SubElement(bank_acct_from, "BRANCHID").text = account.branch_id
        ET.SubElement(bank_acct_from, "ACCTID").text = account.account_id
        ET.SubElement(bank_acct_from, "ACCTTYPE").text = account.account_type.value

    def _add_transactions(self, stmt_rs: ET.Element, statement: BankStatement) -> None:
        """Add transaction list to statement response."""
        trans_list = ET.SubElement(stmt_rs, "BANKTRANLIST")
        ET.SubElement(trans_list, "DTSTART").text = format_datetime(statement.start_date)
        ET.SubElement(trans_list, "DTEND").text = format_datetime(statement.end_date)

        for transaction in statement.transactions:
            trans = ET.SubElement(trans_list, "STMTTRN")
            ET.SubElement(trans, "TRNTYPE").text = transaction.transaction_type.value
            ET.SubElement(trans, "DTPOSTED").text = format_datetime(transaction.date_posted)
            ET.SubElement(trans, "TRNAMT").text = str(transaction.amount)
            ET.SubElement(trans, "FITID").text = transaction.fit_id
            if transaction.check_num:
                ET.SubElement(trans, "CHECKNUM").text = transaction.check_num
            if transaction.ref_num:
                ET.SubElement(trans, "REFNUM").text = transaction.ref_num
            if transaction.memo:
                ET.SubElement(trans, "MEMO").text = transaction.memo

    def _add_balance(self, stmt_rs: ET.Element, balance: Balance) -> None:
        """Add balance information to statement response."""
        ledger_bal = ET.SubElement(stmt_rs, "LEDGERBAL")
        ET.SubElement(ledger_bal, "BALAMT").text = str(balance.amount)
        ET.SubElement(ledger_bal, "DTASOF").text = format_datetime(balance.date_as_of)

    def _add_credit_card_info(
        self, ofx: ET.Element, credit_card_account: CreditCardAccount
    ) -> None:
        """Add credit card account information to the root OFX node."""
        if credit_card_account:
            ET.SubElement(ofx, "CASHADVAVAILAMT").text = str(
                credit_card_account.cash_advance_available_amount
            )
            ET.SubElement(ofx, "CASHADVCREDITLIMIT").text = str(
                credit_card_account.cash_advance_credit_limit
            )

    def _generate_output(self, ofx: ET.Element) -> str:
        """Combine headers and XML content in OFX-specified order."""
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            + format_ofx_header()
            + ET.tostring(ofx, encoding="unicode", method="xml")
        )
