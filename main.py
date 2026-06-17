from pathlib import Path
import json

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import settings


app = FastAPI(title="AI Chatbot")


class ChatRequest(BaseModel):
    message: str
    stream: bool = True


class ChatResponse(BaseModel):
    response: str


async def _stream_response(body: ChatRequest):
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    messages = [SystemMessage(content=settings.system_prompt), HumanMessage(content=body.message)]
    async for chunk in llm.astream(messages):
        if content := chunk.content:
            yield f"data: {json.dumps({'token': content})}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/chat")
async def chat(body: ChatRequest):
    if body.stream:
        return StreamingResponse(_stream_response(body), media_type="text/event-stream")
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    messages = [SystemMessage(content=settings.system_prompt), HumanMessage(content=body.message)]
    result = await llm.ainvoke(messages)
    return ChatResponse(response=result.content)


ui_path = Path(__file__).parent / "ui" / "dist"
if ui_path.exists():
    app.mount("/", StaticFiles(directory=str(ui_path), html=True), name="ui")


def main():
    import uvicorn
    print(settings)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
