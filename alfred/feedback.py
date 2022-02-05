# -*- coding: utf-8 -*-
from xml.etree import ElementTree
import xml.sax.saxutils as saxutils
import copy, random
from . import core

class Item(object):
    def __init__(self, **kwargs):
        self.content = {
            'title'     : kwargs.get('title', ''),
            'subtitle'  : kwargs.get('subtitle', ''),
            'icon'      : kwargs.get('icon', 'icon.png')
        }

        it = kwargs.get('icontype', '').lower()
        self.icon_type = it if it in ['fileicon', 'filetype'] else None

        valid = kwargs.get('valid', None)
        if isinstance(valid, str) and valid.lower() == 'no':
            valid = 'no'
        elif isinstance(valid, bool) and not valid:
            valid = 'no'
        else:
            valid = None

        self.attrb = {
            'uid'           : kwargs.get('uid', '{0}.{1}'.format(core.bundleID(), random.getrandbits(40))),
            'arg'           : kwargs.get('arg', None),
            'valid'         : valid,
            'autocomplete'  : kwargs.get('autocomplete', None),
            'type'          : kwargs.get('type', None)
        }

        for k, v in copy.copy(self.content).items():
            if not v:
                self.content.pop(k)

        for k, v in copy.copy(self.attrb).items():
            if not v:
                self.attrb.pop(k)

    def copy(self):
        return copy.copy(self)

    def getXMLElement(self):
        item = ElementTree.Element('item', self.attrb)
        for (k, v) in self.content.items():
            attrb = {}
            if k == 'icon' and self.icon_type:
                attrb['type'] = self.icon_type
            sub = ElementTree.SubElement(item, k, attrb)
            sub.text = v
        return item

class Feedback(object):
    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)
        
    def addItem(self, **kwargs):
        item = kwargs.pop('item', None)
        if not isinstance(item, Item):
            item = Item(**kwargs)
        self.items.append(item)

    def clean(self):
        self.items = []

    def isEmpty(self):
        return not bool(self.items)

    def get(self, unescape = False):
        ele_tree = ElementTree.Element('items')
        for item in self.items:
            ele_tree.append(item.getXMLElement())
        res = ElementTree.tostring(ele_tree, encoding='unicode')
        if unescape:
            return saxutils.unescape(res)
        return res

    def output(self):
        print(self.get())