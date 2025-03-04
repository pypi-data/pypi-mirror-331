from DrSai import DrSaiAPP, Run_DrSaiAPP
from DrSai.apis.base_agent_api import LearnableAgent, HostAgent

def run_console(
        agent: LearnableAgent | HostAgent,
        task: str
):
    '''
    命令行启动
    '''
    drsaiapp = DrSaiAPP(agent=agent)
    drsaiapp.start_runs(messages=[{"role":"relo", "content":task}])

def run_backend(agent: LearnableAgent | HostAgent, **kwargs):
    '''
    启动后端服务
    '''
    drsaiapp = DrSaiAPP(agent=agent)

    model_name: str = kwargs.get("model_name", None)
    host: str =  kwargs.get("host", None)
    port: int =  kwargs.get("port", None)
    no_register: bool =  kwargs.get("no_register", True)
    controller_address: str =  kwargs.get("controller_address", "http://localhost:42601")
    Run_DrSaiAPP().run_drsai(
        model_name=model_name,
        host=host,
        port=port,
        no_register=no_register,
        controller_address=controller_address,
        drsaiapp=drsaiapp
    )

def run_hepai_worker(agent: LearnableAgent | HostAgent, **kwargs):
    '''
    启动Hepai Worker
    '''
    drsaiapp = DrSaiAPP(agent=agent)

    model_name: str = kwargs.get("model_name", None)
    host: str =  kwargs.get("host", None)
    port: int =  kwargs.get("port", None)
    no_register: bool =  kwargs.get("no_register", False)
    controller_address: str =  kwargs.get("controller_address", "https://aiapi.ihep.ac.cn")
    Run_DrSaiAPP().run_drsai(
        model_name=model_name,
        host=host,
        port=port,
        no_register=no_register,
        controller_address=controller_address,
        drsaiapp=drsaiapp
    )