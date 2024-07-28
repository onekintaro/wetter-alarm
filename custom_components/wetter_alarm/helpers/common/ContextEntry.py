from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ContextEntry:
    title: str
    data: Dict[str, Any]
    options: Dict[str, Any]
    context_entry: Dict[str, str] = field(default_factory=dict)