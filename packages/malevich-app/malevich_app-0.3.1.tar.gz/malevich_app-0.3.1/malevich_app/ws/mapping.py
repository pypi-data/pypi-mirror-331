import base64
from typing import Dict, Optional, List, Callable, Type, Any, Tuple
from pydantic import BaseModel
from fastapi import Response

from malevich_app.export.abstract.abstract import LogsOperation, GetAppInfo, InputCollections, FunMetadata, \
    InitPipeline, InitRun, RunPipeline, Init, Run, Collection, Objects, WSObjectsReq
from malevich_app.export.api.api import ping, logs, app_functions_info, input_put, processor_put, output_put, \
    init_run_pipeline, init_pipeline, run_pipeline, init_run, init_put, run, finish, put_collection, put_objects, \
    get_objects


def __wrapper(fun: Callable, model: Optional[Type[BaseModel]] = None, with_response: bool = True, return_response: bool = False, keys_order: Optional[List[str]] = None, key_body: Optional[str] = None) -> Callable:   # key_body check only if keys_order exists
    async def internal_call(data: Optional[bytes]) -> Tuple[Optional[Any], Response]:
        data = None if model is None else model.model_validate_json(data)
        response = Response() if with_response else None

        args = []
        if data is not None:
            if keys_order is not None:
                data = data.model_dump()
                for key in keys_order:
                    args.append(data.get(key))

                if key_body is not None:
                    body_str = data.get(key_body)
                    response.body = base64.b64decode(body_str).decode('utf-8')
            else:
                args.append(data)
        if with_response:
            args.append(response)
        res = await fun(*args)
        if return_response:
            return None, res
        else:
            return res, response
    return internal_call


operations_mapping: Dict[str, ...] = {
    "ping": __wrapper(ping, with_response=False),
    "logs": __wrapper(logs, LogsOperation),
    "app_info": __wrapper(app_functions_info, GetAppInfo),
    "input": __wrapper(input_put, InputCollections),
    "processor": __wrapper(processor_put, FunMetadata),
    "output": __wrapper(output_put, FunMetadata),
    "init/pipeline": __wrapper(init_pipeline, InitPipeline),
    "init_run/pipeline": __wrapper(init_run_pipeline, InitRun,False, return_response=True),
    "run/pipeline": __wrapper(run_pipeline, RunPipeline),
    "init": __wrapper(init_put, Init),
    "init_run": __wrapper(init_run, InitRun, False, return_response=True),
    "run": __wrapper(run, Run),
    "finish": __wrapper(finish, FunMetadata, False, return_response=True),
    "collection": __wrapper(put_collection, Collection, False, return_response=True),
    "objects": __wrapper(put_objects, WSObjectsReq, return_response=True, keys_order=["operationId", "runId", "asset"], key_body="payload"),
    "objects/reverse": __wrapper(get_objects, Objects, False, return_response=True),
}
