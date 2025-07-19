FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install uv

RUN uv sync

CMD ["uv", "run", "fastmcp", "run", "mcp_server/callmind_mcp.py"]
