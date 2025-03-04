from .utils import helper_function

class MyClass:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        """Return a greeting message"""
        return f"Hello, {self.name}!"
    
    def process_data(self, data):
        """Process data using helper function"""
        return helper_function(data)