from functools import wraps

def manage_generation_state(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            with self.state.lock:
                self.state.is_generating = True
                self.state.last_complete_sentence = ""
                self.state.current_buffer = ""

            func(self, *args, **kwargs)

        except Exception as e:
            self.logger.error(f"Error during generation: {e}")
            raise e
        finally:
            with self.state.lock:
                self.state.is_generating = False
            self.logger.info("Generation complete")
    return wrapper

def timer_decorator(func):
    """
    Decorator to measure the execution time of a function.
    Usage:
    @timer_decorator
    def my_function():
        # code to execute
    """
    from time import time
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(f"\n{func.__name__} took {end_time - start_time:.2f} seconds to execute\n")
        return result
    return wrapper