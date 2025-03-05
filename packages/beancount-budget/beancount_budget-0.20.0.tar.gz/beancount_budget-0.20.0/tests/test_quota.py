from decimal import Decimal

from beancount_budget.budget import Budget
from beancount_budget.month import Month
from beancount_budget.quota import Quota

from . import LAST_MONTH, ZERO, config, takes_data_dir


@takes_data_dir
def test_quotas(datafiles):
    b = Budget.from_config(config(datafiles))
    month = LAST_MONTH

    b.reinit()
    b.fill(month)

    # First month's quota is budgeted twice: once to pay for
    # that month's tram, and once to keep the balance at $120.
    assert b[b.months[0]]["Expenses:Transport:Tram"] == Decimal(240)

    # Balance is already $120 and new month has no tram ticket purchases,
    # so no budgeting needed here.
    assert b[b.months[-1]]["Expenses:Transport:Tram"] == ZERO

    # The bank fee is covered by a fixed quota: no required balance,
    # only a required _budgeted_ amount.
    assert (
        b[b.months[0]]["Expenses:Financial:Fees"]
        == b[b.months[-1]]["Expenses:Financial:Fees"]
        == Decimal(4)
    )


def test_required_balances():
    def check(qdata: dict, month: Month, expected: Decimal | None):
        assert Quota.from_dict(qdata, month).required_balance == expected

    yearly = {
        "type": "yearly",
        "amount": 1200,
        "month": 1,
    }

    check(yearly, Month(2000, 4), Decimal(400))
    check(yearly, Month(2024, 12), Decimal(1200))

    goal = {
        "type": "goal",
        "amount": 1200,
        "start": "2023-01",
        "by": "2024-01",
        "hold": True,
    }

    check(goal, Month(2023, 4), Decimal(400))
    check(goal, Month(2022, 12), None)
    check(goal, Month(2024, 1), Decimal(1200))
    check(goal, Month(2024, 2), Decimal(1200))
    goal["hold"] = False
    check(goal, Month(2024, 2), Decimal(0))
