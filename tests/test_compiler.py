from compiler import Compiler, CompilationResult

def test_compile_free_tier():
    compiler = Compiler()
    result = compiler.compile(500)
    assert result.success
    assert result.message == "Compilation successful"

def test_compile_paid_tier():
    compiler = Compiler()
    result = compiler.compile(1500)
    assert not result.success
    assert result.message == "Codebase size exceeds free tier limit"

def test_signup():
    compiler = Compiler()
    assert compiler.signup("test@example.com")

def test_upgrade():
    compiler = Compiler()
    assert compiler.upgrade("test@example.com")
