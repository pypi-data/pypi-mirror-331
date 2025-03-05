import abc
import datetime as dt
from typing import Any

import polars as pl

from bayesline.api._src.equity.portfoliohierarchy_settings import (
    PortfolioHierarchySettings,
)
from bayesline.api._src.equity.report_settings import ReportSettings, ReportSettingsMenu
from bayesline.api._src.registry import AsyncRegistryBasedApi, RegistryBasedApi
from bayesline.api._src.types import DateLike


class PortfolioReportApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> ReportSettings:
        """
        Returns
        -------
        The settings used to create this report.
        """
        ...

    @abc.abstractmethod
    def dates(self) -> list[dt.date]: ...

    @abc.abstractmethod
    def get_report(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
        add_totals_columns: bool = False,
        serverside: bool = False,
    ) -> pl.DataFrame | dict[str, Any]: ...


class AsyncPortfolioReportApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> ReportSettings:
        """
        Returns
        -------
        The settings used to create this report.
        """
        ...

    @abc.abstractmethod
    async def dates(self) -> list[dt.date]: ...

    @abc.abstractmethod
    async def get_report(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
        serverside: bool = False,
        add_totals_columns: bool = False,
    ) -> pl.DataFrame | dict[str, Any]: ...


class BayeslinePortfolioReportApi(
    RegistryBasedApi[ReportSettings, ReportSettingsMenu, PortfolioReportApi],
):

    @abc.abstractmethod
    def load(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
    ) -> PortfolioReportApi: ...


class AsyncBayeslinePortfolioReportApi(
    AsyncRegistryBasedApi[ReportSettings, ReportSettingsMenu, AsyncPortfolioReportApi],
):

    @abc.abstractmethod
    async def load(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
    ) -> AsyncPortfolioReportApi: ...
