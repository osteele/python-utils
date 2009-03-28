import symbol, token
IMPORT_STMT_WITH_LIST_PATTERN =(
    symbol.stmt,
    (symbol.simple_stmt,
     (symbol.small_stmt,
      ['import_stmt']
      ),
     (token.NEWLINE, '')
     )
    )

def findModuleFile(mname):
    import sys, os
    for path in sys.path:
        fname = os.path.join(path, mname.split('.'))
        if os.path.isfile(fname): return fname
    return None

def getImports(mname):
    fname = findModuleFile(mname)
    if not fname: return []
    import parser
    ast = parser.suite(open(source).read())
    tup = ast.2tuple()
    from HappyDoc.parseinfo import match
    match(IMPORT_PATTERN, tup)

def graphModuleImports(mname):
    graph = Graph()
    visited = {}
    def visit(mname, graph=graph, visited=visited):
        id = visited.get(mname)
        if id: return id
        id = visited[mname] = graph.makeNextId()
        for cm in getImports(mname):
            cf = findModuleFile(cm)
            cid = visit(cf)
            graph.addEdge(id, cid)
        return id
    visit(mname)
    graph.write('imports.jpeg', 'jpeg')

graphModuleImports('graphviz')

if __name__ == '__main__':
    pass
