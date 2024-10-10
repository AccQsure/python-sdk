class Text(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def generate(self, messages, max_tokens=2048, temperature=0.8, **kwargs):
        resp = await self.accqsure._query_stream(
            f"/text/generate",
            "POST",
            None,
            {
                **kwargs,
                **dict(
                    messages=messages, max_tokens=max_tokens, temperature=temperature
                ),
            },
        )
        return resp

    async def vectorize(self, inputs, **kwargs):
        resp = await self.accqsure._query(
            f"/text/vectorize", "POST", None, {**kwargs, **dict(inputs=inputs)}
        )
        return resp

    async def tokenize(self, inputs, **kwargs):
        resp = await self.accqsure._query(
            f"/text/tokenize", "POST", None, {**kwargs, **dict(inputs=inputs)}
        )
        return resp
