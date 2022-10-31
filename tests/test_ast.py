from gdtoolkit.parser import parser
from gdtoolkit.common.ast import AbstractSyntaxTree


def test_toplevel():
    code = """func foo():
    pass
    """
    parse_tree = parser.parse(code, gather_metadata=True)
    ast = AbstractSyntaxTree(parse_tree)
    assert len(ast.all_functions) == 1
    function = ast.all_functions[0]
    assert function.name == "foo"
    assert len(function.all_sub_statements) == 1


def test_all_sub_statements_of_function():
    code = """func foo():
    pass
    if true:
        pass
        if true:
            return
        elif true:
            return
        else:
            return
    while true:
        if true:
            return
    for f in range(10):
        if true:
            return
    var x
    match(x):
        1:
            pass
    """
    parse_tree = parser.parse(code, gather_metadata=True)
    ast = AbstractSyntaxTree(parse_tree)
    assert len(ast.all_functions) == 1
    function = ast.all_functions[0]
    assert len(function.all_sub_statements) == 16
    assert function.all_sub_statements[0].kind == 'pass_stmt'
    assert function.all_sub_statements[1].kind == 'if_stmt'
    assert function.all_sub_statements[2].kind == 'pass_stmt'
    assert function.all_sub_statements[3].kind == 'if_stmt'
    assert function.all_sub_statements[4].kind == 'return_stmt'
    assert function.all_sub_statements[5].kind == 'return_stmt'
    assert function.all_sub_statements[6].kind == 'return_stmt'
    assert function.all_sub_statements[7].kind == 'while_stmt'
    assert function.all_sub_statements[8].kind == 'if_stmt'
    assert function.all_sub_statements[9].kind == 'return_stmt'
    assert function.all_sub_statements[10].kind == 'for_stmt'
    assert function.all_sub_statements[11].kind == 'if_stmt'
    assert function.all_sub_statements[12].kind == 'return_stmt'
    assert function.all_sub_statements[13].kind == 'func_var_stmt'
    assert function.all_sub_statements[14].kind == 'match_stmt'
    assert function.all_sub_statements[15].kind == 'pass_stmt'
