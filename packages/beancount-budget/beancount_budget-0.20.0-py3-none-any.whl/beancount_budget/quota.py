import os
import tomllib
from collections import namedtuple
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Self

from .beancount import PerCategory
from .month import Month

# Quotas can be input as arbitrarily precise floating points
# (e.g., a £100.00 quota written as `100`), but must conform
# to the format Beancount determines for the currency.
# Neither format nor currency is known ahead of time, so
# the `Budget` loading the `Quotas` must provide a quantizer.
type Quantizer = Callable[[Decimal], Decimal]
FALLBACK_ZERO = Decimal("0.00")


def two_places(x: Decimal) -> Decimal:
    """Quantize an amount to two decimal places.

    As of 2025: of the ten most-traded currencies by value, nine have sub-units
    of a hundredth. The remaining one is the yen, which has no sub-units.
    """
    return x.quantize(FALLBACK_ZERO)


QuotaType = StrEnum("QuotaType", ["MONTHLY", "YEARLY", "GOAL", "FIXED"])
QuotaRow = namedtuple(
    "QuotaRow",
    ("name", "type", "reqd_balance", "reqd_budget"),
    defaults=([None, None, None, None]),
)


# TODO: This should be split into multiple classes.
@dataclass(frozen=True)
class Quota:
    """Represents a single quota.

    A target month indicates that the quota should be met the month before.
    Quota(QuotaType.Goal, 3000, Month(2023, 5)) means $3000 should be available
    on 2023-05-01.

    The default quota expects a balance of zero -- useful for most budget
    categories, which expect neither over- nor underbudgeting.
    """

    amount: Decimal
    qtype: QuotaType = QuotaType.MONTHLY
    month: Month = Month.this()
    start: Month | None = None
    target: Month | None = None
    hold: bool = False
    quantize: Quantizer = two_places
    zero: Decimal = FALLBACK_ZERO

    def __post_init__(self):
        "Ensure `self.amount` is quantized correctly."
        object.__setattr__(self, "amount", self.quantize(self.amount))
        object.__setattr__(self, "zero", self.quantize(FALLBACK_ZERO))

    @classmethod
    def from_dict(
        cls, data: dict, month: Month, quantize: Quantizer = two_places
    ) -> Self:
        "Deserialize a Quota from a dictionary."

        amount = Decimal(data["amount"])
        qtype = QuotaType[data["type"].upper()]
        start: Month | None = None
        target: Month | None = None
        hold = data.get("hold", False)

        match qtype:
            case QuotaType.YEARLY:
                target = month.next(data["month"])
                start = target - 12
            case QuotaType.GOAL:
                target = Month.from_str(data["by"])
                start = Month.from_str(data["start"])
            case _:
                if start := data.get("start"):
                    start = Month.from_str(start)

        return cls(amount, qtype, month, start, target, hold, quantize)

    @property
    def type_repr(self) -> str:
        "Return a textual representation of the quota's time parameters."
        match self.qtype:
            case QuotaType.MONTHLY:
                return "monthly"
            case QuotaType.FIXED:
                return "monthly (fixed)"
            case QuotaType.YEARLY:
                assert self.start
                return f"yearly ({self.start.month})"
            case QuotaType.GOAL:
                assert self.start and self.target
                return f"goal ({self.start} to {self.target})"

    @property
    def required_balance(self) -> Decimal | None:
        "Return the balance required to meet this quota."
        if self.start and self.month < self.start:
            return None

        match self.qtype:
            case QuotaType.FIXED:
                return None
            case QuotaType.MONTHLY:
                return self.amount
            case QuotaType.GOAL | QuotaType.YEARLY:
                assert self.start and self.target  # placates mypy
                if self.month >= self.target:
                    return self.amount if self.hold else self.zero

                all_months = self.start.delta(self.target)
                remaining_months = self.month.delta(self.target) - 1
                chunk = Decimal(self.amount / all_months)
                return self.quantize(chunk * (all_months - remaining_months))


@dataclass(frozen=True)
class CategoryQuota:
    "Represents the sum of quotas for a single category."
    quotas: dict[str, Quota]
    month: Month
    quantize: Quantizer = two_places

    def __post_init__(self):
        "Ensure `self.zero` is quantized correctly."
        object.__setattr__(self, "zero", self.quantize(FALLBACK_ZERO))

    @classmethod
    def from_dict(
        cls, data: dict, month: Month, quantize: Quantizer = two_places
    ) -> Self:
        "Deserialize a CategoryQuota from a dictionary."
        return cls(
            {
                qname: Quota.from_dict(qdata, month, quantize)
                for qname, qdata in data.items()
            },
            month,
        )

    @property
    def required_budget(self) -> Decimal:
        "Return the amount to be budgeted to meet this quota."
        return (
            sum(q.amount for q in self.quotas.values() if q.qtype == QuotaType.FIXED)
            or FALLBACK_ZERO
        )

    @property
    def required_balance(self) -> Decimal:
        "Return the amount to remain available to meet this quota."
        return (
            sum(q.required_balance for q in self.quotas.values() if q.required_balance)
            or FALLBACK_ZERO
        )

    def deviation(self, budgeted: Decimal, balance: Decimal) -> Decimal:
        "Return the difference between budgeted and expected amounts."
        deviation = balance - self.required_balance
        if self.required_budget:
            return min(budgeted - self.required_budget, deviation)
        return deviation

    def show(self, category: str) -> list[QuotaRow]:
        "Visualize each quota's contribution to this category-quota."
        ret = [
            QuotaRow(
                category,
                None,
                self.required_balance,
                self.required_budget,
            )
        ]

        for name, quota in self.quotas.items():
            if quota.qtype == QuotaType.FIXED:
                values = {
                    "reqd_balance": None,
                    "reqd_budget": quota.amount,
                }
            else:
                reqd_balance = quota.required_balance or FALLBACK_ZERO
                values = {
                    "reqd_balance": reqd_balance,
                    "reqd_budget": None,
                }
            ret.append(QuotaRow(f"- {name}", quota.type_repr, **values))

        return ret


def load_quotas(
    path: str | os.PathLike, month: Month, quantize: Quantizer
) -> PerCategory[CategoryQuota]:
    with open(path, mode="rb") as f:
        return {
            category: CategoryQuota.from_dict(quotas, month, quantize)
            for category, quotas in tomllib.load(f).items()
        }
