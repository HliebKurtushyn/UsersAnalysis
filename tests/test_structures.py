from web_app.structures import Queue, Stack


def test_queue_is_fifo():
    queue = Queue()
    queue.enqueue("first")
    queue.enqueue("second")
    assert queue.dequeue() == "first"


def test_stack_is_lifo():
    stack = Stack()
    stack.push("first")
    stack.push("second")
    assert stack.pop() == "second"
