__author__ = "Oliver Steele <steele@cs.brandeis.edu>"
__copyright__ = "Copyright 2001 by Oliver Steele.  All rights reserved."
__version__ = 'alpha (prerelease)'

#
# XML Model
#

class XMLObject:
    def __init__(self, name, attributes, children):
        self.tagName = name
        self.attributes = attributes
        self.children = children

    def __repr__(self):
        attrs = ''.join([" %s=\"%s\"" % (key, value) for (key, value) in self.attributes.items()])
        if self.children:
            from cStringIO import StringIO
            buffer = StringIO()
            buffer.write(str("<%s%s>" % (self.tagName, attrs)))
            for child in self.children:
                buffer.write(str(child))
            buffer.write(str("</%s>" % self.tagName))
            return buffer.getvalue()
        else:
            return str("<%s%s/>" % (self.tagName, attrs))

    def __getitem__(self, key):
        return self.attributes[key]

    def get(self, key, default=None):
        return self.attributes.get(key, default)

class XMLObjectFactory:
    def makeElement(self, name, attributes, children):
        return XMLObject(name, attributes, children)

    def makeTextNode(self, data):
        return data
    
    def makeNode(self, node):
        if node.nodeType == node.ELEMENT_NODE:
            element = node
            attributes = {}
            for key in element.attributes.keys():
                attributes[key] = element.attributes[key].value
            children = filter(None, map(self.makeNode, element.childNodes))
            return self.makeElement(element.nodeName, attributes, children)
        elif node.nodeType == node.TEXT_NODE:
            return self.makeTextNode(node.data)
        elif node.nodeType in (node.PROCESSING_INSTRUCTION_NODE,):
            return None
        raise 'unknown node type %r %r' % (node, node.nodeType)

    def makeDocument(self, doc):
        root = doc.documentElement
        return self.makeNode(root)

    def parseFile(self, file):
        from xml.dom.minidom import parse
        doc = parse(file)
        return self.makeDocument(doc)
 
