import logging

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

import config
from logging_config import setup_logging
from upstream import resolve_upstream

setup_logging()
logger = logging.getLogger(__name__)

_SKIP_RESPONSE_HEADERS = {'content-length', 'transfer-encoding', 'connection'}

app = FastAPI(title='Cinemaabyss proxy')
client = httpx.AsyncClient(
    timeout=httpx.Timeout(config.UPSTREAM_TIMEOUT), follow_redirects=False
)


@app.on_event('shutdown')
async def _shutdown() -> None:
    await client.aclose()


@app.get('/health')
async def health() -> Response:
    return Response(content='proxy is healthy')


@app.api_route(
    '/{full_path:path}',
    methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD'],
)
async def proxy(full_path: str, request: Request) -> Response:
    path = '/' + full_path
    base_url = resolve_upstream(path)

    url = base_url + path
    if request.url.query:
        url += '?' + request.url.query

    body = await request.body()

    try:
        upstream = await client.request(
            request.method, url, headers=dict(request.headers), content=body
        )
    except httpx.RequestError as exc:
        logger.error('upstream error for %s: %s', url, exc)
        return JSONResponse({'error': 'Bad Gateway'}, status_code=502)

    headers = {
        k: v for k, v in upstream.headers.items()
        if k.lower() not in _SKIP_RESPONSE_HEADERS
    }
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=headers,
    )
