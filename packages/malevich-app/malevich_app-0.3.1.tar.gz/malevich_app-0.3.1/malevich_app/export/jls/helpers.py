import asyncio
from typing import List, Tuple, Optional, Callable
import pandas as pd
from mypy_extensions import VarArg
from starlette.concurrency import run_in_threadpool
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.df import JDF
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.jls.WrapperMode import InputWrapper
from malevich_app.export.secondary.const import DOC_SCHEME_PREFIX, DOCS_SCHEME_PREFIX


async def get_schemes_info(julius_app, collections: List[Tuple[Collection, ...]]) -> Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[int]]:
    schemes_info, ret_type, sink_index = await julius_app.get_schemes_info()
    if julius_app.get_operation() == EntityType.INPUT and julius_app.get_input_mode() == InputWrapper.INPUT_DOC:
        assert ret_type is None or ret_type == "bool", f"wrong function return type={ret_type} (app id={julius_app.app_id})"

    if len(schemes_info) != len(collections) and sink_index is None:
        schemes_names = [x[1] for x in schemes_info]
        if not (julius_app.get_operation() == EntityType.OUTPUT and len(schemes_names) == 1 and schemes_names[0] is not None and len(schemes_names[0]) == 1 and schemes_names[0][0] is not None and schemes_names[0][0].endswith("*")):
            raise Exception(f"wrong function type, schemes={schemes_names}, collections={[tuple([subcollection.get() for subcollection in subcollections]) for subcollections in collections]}."
                            f" wrong count arguments: {len(schemes_names)} != {len(collections)} (app id={julius_app.app_id})")
    return schemes_info, sink_index


def get_params_names(fun: callable):
    return list(getattr(fun, "__annotations", fun.__annotations__).keys())


def is_async(fun: callable):
    return fun.__code__.co_flags & (1 << 7) != 0


async def run_func_in_threadpool(f: callable, *args, **kwargs):
    if is_async(f):
        return await run_in_threadpool(lambda: asyncio.run(f(*args, **kwargs)))
    else:
        return await run_in_threadpool(f, *args, **kwargs)


async def run_func(f: callable, *args, **kwargs):
    if is_async(f):
        return await f(*args, **kwargs)
    else:
        return f(*args, **kwargs)


class Object(object):
    pass


class PreContext:
    def _logs(self, *args, **kwargs):
        return ""


def is_docs_scheme(scheme: Optional[str]) -> bool:
    return scheme is not None and (scheme.startswith(DOC_SCHEME_PREFIX) or scheme.startswith(DOCS_SCHEME_PREFIX))
