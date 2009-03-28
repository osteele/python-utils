"""An OO interface to the "GraphViz":http://www.research.att.com/sw/tools/graphviz/ open source graph drawing software.
"""

__author__ = "Oliver Steele <steele@osteele.com>"
__copyright__ = "Copyright 1999-2001 by Oliver Steele."
__license__ = "Python License"
__version__ = '1.0a2'

class Graph:
    def __init__(self, name='graph'):
        assert ' ' not in name
        self.name = name
        self.nodes = []
        self.nodeMap = {}
        self.edgeMap = {}
        self.nextId = 0

    def makeNextId(self, prefix='g'):
        self.nextId += 1
        return prefix + str(self.nextId)

    def addNode(self, name, **attrs):
        self.nodeMap.setdefault(name, {}).update(attrs)
        if name not in self.nodes:
            self.nodes.append(name)

    def addEdge(self, source, target, **attrs):
        self.addNode(source)
        self.addNode(target)
        self.edgeMap.setdefault((source, target), {}).update(attrs)

    def asSource(self):
        """Returns a string that can be printed by the DOT tool at
        http://www.research.att.com/sw/tools/graphviz/ ."""
        import string
        output = []
        output.append('digraph %s {' % self.name);
        def attrString(attrs):
            if attrs:
                def a(k, v):
                    if k in ['URL', 'label']:
                        return '"%s"' % v
                    else:
                        return str(v)
                return ' [' + ', '.join(['%s=%s' % (k, a(k, v)) for k, v in attrs.items()]) + ']'
            return ''
        def ql(s): return '\"' + s + '\"'
        ranks = {}
        for name in self.nodes:
            attrs = {}
            attrs.update(self.nodeMap[name])
            if attrs.has_key('rank'):
                import sys
                ranks.setdefault(attrs['rank'], []).append(name)
                del attrs['rank']
            output.append('\t%s%s;' % (ql(name), attrString(attrs)))
        keys = ranks.keys()
        keys.sort()
        for rank in keys:
            nodes = ranks[rank]
            output.append('\t{rank=same; ' + ''.join(['%s; ' % ql(name) for name in nodes]) + '};')
        for (s0, s1), attrs in self.edgeMap.items():
            output.append('\t%s -> %s%s;' % (ql(s0), ql(s1), attrString(attrs)))
        output.append('}');
        return string.join(output, '\n')

    def write(self, fname, format):
        # format in text, ps, hpgl, pcl, ..., gif, jpeg, png, ismap, imap, svg, plain
        if format == 'dot':
            open(fname, 'w').write(self.asSource())
            return
        import os, tempfile
        dotter = 'dot'
        str = self.asSource()
        dotfile = tempfile.mktemp()
        try:
            open(dotfile, 'w').write(str)
            expr = ("%s -T%s %s -o \"%s\"" % (dotter, format, dotfile, fname))
            os.system(expr)
        finally:
            try: os.remove(dotfile)
            except: pass

    def as(self, format):
        if format == 'dot':
            return self.asSource()
        import tempfile
        fname = tempfile.mktemp()
        #fname = 'c:/documents and settings/steele/my documents/temp.out'
        self.write(fname, format)
        try:
            self.write(fname, format)
            return open(fname, 'rb').read()
        finally:
            try: os.remove(fname)
            except: pass

def _test():
    graph = Graph('my_graph')
    graph.addNode('Zeus', URL="zeus", shape='box', style='filled', rank=1)
    graph.addNode('Hera', URL="hera", rank=1)
    graph.addNode('Zeus+Hera', rank=1, shape='none')
    graph.addNode('Heracles', shape="box", rank=2)
    graph.addEdge('Zeus', 'Zeus+Hera', dir='none')
    graph.addEdge('Zeus+Hera', 'Hera', dir='none')
    graph.addEdge('Zeus+Hera', 'Heracles')
    #graph.addEdge('Zeus', 'Hera', label='wife', dir='none')
    #graph.addEdge('Zeus', 'Heracles', label='children')
    print graph.asSource()
    import os
    #graph.write(os.path.join(os.path.split(__file__)[0], 'zeus.dot'), 'dot')
    graph.write(os.path.join(os.path.split(__file__)[0], 'zeus.jpeg'), 'jpeg')

#_test()
