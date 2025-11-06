from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING

from .elements import PlotElements

if TYPE_CHECKING:
    from accqsure import AccQsure


class PlotSections(object):
    def __init__(self, accqsure, plot_id):
        self.accqsure = accqsure
        self.plot_id = plot_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{id_}", "GET", kwargs
        )
        return PlotSection.from_api(self.accqsure, self.plot_id, resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_sections = [
            PlotSection.from_api(self.accqsure, self.plot_id, plot_section)
            for plot_section in resp.get("results")
        ]
        return plot_sections, resp.get("last_key")


@dataclass
class PlotSection:
    plot_id: str
    id: str
    heading: str
    style: str
    order: int
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    number: Optional[str] = field(default=None)

    elements: PlotElements = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", plot_id: str, data: dict[str, Any]
    ) -> "PlotSection":
        if not data:
            return None
        entity = cls(
            plot_id=plot_id,
            id=data.get("entity_id"),
            heading=data.get("heading"),
            number=data.get("number"),
            style=data.get("style"),
            order=data.get("order"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        entity.accqsure = accqsure
        entity.elements = PlotElements(
            entity.accqsure, entity.plot_id, entity.id
        )
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like elements)
                setattr(self, f.name, resp.get(f.name))
        return self
