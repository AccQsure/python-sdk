import json


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
        return PlotElement(
            self.accqsure, self.plot_id, self.section_id, **resp
        )

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_elements = [
            PlotElement(
                self.accqsure, self.plot_id, self.section_id, **plot_element
            )
            for plot_element in resp.get("results")
        ]
        return plot_elements, resp.get("last_key")


class PlotElement:
    def __init__(self, accqsure, plot_id, plot_section_id, **kwargs):
        self.accqsure = accqsure
        self.plot_id = plot_id
        self.section_id = plot_section_id
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._order = self._entity.get("order")
        self._type = self._entity.get("type")
        self._status = self._entity.get("status")
        self._content = self._entity.get("content")

    @property
    def id(self) -> str:
        return self._id

    @property
    def order(self) -> int:
        return self._order

    @property
    def type(self) -> str:
        return self._type

    @property
    def status(self) -> str:
        return self._status

    @property
    def content(self) -> str:
        return self._content

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"PlotElement( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self
