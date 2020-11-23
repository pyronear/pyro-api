
from typing import Any
def __getattr__(name: Any) -> Any: ...
# Caught error in pytype: 
# Traceback (most recent call last):
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/io.py", line 151, in check_or_generate_pyi
#     errorlog, result, ast = generate_pyi(
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/io.py", line 110, in generate_pyi
#     errorlog, (mod, builtins) = _call(analyze.infer_types, src, options, loader)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/io.py", line 64, in wrapper
#     return f(*args, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/io.py", line 76, in _call
#     return errorlog, analyze_types(
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/analyze.py", line 678, in infer_types
#     loc, defs = tracer.run_program(src, filename, init_maximum_depth)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/vm.py", line 828, in run_program
#     node, f_globals, f_locals, _ = self.run_bytecode(node, code)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/vm.py", line 795, in run_bytecode
#     node, return_var = self.run_frame(frame, node)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/vm.py", line 331, in run_frame
#     state = self.run_instruction(op, state)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/vm.py", line 287, in run_instruction
#     state = bytecode_fn(state, op)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/vm.py", line 2974, in byte_IMPORT_NAME
#     module = self.import_module(name, full_name, level)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/vm.py", line 1552, in import_module
#     module = self._import_module(name, level)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/utils.py", line 302, in call
#     result = f(*posargs, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/vm.py", line 1602, in _import_module
#     ast = self.loader.import_name(base.name + "." + name)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/load_pytd.py", line 441, in import_name
#     ast = self._import_name(module_name)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/load_pytd.py", line 517, in _import_name
#     file_ast, path = self._import_file(module_name, module_name.split("."))
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/load_pytd.py", line 584, in _import_file
#     file_ast, full_path = self._load_pyi(path, module_name)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/load_pytd.py", line 611, in _load_pyi
#     ast = self.load_file(filename=full_path, module_name=module_name)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/load_pytd.py", line 250, in load_file
#     return self._process_module(module_name, filename, ast)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/load_pytd.py", line 268, in _process_module
#     module.ast = self._resolve_builtins(module.ast)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/load_pytd.py", line 207, in _resolve_builtins
#     pyval = pyval.Visit(visitors.ExpandCompatibleBuiltins(self.builtins))
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/parse/node.py", line 197, in Visit
#     return _Visit(self, visitor, *args, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/parse/node.py", line 225, in _Visit
#     return _VisitNode(node, visitor, *args, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/parse/node.py", line 309, in _VisitNode
#     new_child = _VisitNode(child, visitor, *args, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/parse/node.py", line 276, in _VisitNode
#     new_child = _VisitNode(child, visitor, *args, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/parse/node.py", line 309, in _VisitNode
#     new_child = _VisitNode(child, visitor, *args, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/parse/node.py", line 298, in _VisitNode
#     status = visitor.Enter(node, *args, **kwargs)
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/pytd_visitors.py", line 163, in Enter
#     return self.enter_functions[node.__class__.__name__](
#   File "/Users/jean/Documents/Perso/PyroNear/pyronear-api/.venv/lib/python3.8/site-packages/pytype/pytd/visitors.py", line 1652, in EnterTypeParameter
#     assert not self.in_type_parameter
# AssertionError