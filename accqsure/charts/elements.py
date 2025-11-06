from __future__ import annotations
from dataclasses import dataclass, field, fields
import logging
from typing import Optional, Any, List, Dict, TYPE_CHECKING
from accqsure.charts.waypoints import ChartWaypoint

if TYPE_CHECKING:
    from accqsure import AccQsure


class ChartElements:
    def __init__(
        self,
        accqsure,
        chart_id,
        chart_section_id,
    ):
        self.accqsure = accqsure
        self.chart_id = chart_id
        self.section_id = chart_section_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{id_}",
            "GET",
            kwargs,
        )
        return ChartElement.from_api(
            self.accqsure, self.chart_id, self.section_id, resp
        )

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        chart_elements = [
            ChartElement.from_api(
                self.accqsure, self.chart_id, self.section_id, chart_element
            )
            for chart_element in resp.get("results")
        ]
        return chart_elements, resp.get("last_key")

    async def create(
        self,
        order,
        element_type,
        description,
        prompt,
        for_each,
        waypoints=None,
        metadata=None,
        **kwargs,
    ):

        data = dict(
            order=order,
            type=element_type,
            description=description,
            prompt=prompt,
            for_each=for_each,
            waypoints=waypoints,
            metadata=metadata,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Chart Element %s", order)

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element",
            "POST",
            None,
            payload,
        )
        chart_element = ChartElement.from_api(
            self.accqsure, self.chart_id, self.section_id, resp
        )
        logging.info("Created Chart %s with id %s", order, chart_element.id)

        return chart_element

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{id_}",
            "DELETE",
            {**kwargs},
        )


@dataclass
class ChartElement:
    chart_id: str
    section_id: str
    id: str
    created_at: str
    updated_at: str
    order: int
    type: str
    description: str
    prompt: str
    for_each: bool
    metadata: Optional[Dict[str, Any]] = field(default=None)

    waypoints: Optional[List[ChartWaypoint]] = field(default=None)

    @classmethod
    def from_api(
        cls,
        accqsure: "AccQsure",
        chart_id: str,
        section_id: str,
        data: dict[str, Any],
    ) -> "ChartElement":
        if not data:
            return None
        entity = cls(
            chart_id=chart_id,
            section_id=section_id,
            id=data.get("entity_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            order=data.get("order"),
            type=data.get("type"),
            description=data.get("description"),
            prompt=data.get("prompt"),
            for_each=data.get("for_each"),
            metadata=data.get("metadata"),
            waypoints=[
                ChartWaypoint.from_api(
                    accqsure=accqsure, chart_id=chart_id, data=waypoint
                )
                for waypoint in data.get("waypoints") or []
            ],
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
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{self.id}",
            "GET",
        )
        exclude = ["id", "chart_id", "section_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self
