# # # # # # # # # # # # # # # # # # # # # # # # # # #
# This script is used to use hepai client functions.#
# Author: xiongdb                                   #
# Date: 2025-01-01                                  #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

import hepai
from hepai import HepAI
from DrSai.configs import CONST

class HepAIFunction:
    def __init__(
            self, 
            api_key: str = None, 
            base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_hai_client(
            self, 
            api_key: str = None, 
            base_url: str = None,
            version="v1",
            **kwargs) -> HepAI:
        if version == "v1":
            BASE_URL = CONST.BASE_URL
        elif version == "v2":
            BASE_URL = CONST.BASE_URL_V2
        else:
            raise ValueError(f"Unsupported version: {version}")
        base_url = base_url or BASE_URL
        api_key = api_key or self.api_key
        if api_key is None:
            raise ValueError("API key is not provided.")
        return HepAI(api_key=api_key, base_url=base_url, **kwargs)
    