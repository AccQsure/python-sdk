import json
from .elements import PlotElements


class PlotSections(object):
    def __init__(self, accqsure, plot_id):
        self.accqsure = accqsure
        self.plot_id = plot_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{id_}", "GET", kwargs
        )
        return PlotSection(self.accqsure, self.plot_id, **resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_sections = [
            PlotSection(self.accqsure, self.plot_id, **plot_section)
            for plot_section in resp.get("results")
        ]
        return plot_sections, resp.get("last_key")


class PlotSection:
    def __init__(self, accqsure, plot_id, **kwargs):
        self.accqsure = accqsure
        self.plot_id = plot_id
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._heading = self._entity.get("heading")
        self._number = self._entity.get("number")
        self._style = self._entity.get("style")
        self._order = self._entity.get("order")
        self.elements = PlotElements(self.accqsure, self.plot_id, self._id)

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
        return f"PlotSection( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self
