import asyncio
import sys
from datetime import datetime
from typing import Optional
from starlette.concurrency import run_in_threadpool
from malevich_app.export.jls.df import get_fun_info
from malevich_app.export.jls.helpers import is_async
from malevich_app.export.secondary.const import CONTEXT, START, END


class InitFunState:
    def __init__(self, j_app, init_fun: callable, id: str, tl: Optional[int]):
        self.j_app = j_app
        self.fun = init_fun
        self.fun_id = id
        self.tl = tl
        self.with_context = False

        fun_info = get_fun_info(init_fun)[0]
        if len(fun_info) != 0:
            assert len(fun_info) == 1 and fun_info[0][1] == CONTEXT, f"\"init\" must have no parameters or only Context (app id={j_app.app_id}, id={self.fun_id})"
            self.with_context = True

    def __init_fun(self, *args):
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {START}, {datetime.now()}\n")
        res = self.fun(*args)
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {END}, {datetime.now()}\n")
        return res

    async def __async_init_fun(self, *args):
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {START}, {datetime.now()}\n")
        res = await self.fun(*args)
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {END}, {datetime.now()}\n")
        return res

    async def run(self):
        args = [self.j_app._get_context(self.fun_id)] if self.with_context else []
        out = sys.stdout
        sys.stdout = self.j_app.logs_buffer     # TODO improve
        try:
            if is_async(self.fun):
                await asyncio.wait_for(self.__async_init_fun(*args), timeout=self.tl)
            else:
                await asyncio.wait_for(run_in_threadpool(lambda: self.__init_fun(*args)), timeout=self.tl)
            sys.stdout = out
        except BaseException as e:
            sys.stdout = out
            # self.j_app.logs_buffer.write(f"init app error: {traceback.format_exc()}\n")
            # log_error(f"init app error: {traceback.format_exc()}")
            raise e
