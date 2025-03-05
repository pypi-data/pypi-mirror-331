import os
import sys
from kirara_ai.workflow.core.block import BlockRegistry
from kirara_ai.ioc.container import DependencyContainer
from kirara_ai.workflow.core.workflow.registry import WorkflowRegistry
from typing import Dict, Any, List
from kirara_ai.plugin_manager.plugin import Plugin
from kirara_ai.logger import get_logger
from .storage import TaskStorage
from datetime import datetime
from kirara_ai.im.adapter import IMAdapter
from .blocks import CreateTaskBlock,AutoExecuteTools,CreateOneTimeTaskBlock,GetTasksBlock,DeleteTaskBlock,DeleteAllTasksBlock,URLToMessageBlock
logger = get_logger("Scheduler")

class SchedulerPlugin(Plugin):
    def __init__(self,  block_registry: BlockRegistry, container: DependencyContainer):
        super().__init__()
        db_path = os.path.join(os.path.dirname(__file__), "tasks.db")
        self.storage = TaskStorage(db_path)
        self.scheduler = None
        self.block_registry = block_registry
        self.workflow_registry = container.resolve(WorkflowRegistry)
        self.container = container
        # 在安装完依赖后再导入

    def on_load(self):
        logger.info("SchedulerPlugin loaded")
        from .scheduler import TaskScheduler
        self.scheduler = TaskScheduler(self.storage, None)
        self.scheduler.start()
        try:
            self.block_registry.register("create_task", "scheduler", CreateTaskBlock)
            self.block_registry.register("create_one_time_task", "scheduler", CreateOneTimeTaskBlock)
            self.block_registry.register("get_tasks", "scheduler", GetTasksBlock)
            self.block_registry.register("delete_task", "scheduler", DeleteTaskBlock)
            self.block_registry.register("delete_all_tasks", "scheduler", DeleteAllTasksBlock)
        except Exception as e:
            logger.warning(f"create_task failed: {e}")
        try:
            self.block_registry.register("auto_execute_tools", "auto", AutoExecuteTools)
            self.block_registry.register("url_to_message", "auto", URLToMessageBlock)

        except Exception as e:
            logger.warning(f"find_scheduler_corn failed: {e}")

    def on_start(self):
        logger.info("SchedulerPlugin started")

    def on_stop(self):
        if self.scheduler:
            self.scheduler.shutdown()
        logger.info("SchedulerPlugin stopped")


