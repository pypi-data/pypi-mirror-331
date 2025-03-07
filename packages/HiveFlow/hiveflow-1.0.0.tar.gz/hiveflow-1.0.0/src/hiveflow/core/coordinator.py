"""
Coordinator class for py-HiveFlow.
"""
import os
import time
import json
import uuid
import logging
import asyncio
from typing import Dict, Any, Optional, List, Type, Set, Tuple, Callable
from datetime import datetime

from hiveflow.core.task import Task

logger = logging.getLogger(__name__)

class Coordinator:
    """
    Coordinator class for managing tasks and workers in the py-HiveFlow framework.
    
    The coordinator is responsible for:
    - Accepting and distributing tasks to workers
    - Tracking worker status and capabilities
    - Monitoring task status and handling retries
    - Storing task results
    
    Attributes:
        redis_url (str): URL of the Redis instance for task queue and worker tracking
        db_url (Optional[str]): URL of the database for persistent storage
    """
    
    def __init__(self, 
                 redis_url: str,
                 db_url: Optional[str] = None,
                 worker_timeout: int = 60,
                 storage_backend: str = "redis"):
        """
        Initialize a new Coordinator.
        
        Args:
            redis_url: URL of the Redis instance
            db_url: URL of the database for persistent storage (optional)
            worker_timeout: Timeout in seconds for worker heartbeats
            storage_backend: Storage backend to use ("redis" or "postgresql")
        """
        self.redis_url = redis_url
        self.db_url = db_url
        self.worker_timeout = worker_timeout
        self.storage_backend = storage_backend
        
        # Runtime attributes
        self._running = False
        self._task_registry = {}  # Maps task type names to task classes
        self._worker_registry = {}  # Maps worker IDs to worker info
        self._task_queue = {}  # Maps task IDs to task info
        self._task_results = {}  # Maps task IDs to task results
        
        # Task hooks
        self._on_task_complete_hooks = []
        self._on_task_failed_hooks = []
    
    async def initialize(self) -> None:
        """
        Initialize the coordinator.
        
        This method connects to Redis and the database (if configured),
        and sets up the necessary data structures.
        """
        logger.info(f"Initializing coordinator with Redis at {self.redis_url}")
        
        # TODO: Implement actual Redis and DB connections
        
        # Placeholder for initialization logic
        self._running = True
        
        logger.info("Coordinator initialized successfully")
    
    async def start(self) -> None:
        """
        Start the coordinator.
        
        This method starts the coordinator services, including the worker monitoring
        task and the task scheduling task.
        """
        if not self._running:
            await self.initialize()
        
        logger.info("Starting coordinator services")
        
        # Start worker monitoring task
        asyncio.create_task(self._monitor_workers())
        
        # Start task scheduling task
        asyncio.create_task(self._schedule_tasks())
        
        logger.info("Coordinator services started")
    
    async def stop(self) -> None:
        """
        Stop the coordinator.
        
        This method stops all coordinator services gracefully.
        """
        logger.info("Stopping coordinator")
        self._running = False
        
        # TODO: Implement graceful shutdown logic
        
        logger.info("Coordinator stopped")
    
    async def register_task_type(self, task_class: Type[Task]) -> None:
        """
        Register a task type with the coordinator.
        
        Args:
            task_class: The task class to register
        """
        task_type = task_class.__name__
        self._task_registry[task_type] = task_class
        logger.info(f"Registered task type: {task_type}")
    
    async def submit_task(self, task: Task) -> str:
        """
        Submit a task for processing.
        
        Args:
            task: The task to submit
            
        Returns:
            str: The task ID
        """
        # Store the task
        task_data = task.to_dict()
        task_id = task.task_id
        
        # Add task to queue
        self._task_queue[task_id] = {
            "task": task_data,
            "status": "pending",
            "submitted_at": time.time(),
            "assigned_to": None,
            "attempts": 0,
            "last_updated": time.time()
        }
        
        logger.info(f"Task {task_id} submitted")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Dict[str, Any]: Task status information
        """
        if task_id in self._task_queue:
            return self._task_queue[task_id]
        elif task_id in self._task_results:
            return self._task_results[task_id]
        else:
            return {"status": "unknown", "error": "Task not found"}
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a completed task.
        
        Args:
            task_id: ID of the task to get the result for
            
        Returns:
            Optional[Dict[str, Any]]: Task result, or None if the task is not completed
        """
        if task_id in self._task_results:
            return self._task_results[task_id].get("result")
        return None
    
    async def register_worker(self, worker_id: str, capabilities: List[str],
                             hostname: str, ip_address: str) -> bool:
        """
        Register a worker with the coordinator.
        
        Args:
            worker_id: Unique ID of the worker
            capabilities: List of task types the worker can process
            hostname: Hostname of the worker
            ip_address: IP address of the worker
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        self._worker_registry[worker_id] = {
            "worker_id": worker_id,
            "capabilities": set(capabilities),
            "hostname": hostname,
            "ip_address": ip_address,
            "status": "idle",
            "last_heartbeat": time.time(),
            "current_task": None,
            "tasks_processed": 0,
            "registered_at": time.time()
        }
        
        logger.info(f"Worker {worker_id} registered with capabilities: {capabilities}")
        return True
    
    async def worker_heartbeat(self, worker_id: str, status: str, 
                              current_task: Optional[str] = None,
                              stats: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update worker heartbeat information.
        
        Args:
            worker_id: ID of the worker
            status: Current status of the worker
            current_task: ID of the task currently being processed (if any)
            stats: Worker statistics
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if worker_id not in self._worker_registry:
            logger.warning(f"Heartbeat from unregistered worker: {worker_id}")
            return False
        
        worker_info = self._worker_registry[worker_id]
        worker_info["last_heartbeat"] = time.time()
        worker_info["status"] = status
        worker_info["current_task"] = current_task
        
        if stats:
            for key, value in stats.items():
                worker_info[key] = value
        
        logger.debug(f"Heartbeat from worker {worker_id}: status={status}")
        return True
    
    async def report_task_complete(self, worker_id: str, task_id: str,
                                  result: Dict[str, Any]) -> bool:
        """
        Report that a task has been completed.
        
        Args:
            worker_id: ID of the worker that completed the task
            task_id: ID of the completed task
            result: Result of the task
            
        Returns:
            bool: True if the report was accepted, False otherwise
        """
        if task_id not in self._task_queue:
            logger.warning(f"Completion report for unknown task: {task_id}")
            return False
        
        task_info = self._task_queue[task_id]
        
        if task_info["assigned_to"] != worker_id:
            logger.warning(f"Task {task_id} was not assigned to worker {worker_id}")
            return False
        
        # Move task from queue to results
        self._task_results[task_id] = {
            "task": task_info["task"],
            "status": "completed",
            "result": result,
            "completed_by": worker_id,
            "completed_at": time.time(),
            "attempts": task_info["attempts"]
        }
        
        del self._task_queue[task_id]
        
        # Update worker info
        if worker_id in self._worker_registry:
            worker_info = self._worker_registry[worker_id]
            worker_info["tasks_processed"] = worker_info.get("tasks_processed", 0) + 1
            worker_info["current_task"] = None
            worker_info["status"] = "idle"
        
        # Run completion hooks
        for hook in self._on_task_complete_hooks:
            try:
                hook(task_id, result)
            except Exception as e:
                logger.error(f"Error in task completion hook: {e}")
        
        logger.info(f"Task {task_id} completed by worker {worker_id}")
        return True
    
    async def report_task_failure(self, worker_id: str, task_id: str,
                                 error: str) -> bool:
        """
        Report that a task has failed.
        
        Args:
            worker_id: ID of the worker that attempted the task
            task_id: ID of the failed task
            error: Error message
            
        Returns:
            bool: True if the report was accepted, False otherwise
        """
        if task_id not in self._task_queue:
            logger.warning(f"Failure report for unknown task: {task_id}")
            return False
        
        task_info = self._task_queue[task_id]
        
        if task_info["assigned_to"] != worker_id:
            logger.warning(f"Task {task_id} was not assigned to worker {worker_id}")
            return False
        
        # Update task info
        task_info["attempts"] += 1
        task_info["last_error"] = error
        task_info["last_updated"] = time.time()
        
        # Check if max retries reached
        task_data = task_info["task"]
        max_retries = task_data.get("max_retries", 3)
        
        if task_info["attempts"] >= max_retries:
            # Move task from queue to results
            self._task_results[task_id] = {
                "task": task_info["task"],
                "status": "failed",
                "error": error,
                "attempts": task_info["attempts"],
                "failed_at": time.time()
            }
            
            del self._task_queue[task_id]
            
            # Run failure hooks
            for hook in self._on_task_failed_hooks:
                try:
                    hook(task_id, error)
                except Exception as e:
                    logger.error(f"Error in task failure hook: {e}")
        else:
            # Reset task for retry
            task_info["status"] = "pending"
            task_info["assigned_to"] = None
        
        # Update worker info
        if worker_id in self._worker_registry:
            worker_info = self._worker_registry[worker_id]
            worker_info["current_task"] = None
            worker_info["status"] = "idle"
        
        logger.info(f"Task {task_id} failed (attempt {task_info['attempts']}): {error}")
        return True
    
    async def get_next_task(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next task for a worker to process.
        
        Args:
            worker_id: ID of the worker requesting a task
            
        Returns:
            Optional[Dict[str, Any]]: Task data, or None if no suitable task is available
        """
        if worker_id not in self._worker_registry:
            logger.warning(f"Task request from unregistered worker: {worker_id}")
            return None
        
        worker_info = self._worker_registry[worker_id]
        worker_capabilities = worker_info["capabilities"]
        
        # Find a suitable task
        for task_id, task_info in self._task_queue.items():
            if task_info["status"] != "pending":
                continue
            
            task_data = task_info["task"]
            task_type = task_data.get("task_type")
            
            if task_type in worker_capabilities:
                # Assign task to worker
                task_info["status"] = "assigned"
                task_info["assigned_to"] = worker_id
                task_info["assigned_at"] = time.time()
                task_info["last_updated"] = time.time()
                
                # Update worker info
                worker_info["status"] = "busy"
                worker_info["current_task"] = task_id
                
                logger.info(f"Task {task_id} assigned to worker {worker_id}")
                return task_data
        
        return None
    
    def on_task_complete(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Register a callback to be called when a task is completed.
        
        Args:
            callback: Callback function that takes task_id and result as arguments
        """
        self._on_task_complete_hooks.append(callback)
    
    def on_task_failed(self, callback: Callable[[str, str], None]) -> None:
        """
        Register a callback to be called when a task fails.
        
        Args:
            callback: Callback function that takes task_id and error as arguments
        """
        self._on_task_failed_hooks.append(callback)
    
    async def _monitor_workers(self) -> None:
        """
        Monitor worker heartbeats and remove inactive workers.
        
        This method runs periodically and checks for workers that have not sent
        a heartbeat within the specified timeout period.
        """
        while self._running:
            try:
                current_time = time.time()
                workers_to_remove = []
                
                for worker_id, worker_info in self._worker_registry.items():
                    last_heartbeat = worker_info["last_heartbeat"]
                    time_since_heartbeat = current_time - last_heartbeat
                    
                    if time_since_heartbeat > self.worker_timeout:
                        logger.warning(f"Worker {worker_id} has not sent a heartbeat for {time_since_heartbeat:.1f}s, marking as inactive")
                        workers_to_remove.append(worker_id)
                        
                        # Handle tasks assigned to this worker
                        current_task = worker_info["current_task"]
                        if current_task and current_task in self._task_queue:
                            task_info = self._task_queue[current_task]
                            task_info["status"] = "pending"
                            task_info["assigned_to"] = None
                            task_info["last_updated"] = current_time
                            logger.info(f"Task {current_task} reset to pending state after worker {worker_id} became inactive")
                
                # Remove inactive workers
                for worker_id in workers_to_remove:
                    del self._worker_registry[worker_id]
                
                await asyncio.sleep(self.worker_timeout / 2)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker monitoring: {e}")
                await asyncio.sleep(10)
    
    async def _schedule_tasks(self) -> None:
        """
        Schedule tasks for execution.
        
        This method runs periodically and schedules pending tasks for execution
        based on priorities and available workers.
        """
        while self._running:
            try:
                # Check for timed out tasks
                current_time = time.time()
                for task_id, task_info in list(self._task_queue.items()):
                    if task_info["status"] == "assigned":
                        assigned_at = task_info.get("assigned_at", 0)
                        time_since_assigned = current_time - assigned_at
                        
                        task_data = task_info["task"]
                        timeout = task_data.get("timeout")
                        
                        if timeout and time_since_assigned > timeout:
                            logger.warning(f"Task {task_id} timed out after {time_since_assigned:.1f}s")
                            
                            # Reset task for retry or fail
                            task_info["attempts"] += 1
                            task_info["last_error"] = "Task timed out"
                            task_info["last_updated"] = current_time
                            
                            # Check if max retries reached
                            max_retries = task_data.get("max_retries", 3)
                            
                            if task_info["attempts"] >= max_retries:
                                # Move task from queue to results
                                self._task_results[task_id] = {
                                    "task": task_data,
                                    "status": "failed",
                                    "error": "Task timed out",
                                    "attempts": task_info["attempts"],
                                    "failed_at": current_time
                                }
                                
                                del self._task_queue[task_id]
                                
                                # Run failure hooks
                                for hook in self._on_task_failed_hooks:
                                    try:
                                        hook(task_id, "Task timed out")
                                    except Exception as e:
                                        logger.error(f"Error in task failure hook: {e}")
                            else:
                                # Reset task for retry
                                task_info["status"] = "pending"
                                task_info["assigned_to"] = None
                
                await asyncio.sleep(1)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in task scheduling: {e}")
                await asyncio.sleep(10)
