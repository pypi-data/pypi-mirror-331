import json
from ..routes.response import return_json_response


async def validation_exception_handler(_, exc):
    error = ''
    for error in exc.errors():
        location = " -> ".join([str(l) for l in error["loc"]])
        error = f"Error [location: '{location}'; message: '{error['msg']}', input: '{json.dumps(error['input'])}]'."
        break
    return return_json_response(data=error, status_code=422)
