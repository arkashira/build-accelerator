from compiler import compile_code, compile_codebase
import pytest

def test_compile_code():
    code = "console.log('Hello World');"
    result = compile_code(code)
    assert result.compilation_time < 1
    assert result.output == '{"compiled": true}'

def test_compile_codebase_small():
    codebase = ["console.log('Hello World');", "console.log('Hello World again');"]
    result = compile_codebase(codebase)
    assert result.compilation_time < 1
    assert result.output == '{"compiled": true}'

def test_compile_codebase_large():
    codebase = ["console.log('Hello World');"] * 1000
    result = compile_codebase(codebase)
    assert result.compilation_time < 5
    assert result.output == '{"compiled": true}'

def test_compile_code_empty():
    code = ""
    result = compile_code(code)
    assert result.compilation_time < 1
    assert result.output == '{"compiled": true}'

def test_compile_codebase_empty():
    codebase = []
    result = compile_codebase(codebase)
    assert result.compilation_time < 1
    assert result.output == '{"compiled": true}'
