"""
设置Dr.Sai的OpenAPI Asistants 格式的标准接口, 使得Dr.Sai可以作为一个服务提供前端调用。
https://platform.openai.com/docs/api-reference/assistants
"""


import os, sys
from pathlib import Path
here = Path(__file__).parent
from typing import Generator, Optional, Union, Dict
from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse, JSONResponse, PlainTextResponse
from dataclasses import dataclass, field
import json
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Response
from fastapi import APIRouter, Query
import traceback
import uvicorn

from DrSai.configs import CONST

try:
    from DrSai.version import __version__
except:
    sys.path.append(str(here.parent.parent))
    from DrSai.version import __version__

import hepai
from hepai import HepAI, HRModel, HModelConfig, HWorkerConfig, HWorkerAPP

from DrSai.dr_sai import DrSai
from DrSai.configs import BaseArgs, BaseWorkerArgs
from DrSai.utils import Logger

from DrSai.version import __version__


logger = Logger.get_logger("app_worker.py")




class DrSaiAPP(DrSai):
    '''
    chat/completion:路由,直接处理聊天和自动回复请求。
    该路由接收前端页面的请求，并返回相应的回复。
    该路由的请求参数包括:
    - messages: 输入的消息列表

    OpenAI Assistants格式的标准接口的DrSai后端服务:
    该后端服务通过http请求或者hepai的openai assistants格式的标准接口api, 提供Dr.Sai多智能体后端服务。
    包括:
    1. Assistants-相关接口，包括创建、获取、删除、更新助手。用于对接前后端Agents设置和前端页面的交互。
    2. Threads-相关接口，包括创建、获取、删除、更新会话。用于对接前端页面的会话交互。
    3. Runs-相关接口，包括创建、获取、删除、更新运行。用于对接前端页面的运行交互。

    '''
    app = FastAPI()
    router = APIRouter(prefix="/apiv2", tags=["agent"])
    # app_args = AppArgs()
    # drsai_args = BaseArgs()
    
    def __init__(
            self, 
            # app_args: BaseWorkerArgs = None, 
            # drsai_args: BaseArgs = None, 
            **kwargs
        ):
        # DrSaiAPP.app_args = app_args or DrSaiAPP.app_args
        # DrSaiAPP.drsai_args = drsai_args or DrSaiAPP.drsai_args
        super(DrSaiAPP, self).__init__(**kwargs)
        # self.name = drsai_args.name
        # self.debug = app_args.debug

        self._init_router()
    
    def _init_router(self):
        # 测试路由
        DrSaiAPP.router.get("/")(self.index)

        # chat/completion路由
        DrSaiAPP.router.post("/chat/completions")(self.a_chat_completions)
        DrSaiAPP.router.post("/chat/completions_test")(self.a_chat_completions_test)

        # 关于Assistant的路由 TODO 删除 
        DrSaiAPP.router.post('/assistants')(self.a_create_assistants)  # 创建助手
        DrSaiAPP.router.get('/assistants')(self.a_list_assistants)  # 获取助手列表 # 
        DrSaiAPP.router.get('/assistants/{assistant_id}')(self.a_retrieve_assistants)  # 获取助手详情，retrieve
        DrSaiAPP.router.delete('/assistants/{assistant_id}')(self.a_delete_assistants)  # 删除助手，delete
        DrSaiAPP.router.post("/assistants/{assistant_id}")(self.a_update_assistants)  # 更新助手，update
        # 关于Threads的路由，相当于一次会话或一次任务
        DrSaiAPP.router.post('/threads')(self.a_create_threads)  # 创建会话
        DrSaiAPP.router.get('/threads/{thread_id}')(self.a_retrieve_threads)  # 获取会话详情，retrieve
        DrSaiAPP.router.delete('/threads/{thread_id}')(self.a_delete_threads)  # 删除会话，delete
        DrSaiAPP.router.post("/threads/{thread_id}")(self.a_update_threads)  # 更新会话，update
        # 关于Runs的路由
        DrSaiAPP.router.post('/threads/{thread_id}/runs')(self.aa_create_runs)  # 创建运行
        DrSaiAPP.router.post("/threads/runs")(self.a_create_thread_and_run)  # 创建线程并运行
        DrSaiAPP.router.get('/threads/{thread_id}/runs/{run_id}')(self.a_retrieve_runs)  # 获取运行详情，retrieve
        # 关于Messages的路由
        DrSaiAPP.router.post('/threads/{thread_id}/messages')(self.a_create_messages)  # 创建消息
        DrSaiAPP.router.get('/threads/{thread_id}/messages')(self.a_list_messages)  # 获取消息列表
        DrSaiAPP.router.get('/threads/{thread_id}/messages/{message_id}')(self.a_retrieve_messages)  # 获取消息详情，retrieve
        DrSaiAPP.router.post("/threads/{thread_id}/messages/{message_id}")(self.a_update_messages)  # 更新消息，update
        #关于文件的路由
        DrSaiAPP.router.post("/files")(self.a_create_files)
        DrSaiAPP.router.get("/files")(self.a_list_files)
        DrSaiAPP.router.get("/files/{file_id}/content")(self.a_get_file_content)
        DrSaiAPP.router.get("/files/{file_id}")(self.a_retrieve_files)
        DrSaiAPP.router.delete("/files/{file_id}")(self.a_delete_files)
        
        #关于vector store的路由
        DrSaiAPP.router.post("/vector_stores")(self.a_create_vector_stores) #创建一个vector store
        DrSaiAPP.router.get("/vector_stores")(self.a_list_vector_stores) #获取向量库列表
        DrSaiAPP.router.get("/vector_stores/{vector_store_id}")(self.a_retrieve_vector_stores) #检索向量库 vector_store_id
        DrSaiAPP.router.post("/vector_stores/{vector_store_id}")(self.a_update_vector_stores) #更新向量库
        DrSaiAPP.router.delete("/vector_stores/{vector_store_id}")(self.a_delete_vector_stores) #删除向量库
        
        #关于vector store files的路由
        DrSaiAPP.router.post("/vector_stores/{vector_store_id}/files")(self.a_create_vector_store_files)
        #DrSaiAPP.router.get("/vector_stores/{vector_store_id}/files")(self.a_list_vector_store_files)
        DrSaiAPP.router.post("/vector_stores/{vector_store_id}/file_batches")(self.a_create_vector_store_filebatch)                                                            

        # 关于AI绘图的路由
        DrSaiAPP.router.post("/images/generations")(self.a_ai_draw)
        DrSaiAPP.router.get("/images/{image_id}")(self.a_retrieve_image)

        # get model route
        DrSaiAPP.router.get("/models")(self.a_list_models) # 

    ### --- 关于chat_completions的路由 --- ###
    async def a_chat_completions_test(self, request: Request):
        # ref: https://platform.openai.com/docs/api-reference/chat
        apikey = request.headers.get("authorization").split(" ")[-1]
        params = await request.json()
        if "messages" not in params or "model" not in params:
            raise HTTPException(status_code=400, detail="messages and model must be required, see https://platform.openai.com/docs/api-reference/chat")
        return self.try_except_raise_http_exception(
            self.start_chat_completions, 
            HEPAI_API_KEY = apikey, **params
            )
        # return "chat_completions"
    
    async def a_chat_completions(self, request: Request):
        # ref: https://platform.openai.com/docs/api-reference/chat
        apikey = request.headers.get("authorization").split(" ")[-1]
        params = await request.json()
        if "messages" not in params or "model" not in params:
            raise HTTPException(status_code=400, detail="messages and model must be required, see https://platform.openai.com/docs/api-reference/chat")
        return self.try_except_raise_http_exception(
            self.start_chat_completions, 
            HEPAI_API_KEY = apikey, **params
            )
        # return "chat_completions"
    
    ### --- 关于list model的路由 --- ###
    async def a_list_models(self, request: Request):
        '''
        List all available models.
        '''
        api_key = request.headers.get("authorization").split(" ")[-1]

        def return_list_models(api_key: str,**kwargs):
            
            hepai_client = HepAI(api_key=api_key, base_url=CONST.BASE_URL_V2)
            base_models = []
            for model in hepai_client.models.list():
                base_models.append(model.id)

            data =  {
                "object": "list",
                "data": [],
                }
            data["data"].append({
                    "id": "hepai/drsai",
                    "object": "Agent",
                    "created": 1686935002,
                    "owned_by": "ihep",
                    "allowed_base_models": base_models
                    },) 
            # import json
            return data # f"data: {json.dumps(data)}\n\n"

        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            return_list_models,
            api_key=api_key,
            )
    
    ### --- 关于绘图的路由 --- ###
    async def a_ai_draw(self, request: Request):
        username = self.verify_headers(request.headers)["username"]
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.ai_drawing_tool.generate, username=username, **params
            )
    
    async def a_retrieve_image(self, request: Request, image_id: str):
        # return f"xxx {image_id}"
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.ai_drawing_tool.retrieve_image, username=username, image_id=image_id,
            cast_to=FileResponse,
            )
    
    #### --- 关于Messages的路由 --- ####
    async def a_create_messages(self, request: Request, thread_id: str):
        username = self.verify_headers(request.headers)["username"]
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.threads_mgr.create_message, 
            thread=thread_id, username=username, **params
            )
    
    async def a_list_messages(
            self, 
            request: Request, 
            thread_id: str,
            limit: int = Query(default=20, ge=1, le=100),  # ge is "greater than or equal"
            order: str = Query(default="desc", regex="^(asc|desc)$"),  # Using regex for validation
            after: Optional[str] = None,
            before: Optional[str] = None,
            run_id: Optional[str] = None,
            ):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.threads_mgr.list_messages, 
            thread_id=thread_id, limit=limit, order=order, after=after, 
            before=before, run_id=run_id, username=username
            )

    async def a_retrieve_messages(self, request: Request, thread_id: str, message_id: str):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.threads_mgr.retrieve_message, 
            thread_id=thread_id, message_id=message_id, username=username
            )
    
    async def a_update_messages(self, request: Request, thread_id: str, message_id: str):
        username = self.verify_headers(request.headers)["username"]
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.threads_mgr.update_message, 
            thread_id=thread_id, message_id=message_id, username=username, **params
            )
    
    #### --- 关于Runs的路由 --- ####
    async def a_retrieve_runs(self, request: Request, thread_id: str, run_id: str):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.threads_mgr.retrieve_run, thread_id=thread_id, run_id=run_id, username=username
            )
    
    async def a_create_thread_and_run(self, request: Request):
        username = self.verify_headers(request.headers)["username"]
        params = await request.json()
        asst_ids = params.pop("assistant_id", None)
        return self.try_except_raise_http_exception(
            self.create_thread_and_run, assistant_ids=asst_ids, username=username, **params
        )
    
    async def aa_create_runs(self, request: Request, thread_id: str):
        username = self.verify_headers(request.headers)["username"]
        params: dict = await request.json()
        if "assistant_id" not in params:
            raise HTTPException(status_code=400, detail="assistant_id is required")
        asst_id = params.pop("assistant_id")
        apikey = request.headers.get("authorization").split(" ")[-1]
        metadata: Optional[dict] = params.pop("metadata", {})
        params.update(metadata)
        return self.try_except_raise_http_exception(
            # self.threads_mgr.create_runs, 
            self.create_runs,
            thread_id=thread_id, 
            assistant_ids=asst_id,
            username=username, 
            HEPAI_API_KEY=apikey,
            **params
            )
        
    #### --- 关于Threads的路由 --- ####
    async def a_create_threads(self, request: Request):
        username = self.verify_headers(request.headers)["username"]
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.threads_mgr.create_threads, username=username, **params
            )
    
    async def a_delete_threads(self, request: Request, thread_id: str):
        username = self.verify_headers(request.headers)["username"]
        extra_query = request.query_params
        return self.try_except_raise_http_exception(
            self.threads_mgr.delete_thread, thread_id=thread_id, username=username,
            **extra_query, 
            )
    
    async def a_update_threads(self, request: Request, thread_id: str):
        username = self.verify_headers(request.headers)["username"]
        # 由于v1/threads/{thread_id}和v1/threads/runs路由冲突，因此需要判断
        if thread_id == "runs":
            return await self.a_create_thread_and_run(request)
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.threads_mgr.update_thread, thread_id=thread_id, username=username, **params
            )
    
    async def a_retrieve_threads(self, request: Request, thread_id: str):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.threads_mgr.retrieve_thread, thread_id=thread_id, username=username
            )

    #### --- 关于Assistant的路由 --- ####
    async def a_create_assistants(self, request: Request):  # 增加助手
        user_info = self.verify_headers(request.headers)
        # print(f"user_info: {user_info}")
        params = await request.json()#; params["api_key"] = user_info["api_key"]
        # new_assistant = self.assistants_mgr.create_assistant(username=username, **params)
        # return new_assistant
        return self.try_except_raise_http_exception(
            self.assistants_mgr.create_assistant, username=user_info["username"], **params)
    
    async def a_delete_assistants(self, request: Request, assistant_id: str):
        username = self.verify_headers(request.headers)["username"]
        # asst = self.assistants_mgr.delete_assistant(username=username, assistant_id=assistant_id)
        # return asst
        extra_query = request.query_params
        return self.try_except_raise_http_exception(
            self.assistants_mgr.delete_assistant, username=username, assistant_id=assistant_id,
            **extra_query,
            )
    
    async def a_update_assistants(self, request: Request, assistant_id: str):
        username = self.verify_headers(request.headers)["username"]
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.assistants_mgr.update_assistant, username=username, assistant_id=assistant_id, **params)
    
    async def a_retrieve_assistants(self, request: Request, assistant_id: str):
        username = self.verify_headers(request.headers)["username"]
        # asst = self.assistants_mgr.retrieve_assistant(username=username, assistant_id=assistant_id)
        # return asst
        return self.try_except_raise_http_exception(
            self.assistants_mgr.retrieve_assistant, username=username, assistant_id=assistant_id)
    
    async def a_list_assistants(
            self, 
            request: Request, 
            limit: int = Query(default=20, ge=1, le=100),  # ge is "greater than or equal"
            order: str = Query(default="desc", regex="^(asc|desc)$"),  # Using regex for validation
            after: Optional[str] = None,
            before: Optional[str] = None,
            ):
        """
        List assistants
        Args:
            limit: int, default=20, ge=1, le=100
            order: str, default="desc", regex="^(asc|desc)$"
            after: Optional[str], default=None
            before: Optional[str], default=None
        """
        # print(f"start a_list_assistants")
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.assistants_mgr.list_assistants,
            username=username, limit=limit, order=order, after=after, before=before)
    
    #### --- 关于DrSai的路由 --- ####
    async def index(self, request: Request):
        # return StreamingResponse(self.dr_sai.chatgroup(request))
        # res = await request.body()
        # res = self.app.dr_sai.get_status()
        # print(res)
        # print("Hello, World!")
        # raise HTTPException(status_code=404, detail=f"Image not found")
        return f"Hello, world! This is DrSai WebUI {__version__}"
    
    #### --- 关于File的路由 --- ####
    async def a_create_files(self,  request: Request, purpose: Optional[str] = Form(None), file: UploadFile = File(...)):
        # 验证API-KEY的代码here
        username = self.verify_headers(request.headers)["username"]
        logger.debug(f"Create file: {file.filename}, purpose: {purpose}")
        if purpose == "assistants":
            # Implement your file extraction logic here
            content = await file.read()
            file_json = self.files_mgr.create_file_client(content, file, 
                                                          purpose, username=username)
            return JSONResponse(file_json)
        else:
            return {"filename": file.filename, "purpose": "Unsupported purpose"}
        
    # list all files
    async def a_list_files(self, request: Request):
        # 验证API-KEY的代码here
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.files_mgr.list_files,
            username=username)
    
    # 获取具体ID的文件内容
    async def a_get_file_content(self, request: Request, file_id: str, authorization: Optional[str] = Header(None)):
        # 验证API-KEY的代码here
        # username = verify_api_key(authorization)
        username = self.verify_headers(request.headers)["username"]
        # 假设app.file_system.retrieve可以根据file_id检索文件内容
        try:
            file_content = self.files_mgr.get_file_content(file_id)
            headers = {"Content-Type": "text/plain; charset=utf-8"}
            return JSONResponse(file_content, headers=headers)
            # return Response(content=file_content, media_type="text/plain", headers=headers)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
    
    # 检索具体ID的文件内容
    async def a_retrieve_files(self, request: Request, file_id: str, authorization: Optional[str] = Header(None)):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.files_mgr.get_file_cliet, username=username, file_id=file_id)
    
    # 删除具体ID的文件
    async def a_delete_files(self, request: Request, file_id: str, authorization: Optional[str] = Header(None)):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.files_mgr.delete,
            file_id=file_id)


    ### --- 关于vector_store的路由 --- #### 
    async def a_create_vector_stores(self, request: Request): #增加知识向量库
        # 验证API-KEY的代码here
        username = self.verify_headers(request.headers)["username"]
        print(username)
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.vector_stores_mgr.create_vector_store_client, username=username, **params)
    
    async def a_list_vector_stores(
            self, 
            request: Request, 
            limit: int = Query(default=20, ge=1, le=100),  # ge is "greater than or equal"
            order: str = Query(default="desc", regex="^(asc|desc)$"),  # Using regex for validation
            after: Optional[str] = None,
            before: Optional[str] = None,
            ):
        """
        List assistants
        Args:
            limit: int, default=20, ge=1, le=100
            order: str, default="desc", regex="^(asc|desc)$"
            after: Optional[str], default=None
            before: Optional[str], default=None
        """
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.vector_stores_mgr.list_vector_stores,
            username=username, limit=limit, order=order, after=after, before=before)

    async def a_retrieve_vector_stores(self, request: Request, vector_store_id: str):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.vector_stores_mgr.retrieve_vector_store, username=username, vector_store_id=vector_store_id)
    
    async def a_update_vector_stores(self, request: Request, vector_store_id: str):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.vector_stores_mgr.modify_vector_store, username=username, vector_store_id=vector_store_id)
    
    async def a_delete_vector_stores(self, request: Request, vector_store_id: str):
        username = self.verify_headers(request.headers)["username"]
        extra_query = request.query_params
        return self.try_except_raise_http_exception(
            self.vector_stores_mgr.delete_vector_stores, username=username, vector_store_id=vector_store_id,
            **extra_query,
            )
    
    ### --- 关于vector_store_files的路由 --- #### 
    #知识向量库附加文件的路由
    async def a_create_vector_store_files(self, request: Request, vector_store_id: str):
        username = self.verify_headers(request.headers)["username"]
        #collection_name = "DrSai_user"
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.vector_store_files_mgr.create_vectorstorefile_client,
            vector_store_id=vector_store_id, username=username, **params
            )
    
    async def a_create_vector_store_filebatch(self, request: Request, vector_store_id: str):
        username = self.verify_headers(request.headers)["username"]
        collection_name = "DrSai_user"
        params = await request.json()
        return self.try_except_raise_http_exception(
            self.vector_store_files_mgr.bulk_upload_files_to_vector_store, collection_name=collection_name,
            vector_store_id=vector_store_id, username=username, **params
            )

    async def a_list_vector_store_files(
            self, 
            request: Request,
            vector_store_id: Optional[str], 
            limit: int = Query(default=20, ge=1, le=100),  # ge is "greater than or equal"
            order: str = Query(default="desc", regex="^(asc|desc)$"),  # Using regex for validation
            after: Optional[str] = None,
            before: Optional[str] = None,
            ):
        username = self.verify_headers(request.headers)["username"]
        return self.try_except_raise_http_exception(
            self.vector_store_files_mgr.list_vector_store_files,
            username=username, vector_store_id=vector_store_id, limit=limit, order=order, after=after, before=before)

    ### --- 其它函数 --- #### 
    def try_except_raise_http_exception(self, func, *args, **kwargs):
        """智能捕获函数内部raise的异常，转换为HTTPException返回，便于前端处理"""
        try:
            res = func(*args, **kwargs)
            if isinstance(res, Generator):
                return StreamingResponse(res)
            return res
        except Exception as e:
            # 获取报错类型：e.__class__.__name__
            # if self.debug:
                # logger.error(f"Error: {e}")
            # tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
            tb_str = traceback.format_exception(*sys.exc_info())
            tb_str = "".join(tb_str)
            logger.debug(f"Error: {e}.\nTraceback: {tb_str}")

            e_class = e.__class__.__name__
            if e_class == "ModuleNotFoundError":
                raise HTTPException(status_code=404, detail=f'{e_class}("{str(e)}")')
            elif e_class == "NotImplementedError":
                raise HTTPException(status_code=501, detail=f'{e_class}("{str(e)}")')
            ## TODO: 其他报错类型转换为合适的报错状态码
            raise HTTPException(status_code=400, detail=f'{e_class}("{str(e)}")')

class DrSaiWorkerModel(HRModel):  # Define a custom worker model inheriting from HRModel.
    def __init__(
            self, 
            config: HModelConfig,
            drsaiapp: DrSaiAPP = None # 传入DrSaiAPP实例
            ):
        super().__init__(config=config)

        # if drsaiapp is not None and isinstance(drsaiapp, type):
        #     self.drsai = drsaiapp()  # Instantiate the DrSaiAPP instance.
        # else:
        #     self.drsai = drsaiapp or DrSaiAPP()  # Instantiate the DrSaiAPP instance.
        # pass
        self.drsai = drsaiapp

    @HRModel.remote_callable  # Decorate the function to enable remote call.
    def custom_method(self, a: int = 1, b: int = 2) -> int:
        """Define your custom method here."""
        return a + b

    @HRModel.remote_callable
    def get_stream(self):
        for x in range(10):
            yield f"data: {json.dumps(x)}\n\n"

    @HRModel.remote_callable
    def chat_completions(self, *args, **kwargs):
        return self.drsai.start_chat_completions(*args, **kwargs)
    
    @HRModel.remote_callable
    def models(self, *args, **kwargs):
        return self.drsai.a_list_models(*args, **kwargs)

        # request = self.params2request(*args, **kwargs)
        # return self.drsai.a_chat_completions(request=request)


@dataclass
class DrSaiModelConfig(HModelConfig):
    name: str = field(default="hepai/drsai", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})

@dataclass
class DrSaiWorkerConfig(HWorkerConfig):
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=42801, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42801, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})
    # controller_address: str = field(default="https://aiapi001.ihep.ac.cn", metadata={"help": "The address of controller"})
    controller_address: str = field(default="http://localhost:42601", metadata={"help": "The address of controller"})
    
    controller_prefix: str = field(default="/apiv2", metadata={"help": "Controller's route prefix"})
    no_register: bool = field(default=True, metadata={"help": "Do not register to controller"})
    

    permissions: str = field(default='groups: default; users: admin, xiongdb@ihep.ac.cn, ddf_free; owner: xiongdb@ihep.ac.cn', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is Dr.Sai multi agents system', metadata={"help": "Model's description"})
    author: str = field(default=None, metadata={"help": "Model's author"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    type: str = field(default="drsai", metadata={"help": "Worker's type"})
    debug: bool = field(default=True, metadata={"help": "Debug mode"})

class Run_DrSaiAPP:
    def __init__(
            self,
            model_args: HModelConfig = DrSaiModelConfig,
            worker_args: HWorkerConfig = DrSaiWorkerConfig,
            **kwargs
            ):
        self.model_args, self.worker_args = hepai.parse_args((model_args, worker_args))
        print(self.model_args)
        print(self.worker_args)
        self.api_key = kwargs.pop('api_key', None)
        self.base_url = kwargs.pop('base_url', "https://aiapi.ihep.ac.cn/apiv2")
        self.base_models = kwargs.pop('base_models', None)

    def run_drsai(self, 
                  model_name: str = None,
                  host: str = None,
                  port: int = None,
                  no_register: bool = True,
                  controller_address="https://aiapi.ihep.ac.cn",
                  drsaiapp: DrSaiAPP = DrSaiAPP):  # 传入DrSaiAPP实例:
        
        if isinstance(drsaiapp, type): # 传入DrSaiAPP类而不是实例
            drsaiapp = drsaiapp(
                api_key=self.api_key,
                base_url=self.base_url,
                base_models=self.base_models,
            )  # Instantiate the DrSaiAPP instance.

        if model_name is not None:
            self.model_args.name = model_name
        model = DrSaiWorkerModel(config=self.model_args, drsaiapp=drsaiapp)

        if host is not None:
            self.worker_args.host = host
        if port is not None:
            self.worker_args.port = port
        if no_register is not None:
            self.worker_args.no_register = no_register
        self.worker_args.controller_address = controller_address
        self.app: FastAPI = HWorkerAPP(model, worker_config=self.worker_args)  # Instantiate the APP, which is a FastAPI application.
        self.app.include_router(model.drsai.router)
        print(self.app.worker.get_worker_info(), flush=True)
        # 启动服务
        uvicorn.run(self.app, host=self.app.host, port=self.app.port)
