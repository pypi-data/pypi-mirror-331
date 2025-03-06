from fastapi import WebSocket
from litegen import LLM
from liteutils import remove_references

from .base import Feature

import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from openai import OpenAI
import asyncio
from liteauto import compress,web


def streamer(res: str):
    "simulating streaming by using streamer"
    for i in range(0, len(res), 20):
        time.sleep(0.001)
        yield res[i:i + 20]


async def handle_google_search(websocket: WebSocket, message: str):
    """Handle Google search-like responses"""
    try:
        for chunk in streamer(message):
            await websocket.send_text(json.dumps({
                "sender": "bot",
                "message": chunk,
                "type": "stream"
            }))
            await asyncio.sleep(0.001)

        await websocket.send_text(json.dumps({
            "sender": "bot",
            "type": "end_stream"
        }))

    except Exception as e:
        await websocket.send_text(json.dumps({
            "sender": "bot",
            "message": f"Error: {str(e)}",
            "type": "error"
        }))

class FastGoogleSearch(Feature):
    """Google search feature implementation"""

    async def handle(self, websocket: WebSocket, message: str, system_prompt: str,
                     chat_history=None,**kwargs):
        from liteauto import google,wlanswer
        from liteauto.parselite import aparse

        max_urls = kwargs.get("is_websearch_k", 3)
        urls = google(message, max_urls=max_urls)

        web_results = await aparse(urls)
        web_results = [w for w in web_results if w.content]

        ctx = ""

        res = ""
        for w in web_results:
            try:
                if 'arxiv' in w.url:
                    content = remove_references(w.content)
                else:
                    content = w.content
                ans = wlanswer(content,message,k=2)
                ctx += ans+ "\n"
                res += f"Source: [{w.url}]\n\n{ans}\n"
                res += f"-"*50 + "\n"
            except:
                pass
        llm = LLM(api_key=kwargs['api_key'])
        llm_answer = llm(system_prompt="You are Answer summarize, answer the user question with context more detailed way",
                         prompt=f"context: {ctx}\n\n question: {message}")

        await handle_google_search(websocket=websocket,
                                   message=llm_answer)
    
    # async def handle(self, websocket: WebSocket, message: str, system_prompt: str,
    #                  chat_history=None,**kwargs):
    #     from liteauto import google,wlanswer
    #     from liteauto.parselite import aparse
    #
    #     max_urls = kwargs.get("is_websearch_k", 3)
    #     urls = google(message, max_urls=max_urls)
    #
    #     web_results = await aparse(urls)
    #     web_results = [w for w in web_results if w.content]
    #
    #     res = ""
    #     for w in web_results:
    #         try:
    #             if 'arxiv' in w.url:
    #                 content = remove_references(w.content)
    #             else:
    #                 content = w.content
    #             ans = wlanswer(content,message,k=2)
    #             res += f"Source: [{w.url}]\n\n{ans}\n"
    #             res += f"-"*50 + "\n"
    #         except:
    #             pass
    #
    #     await handle_google_search(websocket=websocket,
    #                                message=res)


