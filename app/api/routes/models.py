from pydantic import BaseModel, Field

class LoginCredentials(BaseModel):
    username: str
    password: str
    
class CreateFolderPayload(BaseModel):
    path: str
    folder_name: str

class LoadAverage(BaseModel):
    min1: float
    min5: float
    min15: float

class SystemMetrics(BaseModel):
    timestamp: int
    hostname: str
    version: str
    cpu_model: str
    cpu_utilization_percent: float
    memory_utilization_percent: float
    load_average: LoadAverage
    uptime_seconds: float
    available_package_updates: int