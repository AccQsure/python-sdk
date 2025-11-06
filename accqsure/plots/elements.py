from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from accqsure import AccQsure


class PlotElements(object):
    def __init__(
        self,
        accqsure,
        plot_id,
        plot_section_id,
    ):
        self.accqsure = accqsure
        self.plot_id = plot_id
        self.section_id = plot_section_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element/{id_}",
            "GET",
            kwargs,
        )
        return PlotElement.from_api(
            self.accqsure, self.plot_id, self.section_id, resp
        )

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_elements = [
            PlotElement.from_api(
                self.accqsure, self.plot_id, self.section_id, plot_element
            )
            for plot_element in resp.get("results")
        ]
        return plot_elements, resp.get("last_key")


@dataclass
class PlotElement:
    plot_id: str
    section_id: str
    id: str
    order: int
    type: str
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    content: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls,
        accqsure: "AccQsure",
        plot_id: str,
        section_id: str,
        data: dict[str, Any],
    ) -> "PlotElement":
        if not data:
            return None
        entity = cls(
            plot_id=plot_id,
            section_id=section_id,
            id=data.get("entity_id"),
            order=data.get("order"),
            type=data.get("type"),
            status=data.get("status"),
            content=data.get("content"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        entity.accqsure = accqsure
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "section_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self
