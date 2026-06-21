import json
import time
from dataclasses import dataclass
from typing import List

@dataclass
class CompilationResult:
    compilation_time: float
    output: str

def compile_code(code: str) -> CompilationResult:
    start_time = time.time()
    # Simulate compilation process
    output = json.dumps({"compiled": True})
    end_time = time.time()
    compilation_time = end_time - start_time
    return CompilationResult(compilation_time, output)

def compile_codebase(codebase: List[str]) -> CompilationResult:
    start_time = time.time()
    # Simulate compilation process
    output = json.dumps({"compiled": True})
    end_time = time.time()
    compilation_time = end_time - start_time
    return CompilationResult(compilation_time, output)
