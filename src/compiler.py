import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class CompilationResult:
    success: bool
    message: str

class Compiler:
    def __init__(self, free_tier_limit: int = 1000):
        self.free_tier_limit = free_tier_limit

    def compile(self, codebase_size: int) -> CompilationResult:
        if codebase_size <= self.free_tier_limit:
            return CompilationResult(True, "Compilation successful")
        else:
            return CompilationResult(False, "Codebase size exceeds free tier limit")

    def signup(self, email: str) -> bool:
        # In a real implementation, this would involve storing the email in a database
        # For the purpose of this example, we'll just return True
        return True

    def upgrade(self, email: str) -> bool:
        # In a real implementation, this would involve checking the user's subscription status
        # For the purpose of this example, we'll just return True
        return True
