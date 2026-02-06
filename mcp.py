from typing import Any, Optional
import os
import json

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("tasks")

# Base URL of your FastAPI Task API
TASK_API_BASE = os.getenv("TASK_API_BASE", "http://localhost:8000")

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
    Make an HTTP request to the Task API and return (status_code, json_or_none).
    Handles 204/empty responses gracefully.
    """
    url = f"{TASK_API_BASE}{path}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=method.upper(),
                url=url,
                json=json_body,
                headers=JSON_HEADERS,
                timeout=timeout,
            )

            if resp.status_code == 204 or not resp.content:
                return resp.status_code, None

            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, None

        except Exception as e:
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
async def get_tasks() -> str:
    """Get all tasks."""
    status, data = await api_request("GET", "/tasks")
    if status == 0:
        return f"Transport error while calling /tasks:\n{pretty(data)}"
    if status >= 400:
        return f"Error {status} from /tasks:\n{pretty(data)}"
    return pretty(data)


@mcp.tool()
async def get_task(task_id: int) -> str:
    """Get a single task by ID."""
    status, data = await api_request("GET", f"/tasks/{task_id}")
    if status == 0:
        return f"Transport error while calling /tasks/{task_id}:\n{pretty(data)}"
    if status == 404:
        return f"Task {task_id} not found."
    if status >= 400:
        return f"Error {status} from /tasks/{task_id}:\n{pretty(data)}"
    return pretty(data)


@mcp.tool()
async def create_task(title: str, done: bool = False) -> str:
    """Create a new task."""
    body = {"title": title, "done": done}
    status, data = await api_request("POST", "/tasks", json_body=body)

    if status == 0:
        return f"Transport error while POST /tasks:\n{pretty(data)}"
    if status >= 400:
        return f"Error {status} creating task:\n{pretty(data)}"

    return f"Task created:\n{pretty(data)}"


@mcp.tool()
async def update_task(task_id: int, title: str, done: bool = False) -> str:
    """Update an existing task."""
    body = {"title": title, "done": done}
    status, data = await api_request("PUT", f"/tasks/{task_id}", json_body=body)

    if status == 0:
        return f"Transport error while PUT /tasks/{task_id}:\n{pretty(data)}"
    if status == 404:
        return f"Task {task_id} not found."
    if status >= 400:
        return f"Error {status} updating task {task_id}:\n{pretty(data)}"

    return f"Task updated:\n{pretty(data)}"


@mcp.tool()
async def delete_task(task_id: int) -> str:
    """Delete a task by ID."""
    status, data = await api_request("DELETE", f"/tasks/{task_id}")

    if status == 0:
        return f"Transport error while DELETE /tasks/{task_id}:\n{pretty(data)}"
    if status == 404:
        return f"Task {task_id} not found."
    if status >= 400:
        return f"Error {status} deleting task {task_id}:\n{pretty(data)}"

    return f"Task {task_id} deleted (status {status})."


# ---------------------------
# Entry point
# ---------------------------
def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

 
