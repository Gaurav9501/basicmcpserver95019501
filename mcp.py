from typing import Any, Optional
import os
import json

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("movies")

# Base URL of your FastAPI Movies API (override with env if needed)
MOVIE_API_BASE = os.getenv("MOVIE_API_BASE", "https://basicrud95019501.onrender.com")

# Default headers for JSON APIs
JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}


# ---------------------------
# HTTP helper
# ---------------------------
async def api_request(
    method: str,
    path: str,
    json_body: Optional[dict[str, Any]] = None,
    timeout: float = 30.0,
) -> tuple[int, Optional[dict[str, Any]]]:
    """
    Make an HTTP request to the Movies API and return (status_code, json_or_none).
    Handles 204/empty responses gracefully.
    """
    url = f"{MOVIE_API_BASE}{path}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=method.upper(),
                url=url,
                json=json_body,
                headers=JSON_HEADERS,
                timeout=timeout,
            )
            # Some endpoints (e.g., DELETE) may return 204 No Content
            if resp.status_code == 204 or not resp.content:
                return resp.status_code, None

            # Try to parse JSON; if it fails, return None with status
            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, None
        except Exception as e:
            # Network/timeout/errors — surface a 0 code to indicate transport failure
            return 0, {"error": str(e), "url": url, "method": method, "body": json_body}


def pretty(data: Any) -> str:
    """Pretty print Python objects as JSON string for readable tool output."""
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return str(data)


# ---------------------------
# Tools
# ---------------------------

@mcp.tool()
async def get_movies() -> str:
    """
    Get all movies from the FastAPI backend.
    Returns a pretty JSON string of the list.
    """
    status, data = await api_request("GET", "/movies")
    if status == 0:
        return f"Transport error while calling /movies:\n{pretty(data)}"
    if status >= 400:
        return f"Error {status} from /movies:\n{pretty(data)}"
    return pretty(data)


@mcp.tool()
async def get_movie(movie_id: int) -> str:
    """
    Get a single movie by its ID.

    Args:
        movie_id: The numeric ID of the movie.
    """
    status, data = await api_request("GET", f"/movies/{movie_id}")
    if status == 0:
        return f"Transport error while calling /movies/{movie_id}:\n{pretty(data)}"
    if status == 404:
        return f"Movie {movie_id} not found."
    if status >= 400:
        return f"Error {status} from /movies/{movie_id}:\n{pretty(data)}"
    return pretty(data)


@mcp.tool()
async def create_movie(title: str, year: int, rating: float) -> str:
    """
    Create a new movie.

    Args:
        title: Movie title
        year: Release year
        rating: Rating as float (e.g., 8.6)
    """
    body = {"title": title, "year": year, "rating": rating}
    status, data = await api_request("POST", "/movies", json_body=body)
    if status == 0:
        return f"Transport error while POST /movies:\n{pretty(data)}"
    if status >= 400:
        return f"Error {status} creating movie:\n{pretty(data)}"
    return f"Movie created:\n{pretty(data)}"


@mcp.tool()
async def update_movie(movie_id: int, title: str, year: int, rating: float) -> str:
    """
    Update an existing movie by ID.

    Args:
        movie_id: The target movie ID
        title: New title
        year: New year
        rating: New rating
    """
    body = {"title": title, "year": year, "rating": rating}
    status, data = await api_request("PUT", f"/movies/{movie_id}", json_body=body)
    if status == 0:
        return f"Transport error while PUT /movies/{movie_id}:\n{pretty(data)}"
    if status == 404:
        return f"Movie {movie_id} not found."
    if status >= 400:
        return f"Error {status} updating movie {movie_id}:\n{pretty(data)}"
    return f"Movie updated:\n{pretty(data)}"


@mcp.tool()
async def delete_movie(movie_id: int) -> str:
    """
    Delete a movie by ID.

    Args:
        movie_id: The target movie ID
    """
    status, data = await api_request("DELETE", f"/movies/{movie_id}")
    if status == 0:
        return f"Transport error while DELETE /movies/{movie_id}:\n{pretty(data)}"
    if status == 404:
        return f"Movie {movie_id} not found."
    if status >= 400:
        return f"Error {status} deleting movie {movie_id}:\n{pretty(data)}"
    return f"Movie {movie_id} deleted (status {status})."


# ---------------------------
# Entry point
# ---------------------------
def main():
    # Run the MCP server over stdio (for hosts/clients to connect)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

 
