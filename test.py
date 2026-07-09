"""Unit of Work interface"""
from __future__ import annotations

import types
from typing import Protocol


class UnitOfWork(Protocol):
    """Interface defining transaction boundaries"""

    def __enter__(self) -> UnitOfWork:
        """Enter transaction context"""
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        """Exit transaction context - commit if no exception, rollback otherwise"""
        ...

    def commit(self) -> None:
        """Commit the current transaction"""
        ...

    def rollback(self) -> None:
        """Rollback the current transaction"""
        ...