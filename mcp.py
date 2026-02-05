import asyncio
import json
from typing import Optional

import httpx
from mcp.server import Server
from mcp.types import Tool, ToolResponse
from mcp.codec import (
    read_message_async,
    write_message_async,
)


MOVIE_API_URL = "https://basicrud95019501.onrender.com"   # << your FastAPI


# -------------------------------------------------------------------
# MCP SERVER
# -------------------------------------------------------------------
server = Server("movie-mcp-server")


# -----------------------
# Tools Definition
# -----------------------
@server.tool(
    Tool(
        name="get_movies",
        description="Get all movies from FastAPI backend.",
        input_schema={"type": "object", "properties": {}},
    )
)
async def get_movies_handler(params):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{MOVIE_API_URL}/movies")
        return ToolResponse(content=json.dumps(resp.json(), indent=2))


@server.tool(
    Tool(
        name="get_movie",
        description="Get a movie by its movie_id",
        input_schema={
            "type": "object",
            "properties": {"movie_id": {"type": "integer"}},
            "required": ["movie_id"],
        },
    )
)
async def get_movie_handler(params):
    movie_id = params["movie_id"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{MOVIE_API_URL}/movies/{movie_id}")
        return ToolResponse(content=json.dumps(resp.json(), indent=2))


@server.tool(
    Tool(
        name="create_movie",
        description="Create a new movie",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "year": {"type": "integer"},
                "rating": {"type": "number"},
            },
            "required": ["title", "year", "rating"],
        },
    )
)
async def create_movie_handler(params):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{MOVIE_API_URL}/movies", json=params)
        return ToolResponse(content=json.dumps(resp.json(), indent=2))


@server.tool(
    Tool(
        name="update_movie",
        description="Update movie by movie_id",
        input_schema={
            "type": "object",
            "properties": {
                "movie_id": {"type": "integer"},
                "title": {"type": "string"},
                "year": {"type": "integer"},
                "rating": {"type": "number"},
            },
            "required": ["movie_id", "title", "year", "rating"],
        },
    )
)
async def update_movie_handler(params):
    movie_id = params["movie_id"]
    body = {
        "title": params["title"],
        "year": params["year"],
        "rating": params["rating"],
    }
    async with httpx.AsyncClient() as client:
        resp = await client.put(f"{MOVIE_API_URL}/movies/{movie_id}", json=body)
        return ToolResponse(content=json.dumps(resp.json(), indent=2))


@server.tool(
    Tool(
        name="delete_movie",
        description="Delete movie by movie_id",
        input_schema={
            "type": "object",
            "properties": {"movie_id": {"type": "integer"}},
            "required": ["movie_id"],
        },
    )
)
async def delete_movie_handler(params):
    movie_id = params["movie_id"]
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{MOVIE_API_URL}/movies/{movie_id}")
        return ToolResponse(content=json.dumps({"status": resp.status_code}, indent=2))


# -------------------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------------------
async def main():
    while True:
        msg = await read_message_async()
        if msg is None:
            break

        reply = await server.handle_message(msg)
        if reply is not None:
            await write_message_async(reply)


if __name__ == "__main__":
    asyncio.run(main())
