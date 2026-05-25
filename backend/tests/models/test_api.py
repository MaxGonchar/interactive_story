import pytest
from app.models.api import RegenerateData, RegenerateResponse, MessageModel


def test_regenerate_response_validates():
    msg = MessageModel(id=1, role="assistant", content="x")
    data = RegenerateData(assistant_message=msg)
    resp = RegenerateResponse(data=data)
    assert resp.data.assistant_message.id == 1
    assert resp.data.assistant_message.role == "assistant"
    assert resp.data.assistant_message.content == "x"
