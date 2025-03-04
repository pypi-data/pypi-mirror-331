import heapq
from typing import Optional, List, Dict, Tuple, Any

class CausalPriorityQueue:
    """
    A dynamically adjusting priority queue where priorities change based on causal influences.
    
    Features:
    - Supports standard priority queue operations (add, pop, remove).
    - Allows tasks to influence the priority of other tasks.
    - Efficiently updates influenced task priorities using a heap-based structure.
    """
    def __init__(self):
        """Initialize an empty Causal Priority Queue."""
        self.heap: List[List[Any]] = []  # Standard priority queue (Min-Heap)
        self.entry_finder: Dict[Any, List[Any]] = {}  # Mapping of elements to priority entries
        self.counter: int = 0  # Unique sequence count to break ties
        self.influence_graph: Dict[Any, Dict[Any, int]] = {}  # Graph storing causal relationships

    def add_task(self, task: Any, priority: int = 0, influences: Optional[List[Any]] = None, influence_weight: int = 1) -> None:
        """
        Adds a task to the priority queue.
        
        :param task: The task identifier.
        :param priority: The initial priority of the task.
        :param influences: Optional list of tasks that this task influences.
        :param influence_weight: The amount by which influenced tasks' priority will be adjusted.
        """
        if task in self.entry_finder:
            self.remove_task(task)
        entry = [priority, self.counter, task]
        self.entry_finder[task] = entry
        heapq.heappush(self.heap, entry)
        self.counter += 1
        
        if influences:
            self.influence_graph[task] = {influenced_task: influence_weight for influenced_task in influences}

    def remove_task(self, task: Any) -> None:
        """
        Removes a task from the priority queue.
        
        :param task: The task to remove.
        """
        entry = self.entry_finder.pop(task, None)
        if entry:
            entry[-1] = None  # Invalidate entry

    def pop_task(self) -> Tuple[Any, int]:
        """
        Removes and returns the task with the lowest priority.
        
        :return: Tuple of (task, priority)
        :raises KeyError: If the queue is empty.
        """
        while self.heap:
            priority, _, task = heapq.heappop(self.heap)
            if task is not None:
                del self.entry_finder[task]
                self._adjust_priorities(task)
                return task, priority
        raise KeyError("pop from an empty priority queue")
    
    def _adjust_priorities(self, removed_task: Any) -> None:
        """
        Adjusts priorities of tasks influenced by the removed task.
        
        :param removed_task: The task being removed, which influences others.
        """
        if removed_task in self.influence_graph:
            for influenced_task, weight in self.influence_graph[removed_task].items():
                if influenced_task in self.entry_finder:
                    # Modify priority in-place instead of reinserting
                    entry = self.entry_finder[influenced_task]
                    new_priority = max(entry[0] - weight, 0)  # Prevent negative priority
                    entry[0] = new_priority
                    heapq.heappush(self.heap, entry)  # Efficient reordering

    def get_tasks(self) -> List[Tuple[Any, int]]:
        """
        Returns a list of all tasks sorted by priority.
        
        :return: List of tuples (task, priority) in priority order.
        """
        return sorted(
            [(entry[2], entry[0]) for entry in self.heap if entry[2] is not None],
            key=lambda x: x[1]
        )
    
    def bulk_add_tasks(self, tasks: List[Tuple[Any, int, Optional[List[Any]], int]]) -> None:
        """
        Adds multiple tasks at once, optimizing heap operations.
        
        :param tasks: List of tuples (task, priority, influences, influence_weight).
        """
        for task, priority, influences, weight in tasks:
            self.add_task(task, priority, influences, weight)
    
    def clear_queue(self) -> None:
        """
        Completely resets the queue, removing all tasks.
        """
        self.heap.clear()
        self.entry_finder.clear()
        self.influence_graph.clear()
        self.counter = 0
