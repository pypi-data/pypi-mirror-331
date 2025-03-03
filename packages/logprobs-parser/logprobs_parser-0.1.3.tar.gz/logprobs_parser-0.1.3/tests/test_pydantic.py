from pydantic import BaseModel

from logprobs_parser.types import JSONArrayLogprob, JSONLogprob, JSONObjectLogprob, Token, ValueLogprob


class WrapperModel(BaseModel):
    json_any: JSONLogprob
    json_primitive: ValueLogprob
    json_array: JSONArrayLogprob
    json_object: JSONObjectLogprob


def test_wrapper():
    wrapper = WrapperModel(
        json_any=ValueLogprob(value=1, logprob=0.1, tokens=[Token(token="1", logprob=0.1)]),
        json_primitive=ValueLogprob(value=1, logprob=0.1, tokens=[Token(token="1", logprob=0.1)]),
        json_array=[ValueLogprob(value=1, logprob=0.1, tokens=[Token(token="1", logprob=0.1)])],
        json_object={"key": ValueLogprob(value=1, logprob=0.1, tokens=[Token(token="1", logprob=0.1)])},
    )
    wrapper.model_dump_json()
