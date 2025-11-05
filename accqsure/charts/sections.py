from __future__ import annotations
from dataclasses import dataclass, field, fields
import logging
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from accqsure import AccQsure


from .elements import ChartElements


@dataclass
class ChartSections(object):
    accqsure: "AccQsure" = field(repr=False, compare=False, hash=False)
    chart_id: str

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{id_}", "GET", kwargs
        )
        return ChartSection.from_api(self.accqsure, self.chart_id, resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        chart_sections = [
            ChartSection.from_api(self.accqsure, self.chart_id, chart_section)
            for chart_section in resp.get("results")
        ]
        return chart_sections, resp.get("last_key")

    async def create(
        self,
        heading,
        style,
        order,
        number=None,
        **kwargs,
    ):

        data = dict(
            heading=heading,
            style=style,
            order=order,
            number=number,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Chart Section %s", order)

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section", "POST", None, payload
        )
        chart_section = ChartSection.from_api(
            self.accqsure, self.chart_id, resp
        )
        logging.info(
            "Created Chart Section %s with id %s", order, chart_section.id
        )

        return chart_section

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{id_}", "DELETE", {**kwargs}
        )


@dataclass
class ChartSection:
    accqsure: "AccQsure" = field(repr=False, compare=False, hash=False)
    chart_id: str
    id: str
    created_at: str
    updated_at: str
    heading: str
    style: str
    order: int
    number: Optional[str] = field(default=None)

    elements: ChartElements = field(
        init=False, repr=False, compare=False, hash=False
    )

    def __post_init__(self):
        self.elements = ChartElements(self.accqsure, self.chart_id, self.id)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", chart_id: str, data: dict[str, Any]
    ) -> "ChartSection":
        if not data:
            return None
        return cls(
            accqsure=accqsure,
            chart_id=chart_id,
            id=data.get("entity_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            heading=data.get("heading"),
            number=data.get("number"),
            style=data.get("style"),
            order=data.get("order"),
        )

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.id}",
            "GET",
        )
        exclude = ["id", "chart_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))

        return self
