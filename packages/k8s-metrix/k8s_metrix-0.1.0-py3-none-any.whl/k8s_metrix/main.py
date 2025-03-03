from pydantic import BaseModel

class K8sMetrix:
    def __init__(self, backend: str):
        self.backend = backend
    
    def expose_metrics():
        pass