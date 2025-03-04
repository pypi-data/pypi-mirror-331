# Causal Priority Queue (CPQ)

## Overview
**Causal Priority Queue (CPQ)** is a dynamically adjusting priority queue where:
- Priorities are **not static** but dynamically change based on causal influences.
- Items in the queue **influence each other** based on relationships.
- Designed for **AI scheduling, intelligent load balancing, and real-time prioritization.**

## How It Works
Unlike traditional priority queues where elements have fixed priorities, CPQ:
1. Stores **influences as a graph** where tasks affect each other.
2. Adjusts priorities **dynamically** when tasks are processed.
3. Ensures **efficient priority updates** using a **heap-based structure**.

## Installation
You can install CPQ by cloning the repository:

```bash
git clone https://github.com/mukerjeejoy-github/causal-priority-queue.git
cd CausalPriorityQueue
```

## Usage Example
```python
from causal_priority_queue.cpq import CausalPriorityQueue

cpq = CausalPriorityQueue()
cpq.add_task("Task A", priority=3, influences=["Task B"], influence_weight=2)
cpq.add_task("Task B", priority=5)
cpq.add_task("Task C", priority=8)

print("Before popping:", cpq.get_tasks())
print("Popped:", cpq.pop_task())
print("After popping:", cpq.get_tasks())
```

## 🔍 Benchmarks
| Data Structure                  | Time Taken (10,000 tasks) |
| ------------------------------- | ------------------------- |
| Causal Priority Queue (CPQ)     | 0.019 sec                 |
| Standard Priority Queue (heapq) | 0.009 sec                 |
| SortedDict Priority Queue       | 0.006 sec                 |

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch.
3. Commit changes and create a pull request.

## 📜 License
This project is licensed under the **MIT License**. See `LICENSE` for details.

