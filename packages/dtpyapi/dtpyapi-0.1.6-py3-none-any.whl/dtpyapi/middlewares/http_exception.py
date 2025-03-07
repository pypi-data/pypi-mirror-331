from ..routes.response import return_json_response


async def http_exception_handler(request, exc):
    status_code = exc.status_code
    detail = request.url.path if status_code == 404 else exc.detail
    return return_json_response(data=str(detail), status_code=status_code)
