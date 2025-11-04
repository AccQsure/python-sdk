import json
import logging
from .elements import ChartElements


class ChartSections(object):
    def __init__(self, accqsure, chart_id):
        self.accqsure = accqsure
        self.chart_id = chart_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{id_}", "GET", kwargs
        )
        return ChartSection(self.accqsure, self.chart_id, **resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        chart_sections = [
            ChartSection(self.accqsure, self.chart_id, **chart_section)
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
        chart_section = ChartSection(self.accqsure, **resp)
        logging.info(
            "Created Chart Section %s with id %s", order, chart_section.id
        )

        return chart_section

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{id_}", "DELETE", {**kwargs}
        )


class ChartSection:
    def __init__(self, accqsure, chart_id, **kwargs):
        self.accqsure = accqsure
        self.chart_id = chart_id
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._heading = self._entity.get("heading")
        self._number = self._entity.get("number")
        self._style = self._entity.get("style")
        self._order = self._entity.get("order")
        self.elements = ChartElements(self.accqsure, self.chart_id, self._id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def heading(self) -> str:
        return self._heading

    @property
    def number(self) -> str:
        return self._number

    @property
    def style(self) -> str:
        return self._style

    @property
    def order(self) -> int:
        return self._order

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"ChartSection( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self
