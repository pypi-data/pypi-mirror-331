"""
Base Task class for py-HiveFlow.
"""
import uuid
import json
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class Task(ABC):
    """
    Abstract base class for all tasks in the py-HiveFlow framework.
    
    A task is a unit of work that can be processed by a worker. It encapsulates
    all the information needed to process the work, as well as methods for
    serialization and deserialization.
    
    Attributes:
        task_id (str): Unique identifier for the task
        created_at (float): Timestamp when the task was created
        priority (int): Priority of the task (higher value means higher priority)
        retry_count (int): Number of times this task has been retried
        max_retries (int): Maximum number of retries allowed
        timeout (Optional[int]): Timeout in seconds, or None for no timeout
    """
    
    def __init__(self, 
                 task_id: Optional[str] = None, 
                 priority: int = 0, 
                 max_retries: int = 3,
                 timeout: Optional[int] = None):
        """
        Initialize a new Task.
        
        Args:
            task_id: Unique identifier for the task. If None, a UUID will be generated.
            priority: Priority of the task (higher value means higher priority).
            max_retries: Maximum number of retries allowed.
            timeout: Timeout in seconds, or None for no timeout.
        """
        self.task_id = task_id or str(uuid.uuid4())
        self.created_at = time.time()
        self.priority = priority
        self.retry_count = 0
        self.max_retries = max_retries
        self.timeout = timeout
    
    @abstractmethod
    def process(self, worker: Any) -> Dict[str, Any]:
        """
        Process the task using the provided worker.
        
        This method must be implemented by subclasses to define how the task is processed.
        
        Args:
            worker: The worker that will process the task.
            
        Returns:
            Dict[str, Any]: Result of the processing.
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the task.
        """
        return {
            "task_id": self.task_id,
            "created_at": self.created_at,
            "priority": self.priority,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "task_type": self.__class__.__name__
        }
    
    def to_json(self) -> str:
        """
        Convert the task to a JSON string.
        
        Returns:
            str: JSON representation of the task.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task from a dictionary.
        
        Args:
            data: Dictionary containing task data.
            
        Returns:
            Task: A new task instance.
        """
        raise NotImplementedError("Subclasses must implement from_dict method")
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Task':
        """
        Create a task from a JSON string.
        
        Args:
            json_str: JSON string containing task data.
            
        Returns:
            Task: A new task instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def mark_as_retried(self) -> None:
        """
        Mark the task as retried, incrementing the retry count.
        """
        self.retry_count += 1
    
    def can_retry(self) -> bool:
        """
        Check if the task can be retried.
        
        Returns:
            bool: True if the task can be retried, False otherwise.
        """
        return self.retry_count < self.max_retries
    
    def has_timed_out(self, current_time: Optional[float] = None) -> bool:
        """
        Check if the task has timed out.
        
        Args:
            current_time: Current time as a UNIX timestamp. If None, use time.time().
            
        Returns:
            bool: True if the task has timed out, False otherwise.
        """
        if self.timeout is None:
            return False
        
        if current_time is None:
            current_time = time.time()
            
        return (current_time - self.created_at) > self.timeout
