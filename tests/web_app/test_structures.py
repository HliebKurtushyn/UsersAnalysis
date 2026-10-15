from web_app.structures import Queue, Stack


def test_queue_is_fifo():
    queue = Queue()
    queue.enqueue("first")
    queue.enqueue("second")
    assert queue.dequeue() == "first"


def test_queue_can_be_reused_after_dequeue():
    queue = Queue()
    queue.enqueue("first")
    assert queue.dequeue() == "first"

    queue.enqueue("second")

    assert queue.dequeue() == "second"
    assert queue.dequeue() is None


def test_stack_is_lifo():
    stack = Stack()
    stack.push("first")
    stack.push("second")
    assert stack.pop() == "second"


def test_stack_can_be_reused_after_pop():
    stack = Stack()
    stack.push("first")
    assert stack.pop() == "first"

    stack.push("second")

    assert stack.pop() == "second"
    assert stack.pop() is None
