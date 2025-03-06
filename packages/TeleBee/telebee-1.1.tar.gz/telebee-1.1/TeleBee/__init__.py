import importlib, os

class TeleBee:
    def __init__(self, function_dirs=None):
        self.function_dirs = function_dirs if function_dirs else [os.getcwd()]

    def load_functions(self):
        for function_dir in self.function_dirs:
            if os.path.isdir(function_dir):
                for filename in os.listdir(function_dir):
                    if filename.endswith(".py") and filename != os.path.basename(__file__):
                        module_name = filename[:-3]
                        module_path = f"{function_dir.replace('/', '.')}.{module_name}"
                        self._load_function(module_path)

    def _load_function(self, module_path):
        try:
            importlib.import_module(module_path)
        except Exception as e:
            print(f"Error loading module {module_path}: {e}")