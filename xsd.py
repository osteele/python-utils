""" Module xsd --- Model an XSD ("XML Schema Definition":http://www.w3.org/XML/Schema) """

__author__ = "Oliver Steele <steele@osteele.com>"
__copyright__ = "Copyright 1999-2001 by Oliver Steele."
__license__ = "Python License"
__version__ = 'alpha (prerelease)'

from __future__ import nested_scopes

#
# XML Model
#

class XMLObject:
    def __init__(self, name, attributes, children):
        self.tagName = name
        self.attributes = attributes
        self.children = children

    def __repr__(self):
        return str("<%s %s/>" % (self.tagName, ' '.join(["%s=\"%s\"" % (key, value) for (key, value) in self.attributes.items()])))

    def __getitem__(self, key):
        return self.attributes[key]

    def get(self, key, default=None):
        return self.attributes.get(key, default)

class XMLMaker:
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
        root.normalize()
        return self.makeNode(root)

    def parse(self, file):
        from xml.dom.minidom import parse
        doc = parse(file)
        return self.makeDocument(doc)

#
# XSD Model
#

class XSDElement(XMLObject):
    def setSchema(self, schema):
        self.schema = schema
        schema.register(self)
        map(lambda x:x.setSchema(schema), self.children)

    def collectChildren(self, type):
        return [c for c in self.children if c.__class__ == type]

class Annotation(XSDElement):
    pass

class Attribute(XSDElement):
    pass

class AttributeGroup(XSDElement):
    def getAttributes(self):
        if self.get('ref'):
            return self.schema.getEntity('attributeGroup', self['ref']).getAttributes()
        return self.collectChildren(Attribute)

class Choice(XSDElement):
    pass

class ComplexType(XSDElement):
    def _getAttributes(self):
        attrs = []
        for content in self.collectChildren(ComplexContent):
            [extension] = content.collectChildren(Extension)
            attrs += extension.collectChildren(Attribute)
            for group in extension.collectChildren(AttributeGroup):
                attrs += group.getAttributes()
            baseType = self.schema.getType(extension['base'])
            attrs += baseType.getAttributes()
        attrs += self.collectChildren(Attribute)
        for group in self.collectChildren(AttributeGroup):
            attrs += group.getAttributes()
        return attrs

    def getAttributes(self):
        if not hasattr(self, 'attrs'):
            self.attrs = self._getAttributes()
        return self.attrs

class ComplexContent(XSDElement):
    pass

class Documentation(XSDElement):
    pass

class Element(XSDElement):
    def getType(self):
        if self.get('type'):
            return self.schema.getType(self['type'])
        [type] = self.collectChildren(ComplexType)
        return type

    #def getSubstitutionGroup(self):

    def getAttributes(self):
        if self.collectChildren(ComplexType):
            return self.getType().getAttributes()
        else:
            return []
    
    def getAttribute(self, attrName):
        attrs = [a for a in self.getAttributes() if a['name'] == attrName]
        if not len(attrs):
            raise str("Attribute not found: %s.%s" % (self['name'], attrName))
        if len(attrs) > 1:
            raise str("Multiple attributes found: %s.%s" % (self['name'], attrName))
        return attrs[0]

    def hasAttribute(self, attrName):
        return [a for a in self.getAttributes() if a['name'] == attrName]

class Extension(XSDElement):
    pass

class MaxInclusive(XSDElement):
    pass

class MinInclusive(XSDElement):
    pass

class Restriction(XSDElement):
    pass

class Schema(XSDElement):
    def setup(self):
        self.elements = {}
        self.setSchema(self)

    def register(self, element):
        name = element.get('name')
        if name and element.tagName not in ("attribute",):
            table = self.elements
            key = (element.tagName, name)
            if table.get(key):
                raise "multiple definitions for <%s name=\"%s\"/>" % \
                      (str(element.tagName), str(name))
            table[key] = element
            table[(element.tagName, "agl:"+name)] = element

    def getEntity(self, elementName, tagName):
        key = (elementName, tagName)
        return self.elements[key]

    def getElement(self, tagName):
        key = ("element", tagName)
        return self.elements[key]

    def getType(self, name):
        return self.getEntity('complexType', name)

    def hasElement(self, tagName):
        key = ("element", tagName)
        return self.elements.get(key)

class Sequence(XSDElement):
    pass

class SimpleType(XSDElement):
    pass

class XSDMaker(XMLMaker):
    def makeElement(self, name, attributes, children):
        klass = globals().get(name[0].upper()+name[1:])
        from types import ClassType
        if not klass or type(klass) != ClassType or klass.__bases__[0] != XSDElement:
            raise "unknown element type: %r" % str(name)
        return klass(name, attributes, children)

    def makeTextNode(self, data):
        return None
    
    def makeDocument(self, doc):
        schema = XMLMaker.makeDocument(self, doc)
        schema.setup()
        return schema

def parse(fname):
    return XSDMaker().parse(fname)

def _test():
    import os
    schema = parse(os.path.expandvars("$ALPHAMASK/xml/aglxml.xsd"))
    #print schema.getElement("radialGradient").getAttributes()
    keys = [x for (n, x) in schema.elements.keys()
            if n == 'element' and not x.startswith('agl:')]
    keys.sort()
    for e in [schema.getElement(key) for key in keys]:
        print e['name']
        attributes = [a['name'] for a in e.getAttributes()]
        attributes.sort()
        if attributes:
            print ' ', ', '.join(attributes)

#_test()
