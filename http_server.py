from aiohttp import web
from aiopath import AsyncPath
import mimetypes
import pathlib

BASE_DIR = AsyncPath(pathlib.Path(__file__).parent)
ERROR_PAGE = BASE_DIR.joinpath("index.html")
INDEX_PAGE = BASE_DIR.joinpath("error.html")
PAGE_CHARSET = "utf-8"

routes = web.RouteTableDef()

@routes.get('/')
@routes.get('/{name}')
async def variable_handler(request):
    status = 200
    charset = PAGE_CHARSET

    try:
        name = request.match_info['name']
    except KeyError:
        name = None

    if not name:
        docpath = INDEX_PAGE
    else:
        docpath = BASE_DIR.joinpath(name)

    if not await docpath.exists():
        docpath = ERROR_PAGE
        status = 404

    if docpath:
        mimetype, _ = mimetypes.guess_type(docpath)
        if not mimetype:
            mimetype = "text/plain"
        content_type = mimetype

    try:
        async with docpath.open("r", encoding=charset) as afp:
            html_data = await afp.readlines()
    except OSError:
        return f"Error while oppening a file {docpath}"

    body = "".join(html_data)
    return web.Response(
        body = body,
        status = status,
        content_type = content_type,
        charset=charset
    )

app = web.Application()
app.add_routes(routes)

web.run_app(app, port=8000)