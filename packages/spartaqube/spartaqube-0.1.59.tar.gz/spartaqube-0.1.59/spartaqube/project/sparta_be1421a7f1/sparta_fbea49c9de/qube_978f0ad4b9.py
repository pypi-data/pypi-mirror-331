import ast
def sparta_6a99b77b6d(code):
	B=ast.parse(code);A=set()
	class C(ast.NodeVisitor):
		def visit_Name(B,node):A.add(node.id);B.generic_visit(node)
	D=C();D.visit(B);return list(A)
def sparta_d7a790725c(script_text):return sparta_6a99b77b6d(script_text)