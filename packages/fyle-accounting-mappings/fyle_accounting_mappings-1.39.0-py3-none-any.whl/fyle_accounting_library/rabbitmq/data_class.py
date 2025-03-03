from dataclasses import dataclass

@dataclass
class RabbitMQData:
    table_name: str = None
    old: dict = {}
    new: dict = {}
    id: str = None
    action: str = None
    diff: dict = {}
