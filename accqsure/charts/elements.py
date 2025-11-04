import json
import logging


class ChartElements(object):
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
        return ChartElement(
            self.accqsure, self.chart_id, self.section_id, **resp
        )

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        chart_elements = [
            ChartElement(
                self.accqsure, self.chart_id, self.section_id, **chart_element
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
        metadata=None,
        **kwargs,
    ):

        data = dict(
            order=order,
            type=element_type,
            description=description,
            prompt=prompt,
            for_each=for_each,
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
        chart_element = ChartElement(self.accqsure, **resp)
        logging.info("Created Chart %s with id %s", order, chart_element.id)

        return chart_element

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{id_}",
            "DELETE",
            {**kwargs},
        )


class ChartElement:
    def __init__(self, accqsure, chart_id, chart_section_id, **kwargs):
        self.accqsure = accqsure
        self.chart_id = chart_id
        self.section_id = chart_section_id
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
        return f"ChartElement( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self
