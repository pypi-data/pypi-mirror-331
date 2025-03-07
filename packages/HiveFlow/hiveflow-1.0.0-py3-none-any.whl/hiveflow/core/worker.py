"""
Base Worker class for py-HiveFlow.
"""
import os
import uuid
import time
import json
import logging
import asyncio
import socket
from typing import Dict, Any, Optional, List, Type, Set, Tuple
from abc import ABC, abstractmethod

from hiveflow.core.task import Task

logger = logging.getLogger(__name__)

class Worker(ABC):
    """
    Abstract base class for all workers in the py-HiveFlow framework.
    
    A worker is responsible for processing tasks. It connects to the coordinator,
    retrieves tasks, processes them, and reports the results back.
    
    Attributes:
        worker_id (str): Unique identifier for the worker
        coordinator_url (str): URL of the coordinator
        status (str): Current status of the worker (idle, busy, etc.)
        capabilities (Set[str]): Set of task types this worker can process
        stats (Dict[str, Any]): Statistics about the worker's performance
    """
    
    def __init__(self, 
                coordinator_url: str,
                worker_id: Optional[str] = None,
                heartbeat_interval: int = 10):
        """
        Initialize a new Worker.
        
        Args:
            coordinator_url: URL of the coordinator service
            worker_id: Unique identifier for the worker. If None, a UUID will be generated.
            heartbeat_interval: Interval in seconds between heartbeat messages
        """
        # Generate worker ID if not provided
        if worker_id is None:
            hostname = socket.gethostname()
            unique_id = str(uuid.uuid4())[:8]
            self.worker_id = f"{hostname}-{unique_id}"
        else:
            self.worker_id = worker_id
        
        self.coordinator_url = coordinator_url
        self.status = "idle"
        self.capabilities = self._detect_capabilities()
        self.heartbeat_interval = heartbeat_interval
        
        # Statistics
        self.stats = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "tasks_succeeded": 0,
            "processing_time": 0.0,
            "last_task_id": None,
            "start_time": time.time()
        }
        
        # Runtime attributes
        self._running = False
        self._current_task = None
        self._heartbeat_task = None
    
    def _detect_capabilities(self) -> Set[str]:
        """
        Detect the capabilities of this worker.
        
        Returns:
            Set[str]: Set of task types this worker can process
        """
        capabilities = set()
        
        # Add capabilities based on can_process method
        for attr_name in dir(self):
            if attr_name.startswith('process_') and callable(getattr(self, attr_name)):
                task_type = attr_name[8:]  # Remove 'process_' prefix
                if task_type:
                    capabilities.add(task_type)
        
        return capabilities
    
    @abstractmethod
    def setup(self) -> None:
        """
        Set up the worker before starting to process tasks.
        
        This method should initialize any resources needed by the worker.
        """
        pass
    
    @abstractmethod
    def can_process(self, task: Task) -> bool:
        """
        Check if this worker can process the given task.
        
        Args:
            task: The task to check
            
        Returns:
            bool: True if the worker can process the task, False otherwise
        """
        pass
    
    @abstractmethod
    def process_task(self, task: Task) -> Dict[str, Any]:
        """
        Process a task.
        
        Args:
            task: The task to process
            
        Returns:
            Dict[str, Any]: Result of the processing
        """
        pass
    
    async def run(self) -> None:
        """
        Start the worker and begin processing tasks.
        
        This method will run indefinitely until stop() is called.
        """
        self._running = True
        
        # Set up the worker
        try:
            self.setup()
        except Exception as e:
            logger.error(f"Failed to set up worker: {e}")
            self._running = False
            return
        
        logger.info(f"Worker {self.worker_id} started with capabilities: {self.capabilities}")
        
        # Start heartbeat task
        self._heartbeat_task = asyncio.create_task(self._send_heartbeat())
        
        # Main worker loop
        while self._running:
            try:
                # Get next task from coordinator
                task = await self._get_next_task()
                
                if task is None:
                    # No task available, wait a bit
                    self.status = "idle"
                    await asyncio.sleep(1)
                    continue
                
                # Process the task
                self._current_task = task
                self.status = "busy"
                
                # Track processing time
                start_time = time.time()
                
                try:
                    result = await self._process_and_report(task)
                    self.stats["tasks_succeeded"] += 1
                except Exception as e:
                    logger.error(f"Error processing task {task.task_id}: {e}")
                    await self._report_task_failure(task, str(e))
                    self.stats["tasks_failed"] += 1
                
                # Update stats
                processing_time = time.time() - start_time
                self.stats["processing_time"] += processing_time
                self.stats["tasks_processed"] += 1
                self.stats["last_task_id"] = task.task_id
                
                self._current_task = None
                self.status = "idle"
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(5)  # Wait a bit before retrying
        
        # Clean up
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    async def stop(self) -> None:
        """
        Stop the worker.
        
        This method will stop the worker gracefully after the current task is completed.
        """
        self._running = False
    
    async def _get_next_task(self) -> Optional[Task]:
        """
        Get the next task from the coordinator.
        
        Returns:
            Optional[Task]: The next task to process, or None if no tasks are available
        """
        # This would be implemented with actual API calls to the coordinator
        # For now, we'll just return None as a placeholder
        return None
    
    async def _process_and_report(self, task: Task) -> Dict[str, Any]:
        """
        Process a task and report the result to the coordinator.
        
        Args:
            task: The task to process
            
        Returns:
            Dict[str, Any]: Result of the processing
        """
        # Process the task
        result = self.process_task(task)
        
        # Report the result
        await self._report_task_success(task, result)
        
        return result
    
    async def _report_task_success(self, task: Task, result: Dict[str, Any]) -> None:
        """
        Report successful task processing to the coordinator.
        
        Args:
            task: The processed task
            result: Result of the processing
        """
        # This would be implemented with actual API calls to the coordinator
        pass
    
    async def _report_task_failure(self, task: Task, error: str) -> None:
        """
        Report task processing failure to the coordinator.
        
        Args:
            task: The failed task
            error: Error message
        """
        # This would be implemented with actual API calls to the coordinator
        pass
    
    async def _send_heartbeat(self) -> None:
        """
        Send periodic heartbeat messages to the coordinator.
        
        This method runs in a separate task and sends heartbeat messages to the coordinator
        at the specified interval.
        """
        while self._running:
            try:
                # Send heartbeat to coordinator
                # This would be implemented with actual API calls to the coordinator
                
                # Update stats for heartbeat
                uptime = time.time() - self.stats["start_time"]
                current_stats = {
                    **self.stats,
                    "status": self.status,
                    "uptime": uptime,
                    "capabilities": list(self.capabilities),
                    "current_task_id": self._current_task.task_id if self._current_task else None
                }
                
                # TODO: Actually send the heartbeat
                logger.debug(f"Heartbeat sent: {current_stats}")
                
                # Wait for the next interval
                await asyncio.sleep(self.heartbeat_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(self.heartbeat_interval)
