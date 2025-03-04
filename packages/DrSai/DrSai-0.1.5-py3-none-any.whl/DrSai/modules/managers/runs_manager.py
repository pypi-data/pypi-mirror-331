"""
用来管理不同的用户所创建的线程，以及线程的状态
"""
from typing import List, Dict
import os, sys
from pathlib import Path
here = Path(__file__).parent
import time

try:
    from DrSai.version import __version__
except:
    sys.path.insert(1, f'{here.parent.parent.parent}')
    from DrSai.version import __version__
from DrSai.utils import BaseJsonSaver
from DrSai.configs import CONST, BaseArgs
from DrSai.version import __appname__

from DrSai.modules.managers.base_thread_message import ThreadMessage, Content, Text
from DrSai.modules.managers.base_run import ThreadRun, TruncationStrategy, Usage, Tool
from DrSai.modules.managers.base_thread import Thread, ThreadDeleted


raise DeprecationWarning("This module is deprecated, please use `DrSai.modules.managers.threads_manager` instead.")


class RunsManager(BaseJsonSaver):
    """
    用于管理所有的runs
    """

    version = "1.0.0"
    metadata = {
        "description": "Runs manager for all users",
        "mapping_username2indexes": {},  # 用来存储线程到run索引的映射，方便快速查找
    }

    def __init__(
        self,
        file_name: str = f'runs.json',
        file_dir: str = f'{Path.home()}/.{__appname__}',
        **kwargs
        ) -> None:
        super().__init__(auto_save=True, **kwargs)

        self.file_path = os.path.join(file_dir, file_name)
        self._data = self._init_load(self.file_path, version=self.version, metadata=self.metadata)
        self.debug = kwargs.get('debug', False)

    def create_runs(self, thread_id, assistant_id, **kwargs):
        save_immediately = kwargs.get('save_immediately', False)

        run_id = self.auto_id(prefix='run_', length=30, deduplicate=False)

        thread_run = Run(
            id=run_id,
            object="thread.run",
            created_at=int(time.time()),
            assistant_id=assistant_id,
            thread_id=thread_id,
            status="queued",
            started_at=int(time.time()),
            expires_at=None,
            cancelled_at=None,
            failed_at=None,
            completed_at=None,
            last_error=None,
            model=kwargs.get('model', CONST.DEFAULT_MODEL),
            instructions=kwargs.get('instructions', None),
            incomplete_details=None,
            tools=kwargs.get('tools', []),
            metadata={},
            usage=None,
            temperature=kwargs.get('temperature', BaseArgs.temperature),
            top_p=kwargs.get('top_p', BaseArgs.top_p),
            max_prompt_tokens=1000,
            max_completion_tokens=1000,
            truncation_strategy=TruncationStrategy(type="auto", last_messages=None),
            response_format="auto",
            tool_choice="auto"
        )

        return thread_run

if __name__ == "__main__":
    rm = RunsManager()

    run = rm.create_runs(thread_id="thread_1", assistant_id="assistant_1")
    print(f"run: {run}")

    pass
