import unittest
from causal_priority_queue.cpq import CausalPriorityQueue

class TestCausalPriorityQueue(unittest.TestCase):
    def setUp(self):
        self.cpq = CausalPriorityQueue()
    
    def test_basic_operations(self):
        self.cpq.add_task("A", priority=5)
        self.cpq.add_task("B", priority=2)
        self.cpq.add_task("C", priority=7)
        self.assertEqual(self.cpq.pop_task()[0], "B")  # Lowest priority first
    
    def test_influence_effect(self):
        self.cpq.add_task("A", priority=3, influences=["B"], influence_weight=2)
        self.cpq.add_task("B", priority=5)
        self.cpq.pop_task()
        self.assertEqual(self.cpq.pop_task()[1], 3)  # Priority adjusted due to influence

    def test_bulk_addition(self):
        tasks = [("A", 1, None, 1), ("B", 2, ["C"], 1), ("C", 5, None, 1)]
        self.cpq.bulk_add_tasks(tasks)
        self.assertEqual(self.cpq.pop_task()[0], "A")

    def test_clear_queue(self):
        self.cpq.add_task("A", priority=1)
        self.cpq.clear_queue()
        with self.assertRaises(KeyError):
            self.cpq.pop_task()

if __name__ == '__main__':
    unittest.main()
