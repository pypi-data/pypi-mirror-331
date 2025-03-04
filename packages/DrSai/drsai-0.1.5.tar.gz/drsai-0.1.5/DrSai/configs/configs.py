"""
基于Python新的dataclasses类实现简单的配置
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from DrSai.configs import CONST

from .config import load_configs, get_llm_config

@dataclass
class BaseArgs:
    """
    Arguments of LLM
    """
    name: str = field(default=f"hepai/{CONST.APPNAME}", metadata={"help": "The name of the model."})
    # llm_config
    cache_seed: int = field(default=None, metadata={"help": "The seed for the cache, change it for different trials."})
    temperature: float = field(default=0.5, metadata={"help": "The temperature for sampling."})
    top_p: float = field(default=1.0, metadata={"help": "The top_p for sampling."})
    timeout: int = field(default=120, metadata={"help": "The timeout for the model."})

    config_file: str = field(default=f'{CONST.CONFIG_DIR}/hepai_llm_config.yaml', metadata={"help": "Path to the configuration file."})

    def __post_init__(self):
        config = load_configs(self.config_file, include_env=False)
        self.llm_config = get_llm_config(config)
    
    def get_hepai_config(self, HEPAI_API_KEY: str):
        for i, _ in enumerate(self.llm_config["config_list"]):
            if self.llm_config["config_list"][i]['base_url'] == CONST.BASE_URL:
                self.llm_config["config_list"][i]["api_key"] = HEPAI_API_KEY
        return self.llm_config

        


@dataclass
class AppArgs:
    """
    Arguments of DrSai Worker Backend
    """
    host : str = field(default="0.0.0.0", metadata={"help": "The host of the webui."})
    port : int = field(default=4280, metadata={"help": "The port of the webui."})
    test: bool = field(default=True, metadata={"help": "The test mode of the webui."})


@dataclass
class BaseWorkerArgs:  # Worker的参数配置和启动代码
    host: str = field(default="0.0.0.0", metadata={"help": "The ip of worker, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: str = field(default="auto", metadata={"help": "The port of worker"})
    controller_address: str = field(default="http://localhost:42901", metadata={"help": "The address of controller"})
    worker_address: str = field(default="auto", metadata={"help": "The address of worker, default is http://<ip>:<port>, the port will be assigned automatically from 42902 to 42999"})
    limit_model_concurrency: int = field(default=5, metadata={"help": "The concurrency limit the model"})
    stream_interval: float = field(default=0., metadata={"help": "Extra interval for stream response"})
    no_register: bool = field(default=True, metadata={"help": "Do not register to controller"})
    permissions: str = field(default="groups: public; owner: admin", metadata={"help": "Specify who can accesss the model, separated by ;, e.g., groups: all; users: a, b; owner: c"})
    description: str = field(default="This is a demo worker in HepAI-Distributed Deploy Framework", metadata={"help": "The description of the model"})
    author: str = field(default="hepai", metadata={"help": "The author of the model"})
    test: bool = field(default=False, metadata={"help": "Test mode, will not really start worker, just print the parameters"})
    

