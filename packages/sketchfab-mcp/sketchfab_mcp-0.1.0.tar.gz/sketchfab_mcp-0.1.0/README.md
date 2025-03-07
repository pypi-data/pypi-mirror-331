# Sketchfab MCP

A microservice for interacting with the Sketchfab API using MCP (Model Control Protocol).

## Features

- Search for downloadable models on Sketchfab
- Download a model from Sketchfab given a UID

## Environment Variables

- `SKETCHFAB_API_TOKEN`: Your Sketchfab API token

## Running with Docker

```bash
docker build -t sketchfab-mcp .
docker run -it --rm -p 8000:8000 -e SKETCHFAB_API_TOKEN=PLACEHOLDER sketchfab-mcp
```
