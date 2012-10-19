# -* coding: utf-8 -*-

#Author: bibi21000
#Licence : GPL

from select import select
import sys
import os
import urwid
from urwid.raw_display import Screen
#import headerpanel
#import dirpanel
#import setuppanel
from traceback import format_exc
#from ucp import UrwidCmdProc, isUCP
#from utils import utilInit, log
sys.path.insert(0, os.path.abspath('../build/tmp/usr/local/lib/python2.6/dist-packages'))
sys.path.insert(0, os.path.abspath('../build/tmp/usr/local/lib/python2.7/dist-packages'))
sys.path.insert(0, os.path.abspath('build/tmp/usr/local/lib/python2.6/dist-packages'))
sys.path.insert(0, os.path.abspath('build/tmp/usr/local/lib/python2.7/dist-packages'))
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from louie import dispatcher, All
import logging
#from frameapp import FrameApp, DIVIDER

#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)

#logger = logging.getLogger('openzwave')

class OldestTree(urwid.ListWalker):

    def __init__(self, window, parent=None, widget_box=None):
        self.window = window
        self.parent = parent
        self.widget_box = widget_box
        self.usage = ['ls : list directory', 'cd <directory> : change to directory <directory>' ]
        self.childrens = {}
        self.subdirs = []
        self.definition = None
        self.key = None
        self.lines = []
        self.focus, oldfocus = (0, 0)
        self.size = 0

    def add_child(self, child, definition):
        self.window.log.info("Add a child")
        self.subdirs.append(child)
        self.childrens[child] = definition

    def _get_at_pos(self, pos):
        if pos >= 0 and pos < self.size and len(self.lines)>0:
            return self.lines[pos], pos
        else:
            return None, None

    def get_nodeid(self):
        return self.get_id()

    def get_id(self):
        line,pos = self._get_at_pos(self.focus)
        return line.id

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def get_focus_entry(self):
        return self.lines[self.focus]

    def set_focus(self, focus):
        if self.focus != focus:
            self.focus = focus
            #self.parent.update_node(self.get_nodeid())
            self._modified()

    def get_next(self, pos):
        return self._get_at_pos(pos + 1)

    def get_prev(self, pos):
        return self._get_at_pos(pos - 1)

    def go_first(self):
        self.set_focus(0)

    def go_last(self):
        self.set_focus(self.size - 1)

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []

    def show_directories(self):
        for child in self.subdirs:
            self.lines.append( \
                RootDir(self.childrens[child]['id'], \
                    self.childrens[child]['name'], \
                    self.childrens[child]['help']))
            self.size += 1
        self.lines.append(urwid.Divider("-"))
        self.size += 1

    def show_help(self):
        self.lines.append(urwid.Divider("-"))
        self.size += 1
        self.lines.append(urwid.Text("Help" , align='left'))
        self.size += 1
        for use in self.usage:
            self.lines.append( \
                urwid.Text("%s" % use, align='left'))
            self.size += 1
        self._modified()

    def refresh(self):
        self.read_lines()
        self.show_help()
        self._modified()

    def get_selected(self):
        ret = []
        for x in self.lines:
            if x.selected == True:
                ret.append(x)
        return ret

    def exist(self, directory):
        """
        Check that the directory exists
        """
        #self.window.log.info("OldestTree exist %s" %self.childrens)
        if directory == "..":
            return self.parent != None
        if directory in self.subdirs:
            #self.window.log.info("OldestTree exist %s" %directory)
            return True
        #for line in self.lines :
        #    if line.id and line.id == directory:
        #        return True
        return False

    def ls(self, opts):
        """
        List directory content
        """
        self.refresh()

    def cd(self, directory):
        """
        Change to directory and return the widget to display
        """
        if self.exist(directory) :
            if directory == '..':
                return self.parent.widget_box
            else :
                return self.childrens[directory]['widget_box']
        return None

    def fullpath(self):
        """
        Path to this directory
        """
        if self.parent == None:
            return "%s/" % (self.path)
        else:
            return "%s%s/" % (self.parent.fullpath(), self.path)

    @property
    def path(self):
        """
        The path

        :rtype: str

        """
        return self._path

    @path.setter
    def path(self,value):
        """
        Path

        :rtype: str

        """
        self._path = value

    def set(self, param, value):
        return False

    def add(self, param, value):
        return False

    def remove(self, param, value):
        return False

    def create(self, value):
        return False

    def delete(self, value):
        return False

    def activate(self, value):
        return False

class GroupsBox(urwid.ListBox):
    """
    GroupsBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = GroupsTree(window, parent.walker, self)
        self.__super.__init__(self.walker)

class GroupsTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
    #    self.window = window
    #    self._framefocus = framefocus
    #    self.read_nodes(None)
        self.subdirs = ['..']
        self.childrens = { '..' : {'id':'..',
                                    'name':'..',
                                    'help':'Go to previous directory',
                                    'widget_box' : None},
                }
        self._path = "groups"
        self.node_id = None
        #self.key = 'Groups'
        self.groups_header = AssociationItem()
        self.definition = {'id':'groups',
                                'name':'groups',
                                'help':'Groups/Associations management',
                                'widget_box': self.widget_box
        }
        if parent != None :
            parent.add_child('groups', self.definition)
        self.usage.append("add <nodeid> to <groupindex> : add node <nodeid> to group of index <groupindex>")
        self.usage.append("remove <nodeid> from <groupindex> : remove node <nodeid> from group of index <groupindex>")
        #self.usage.append("set <label> to <data> : change value <label> to data")
        dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.window.log.info("GroupsTree _louie_network_ready")
        self.refresh()
        dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_GROUP)
        self.window.log.info("GroupsTree _louie_network_ready")

    def _louie_node_update(self, network, node):
        self.window.log.info("GroupsTree _louie_node_update")
        self.refresh()
        self.window.log.info("GroupsTree _louie_node_update")

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        if self.window.network == None or self.node_id == None:
            return
        self.show_directories()
        self.lines.append(self.groups_header.get_header())
        self.size += 1
        groups = self.window.network.nodes[self.node_id].groups
        self.window.log.info("GroupsTree groups=%s" % groups)
        for group in groups :
            self.window.log.info("GroupsTree group=%s" % group)
            self.lines.append(urwid.Text(    "      %s:%s" % (groups[group].index,groups[group].label), align='left'))
            self.size += 1
            for assoc in groups[group].associations:
                self.lines.append(AssociationItem(assoc, \
                    self.window.network.nodes[assoc].name
                    ))
                self.size += 1
        self._modified()

    def exist(self, directory):
        """
        List directory content
        """
        if OldestTree.exist(self, directory):
            return True
        return False

    def cd(self, directory):
        """
        Change to directory and return the widget to display
        """
        if self.exist(directory) :
            if directory == '..':
                return self.parent.widget_box
            if directory in self.childrens:
                self.window.log.info("cd %s" %directory)
                return self.childrens[directory]['widget_box']
        return None

    def add(self, param, value):
        try:
            param = int(param)
            value = int(value)
        except:
            self.window.status_bar.update(status="Invalid index or node ID %s/%s" % (param, value))
            return False
        if param in self.window.network.nodes[self.node_id].groups:
            self.window.network.nodes[self.node_id].groups[param].add_association(value)
            self.window.status_bar.update(status='Group %s updated' % param)
            return True
        else :
            self.window.network.nodes[self.node_id].add_group(value)
            self.window.status_bar.update(status='Group %s added' % param)
            return True

    def remove(self, param, value):
        try:
            param = int(param)
            value = int(value)
        except:
            self.window.status_bar.update(status="Invalid index or node ID %s/%s" % (param, value))
            return False
        if param in self.window.network.nodes[self.node_id].groups:
            if value in self.window.network.nodes[self.node_id].groups[param] :
                self.window.network.nodes[self.node_id].groups[param].remove_association(value)
                self.window.status_bar.update(status='Group %s updated' % param)
                return True
            else :
                self.window.status_bar.update(status="Can't find node %s in group %s" % (value,param))
                return False
        else :
            self.window.status_bar.update(status="Can't find group %s" % (param))
            return False

class AssociationItem (urwid.WidgetWrap):

    def __init__ (self, id=0, name=None):
        self.id = id
        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % id, wrap='space'), 'body', 'focus'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % name, wrap='space'), 'body'),
        ]
        w = urwid.Columns(self.item, dividechars=1 )
        self.__super.__init__(w)

    def get_header (self):
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % "NodeId", wrap='clip'), 'node_header'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % "Name", wrap='clip'), 'node_header'),
        ]
        return urwid.Columns(self.item, dividechars=1)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class RootTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
    #    self._framefocus = framefocus
        self.childrens = { 'controller' : {'id':'ctl',
                                        'name':'Controller',
                                        'help':'Controller management',
                                        'widget_box' : None},
                'scenes' : {'id':'scn',
                            'name':'Scenes',
                            'help':'scenes management',
                            'widget_box' : None},
                }
        self._path = ""
        self.refresh()
        dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.window.log.info("RootTree _louie_network_ready")
        self.refresh()
        self.window.log.info("RootTree _louie_network_ready")

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        self.show_directories()
        if self.window.network != None:
            self.lines.append(urwid.Text("    HomeId = %s" % self.window.network.home_id_str, align='left'))
            self.size += 1
        self._modified()

class RootDir (urwid.WidgetWrap):

    def __init__ (self, id=None, name=None, help=None):
        self.id = id
        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
        self.item = [
            ('fixed', 15,
                urwid.Padding(urwid.AttrWrap(urwid.Text('%s' % id, wrap='clip'), 'body', 'focus'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % name, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % help, wrap='clip'), 'body'),
        ]
        w = urwid.Columns(self.item, dividechars=1 )
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class RootItem (urwid.WidgetWrap):

    def __init__ (self, id=0, name=None, location=None, signal=0, battery_level=-1):
        self.id = id
        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
        self.item = [
            ('fixed', 20, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % str(id), wrap='clip'), 'body', 'focus'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % name, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % location, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % signal, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % battery_level, wrap='clip'), 'body'),
        ]
        w = urwid.Columns(self.item, dividechars=1 )
        self.__super.__init__(w)

    def get_header (self):
        self.item = [
            ('fixed', 20, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % "Id", wrap='clip'), 'node_header'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % "Name", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Location", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Baud", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Battery", wrap='clip'), 'node_header'),
        ]
        return urwid.Columns(self.item, dividechars=1)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class RootBox(urwid.ListBox):
    """
    RootBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = RootTree(window, None, self)
        self.__super.__init__(self.walker)

class NodesBox(urwid.ListBox):
    """
    NodexBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = NodesTree(window, parent.walker, self)
        self.__super.__init__(self.walker)

class NodesTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
    #    self.window = window
    #    self._framefocus = framefocus
    #    self.read_nodes(None)
        self.subdirs = ['..']
        self.childrens = { '..' : {'id':'..',
                                    'name':'..',
                                    'help':'Go to previous directory',
                                    'widget_box' : None}
                }
        self._path = "nodes"
        self.node_header = NodesItem()
        self.definition = {'id':'nodes',
                                'name':'nodes',
                                'help':'Nodes management',
                                'widget_box': self.widget_box
        }
        if parent != None and self.definition != None :
            parent.add_child(self.path, self.definition)
        #dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.window.log.info("NodesTree _louie_network_ready")
        self.refresh()
        self.window.log.info("NodesTree _louie_network_ready")
        dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE)
        #dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE_ADDED)
        #dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE_NAMING)
        #dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE_NEW)
        #dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE_PROTOCOL_INFO)
        #dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE_READY)
        #dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE_REMOVED)

    def _louie_node_update(self, network, node_id):
        self.refresh()

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        if self.window.network == None:
            return
        self.show_directories()
        self.lines.append(self.node_header.get_header())
        self.size += 1
        for node in self.window.network.nodes:
            self.lines.append(NodesItem(self.window.network.nodes[node].node_id, \
                self.window.network.nodes[node].name, \
                self.window.network.nodes[node].location, \
                self.window.network.nodes[node].max_baud_rate, \
                self.window.network.nodes[node].battery_level, \
                ))
            self.size += 1
        self._modified()

    def exist(self, directory):
        """
        List directory content
        """
        self.window.log.info("exist in NodesTree")
        if OldestTree.exist(self, directory):
            return True
        self.window.log.info("exist in NodesTree")
        try :
            if int(directory) in self.window.network.nodes:
                return True
        except :
            pass
        self.window.log.info("exist in NodeTrees return false")
        return False

    def cd(self, directory):
        """
        Change to directory and return the widget to display
        """
        if self.exist(directory) :
            if directory == '..':
                return self.parent.widget_box
            if directory in self.childrens:
                self.window.log.info("cd %s" %directory)
                return self.childrens[directory]['widget_box']
            try :
                if int(directory) in self.window.network.nodes:
                    self.window.log.info("cd a node id %s" %directory)
                    self.childrens['node']['widget_box'].walker.key=int(directory)
                    return self.childrens['node']['widget_box']
            except :
                pass
        return None


#class NodesDir (urwid.WidgetWrap):
#
#    def __init__ (self, id=None, help=None):
#        self.id = id
#        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
#        self.item = [
#            ('fixed', 15, urwid.Padding(
#                urwid.AttrWrap(urwid.Text('%s' % id, wrap='clip'), 'body', 'focus'), left=2)),
#        ]
#        w = urwid.Columns(self.item, dividechars=1 )
#        self.__super.__init__(w)
#
#    def selectable (self):
#        return True
#
#    def keypress(self, size, key):
#        return key

class NodesItem (urwid.WidgetWrap):

    def __init__ (self, id=0, name=None, location=None, signal=0, battery_level=-1):
        self.id = id
        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
        self.item = [
            ('fixed', 15, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % str(id), wrap='clip'), 'body', 'focus'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % name, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % location, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % signal, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % battery_level, wrap='clip'), 'body'),
        ]
        w = urwid.Columns(self.item, dividechars=1 )
        self.__super.__init__(w)

    def get_header (self):
        self.item = [
            ('fixed', 15, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % "Id", wrap='clip'), 'node_header'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % "Name", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Location", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Baud", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Battery", wrap='clip'), 'node_header'),
        ]
        return urwid.Columns(self.item, dividechars=1)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class NodeBox(urwid.ListBox):
    """
    NodeBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = NodeTree(window, parent.walker, self)
        self.__super.__init__(self.walker)


class NodeTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
        self.childrens = { '..' : {'id':'..',
                                'name':'..',
                                'help':'Go to previous directory',
                                'widget_box' : None}
                }
        self._path = ""
        self.subdirs = ['..']
    #    self.window = window
    #    self._framefocus = framefocus
    #    self.read_nodes(None)
        self.definition = {'id':'<idx>',
                        'name':'node',
                        'help':'Node management',
                        'widget_box': self.widget_box}
        self.usage.append("set <field> to <value> : change the value of a field")
        if parent != None and self.definition != None :
            parent.add_child("node",self.definition)
        dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.window.log.info("NodeTree _louie_network_ready")
        self.refresh()
        dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE)

    def _louie_node_update(self, network, node_id):
        self.refresh()

    def set(self, param, value):
        if param in ['name', 'location', 'product_name', 'manufacturer_name' ]:
            self.window.network.nodes[self.key].set_field(param, \
                        value)
            self.window.status_bar.update(status='Field %s updated' % param)
            return True
        return False

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        if self.window.network == None or self.key == None:
            return
        self.show_directories()
        self.edit_fields = {
            'name' :              urwid.Edit("  Name <name>                      = ", \
                self.window.network.nodes[self.key].name, align='left'),
            'location' :          urwid.Edit("  Location <location>              = ", \
                self.window.network.nodes[self.key].location, align='left'),
            'product_name' :      urwid.Edit("  Product <product_name>           = ", \
                self.window.network.nodes[self.key].product_name, align='left'),
            'manufacturer_name' : urwid.Edit("  Manufacturer <manufacturer_name> = ", \
                self.window.network.nodes[self.key].manufacturer_name, align='left'),
        }
        if self.window.network != None:
            self.lines.append(self.edit_fields['name'])
            self.size += 1
            self.lines.append(self.edit_fields['location'])
            self.size += 1
            self.lines.append(self.edit_fields['product_name'])
            self.size += 1
            self.lines.append(self.edit_fields['manufacturer_name'])
            self.size += 1
            self.lines.append(urwid.Text(    "  Baud rate                        = %s" % \
                self.window.network.nodes[self.key].max_baud_rate, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  Capabilities                     = %s" % \
                self.window.network.nodes[self.key].capabilities, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  Neighbors                        = %s" % \
                self.window.network.nodes[self.key].neighbors, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  Groups                           = %s" % \
                self.window.network.nodes[self.key].groups, align='left'))
            self.size += 1
        self._modified()

    @property
    def path(self):
        """
        The path

        :rtype: str

        """
        return "%s" % self.key

    def cd(self, directory):
        """
        Change to directory and return the widget to display
        """
        if self.exist(directory) :
            if directory == '..':
                return self.parent.widget_box
            if directory in self.childrens:
                self.window.log.info("cd a values list key=%s" %directory)
                self.childrens[directory]['widget_box'].walker.key=directory
                self.childrens[directory]['widget_box'].walker.node_id=self.key
                return self.childrens[directory]['widget_box']
        return None

class ControllerBox(urwid.ListBox):
    """
    NodeBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = ControllerTree(window, parent.walker, self)
        self.__super.__init__(self.walker)


class ControllerTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
        self.childrens = { '..' : {'id':'..',
                                'name':'..',
                                'help':'Go to previous directory',
                                'widget_box' : None}
                }
        self._path = "controller"
        self.subdirs = ['..']
    #    self.window = window
    #    self._framefocus = framefocus
    #    self.read_nodes(None)
        self.definition = {'id':'controller',
                        'name':'controller',
                        'help':'Controller management',
                        'widget_box': self.widget_box}
        if parent != None and self.definition != None :
            parent.add_child(self._path,self.definition)
        self.usage.append("reset soft : reset the controller in a soft way. Node association is not required")
        self.usage.append("reset hard : reset the controller. Warning : all nodes must be re-associated with your stick.")
        dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.window.log.info("ControllerTree _louie_network_ready")
        self.refresh()
        self.window.log.info("ControllerTree _louie_network_ready")
        dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE)

    def _louie_node_update(self, network, node_id):
        self.refresh()

    def set(self, param, value):
        if param in ['name', 'location', 'product_name', 'manufacturer_name' ]:
            self.window.network.controller.node.set_field(param, \
                        value)
            self.window.status_bar.update(status='Field %s updated' % param)
            return True
        return False

    def reset(self, state):
        if state == 'soft':
            self.window.network.controller.soft_reset()
            self.window.status_bar.update(status='Reset controller softly')
            return True
        if state == 'hard':
            self.window.network.controller.hard_reset()
            self.window.status_bar.update(status='Reset controller hardly')
            return True
        return False

    def read_lines(self):
        self.size = 0
        #self.key = self.window.network.controller.node_id
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        if self.window.network == None:
            return
        self.show_directories()
        self.edit_fields = {
            'name' :              urwid.Edit("  Name <name>                      = ", \
                self.window.network.controller.node.name, align='left'),
            'location' :          urwid.Edit("  Location <location>              = ", \
                self.window.network.controller.node.location, align='left'),
            'product_name' :      urwid.Edit("  Product <product_name>           = ", \
                self.window.network.controller.node.product_name, align='left'),
            'manufacturer_name' : urwid.Edit("  Manufacturer <manufacturer_name> = ", \
                self.window.network.controller.node.manufacturer_name, align='left'),
        }
        if self.window.network != None:
            self.lines.append(self.edit_fields['name'])
            self.size += 1
            self.lines.append(self.edit_fields['location'])
            self.size += 1
            self.lines.append(self.edit_fields['product_name'])
            self.size += 1
            self.lines.append(self.edit_fields['manufacturer_name'])
            self.size += 1
            self.lines.append(urwid.Divider("-"))
            self.size += 1
            self.lines.append(urwid.Text(    "  Capabilities = %s" % \
                self.window.network.controller.node.capabilities, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  Neighbors    = %s" % \
                self.window.network.controller.node.neighbors, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  Baud rate    = %s" % \
                self.window.network.controller.node.max_baud_rate, align='left'))
            self.size += 1
            self.lines.append(urwid.Divider("-"))
            self.size += 1
            self.lines.append(urwid.Text(    "  Statistics   = %s" % \
                self.window.network.controller.stats, align='left'))
            self.size += 1
            self.lines.append(urwid.Divider("-"))
            self.size += 1
            self.lines.append(urwid.Text(    "  Device=%s" % \
                self.window.network.controller.device, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  %s" % \
                self.window.network.controller.library_description, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  %s" % \
                self.window.network.controller.ozw_library_version, align='left'))
            self.size += 1
            self.lines.append(urwid.Text(    "  %s" % \
                self.window.network.controller.python_library_version, align='left'))
            self.size += 1
        self._modified()

class ValuesBox(urwid.ListBox):
    """
    ValuesBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = ValuesTree(window, parent.walker, self)
        self.__super.__init__(self.walker)


class ValuesTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
    #    self.window = window
    #    self._framefocus = framefocus
    #    self.read_nodes(None)
        self.subdirs = ['..']
        self.childrens = { '..' : {'id':'..',
                                    'name':'..',
                                    'help':'Go to previous directory',
                                    'widget_box' : None},
                }
        self._path = ""
        self.node_id = None
        self.key = 'User'
        self.value_header = ValuesItem()
        self.definition_user = {'id':'User',
                                'name':'User',
                                'help':'User values management',
                                'widget_box': self.widget_box
        }
        self.definition_basic = {'id':'Basic',
                                'name':'Basic',
                                'help':'Basic values management',
                                'widget_box': self.widget_box
        }
        self.definition_config = {'id':'Config',
                                'name':'Config',
                                'help':'Config values management',
                                'widget_box': self.widget_box
        }
        self.definition_system = {'id':'System',
                                'name':'System',
                                'help':'System values management',
                                'widget_box': self.widget_box
        }
        self.definition_all = {'id':'All',
                                'name':'All',
                                'help':'All values management',
                                'widget_box': self.widget_box
        }
        if parent != None :
            parent.add_child('User', self.definition_user)
            parent.add_child('Basic', self.definition_basic)
            parent.add_child('Config', self.definition_config)
            parent.add_child('System', self.definition_system)
            parent.add_child('All', self.definition_all)
        self.usage.append("set <valueid> to <data> : change value <valueid> to data")
        self.usage.append("set <label> to <data> : change value <label> to data")
        dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.window.log.info("ValuesTree _louie_network_ready")
        self.refresh()
        dispatcher.connect(self._louie_value_update, ZWaveNetwork.SIGNAL_VALUE)
        self.window.log.info("ValuesTree _louie_network_ready")

    def _louie_value_update(self, network, node, value_id):
        self.window.log.info("ValuesTree _louie_value_update")
        self.refresh()
        self.window.log.info("ValuesTree _louie_value_update")

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        if self.window.network == None or self.node_id == None:
            return
        self.show_directories()
        self.lines.append(self.value_header.get_header())
        self.size += 1
        values = self.window.network.nodes[self.node_id].get_values_by_command_classes(genre=self.key)
        for cmd in values :
            self.lines.append(urwid.Text(    "      %s" % (cmd), align='left'))
            self.size += 1
            for val in values[cmd]:
                self.lines.append(ValuesItem(values[cmd][val].value_id, \
                    values[cmd][val].label, \
                    values[cmd][val].help, \
                    values[cmd][val].data, \
                    values[cmd][val].type, \
                    values[cmd][val].data_items, \
                    values[cmd][val].is_read_only, \
                    ))
                self.size += 1
        self._modified()

    def exist(self, directory):
        """
        List directory content
        """
        if OldestTree.exist(self, directory):
            return True
        return False

    def cd(self, directory):
        """
        Change to directory and return the widget to display
        """
        if self.exist(directory) :
            if directory == '..':
                return self.parent.widget_box
            if directory in self.childrens:
                self.window.log.info("cd %s" %directory)
                return self.childrens[directory]['widget_box']
        return None

    def set(self, param, value):
        try:
            param = long(param)
        except:
            ok = False
            for val in self.window.network.nodes[self.node_id].values:
                if self.window.network.nodes[self.node_id].values[val].label == param:
                    param = val
                    ok = True
                    exit
            if not ok :
                self.window.status_bar.update(status="Invalid value ID %s" % (param))
                return False
        if param in self.window.network.nodes[self.node_id].values:
            if self.window.network.nodes[self.node_id].values[param].check_data(value) :
                self.window.network.nodes[self.node_id].values[param].data=value
                self.window.status_bar.update(status='Value %s updated' % param)
                return True
            else :
                self.window.status_bar.update(status='Invalid data value : "%s"' % value)
            return False
        else :
            self.window.status_bar.update(status="Can't find value Id %s" % (param))
            return False

    @property
    def path(self):
        """
        The path

        :rtype: str

        """
        return "%s" % self.key


class ValuesItem (urwid.WidgetWrap):

    def __init__ (self, id=0, name=None, help=None, value=0, type='All', selection='All', read_only=False):
        self.id = id
        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
        if read_only :
            value_widget = urwid.AttrWrap(urwid.Text('%s' % value, wrap='clip'), 'body')
        else :
            value_widget = urwid.AttrWrap(urwid.Edit(edit_text='%s' % value, wrap='space'), 'body')
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % str(id), wrap='space'), 'body', 'focus'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % name, wrap='space'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % help, wrap='space'), 'body'),
                value_widget,
                urwid.AttrWrap(urwid.Text('%s' % type, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % selection, wrap='space'), 'body'),
        ]
        w = urwid.Columns(self.item, dividechars=1 )
        self.__super.__init__(w)

    def get_header (self):
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % "Id", wrap='clip'), 'node_header'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % "Label", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Help", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Value", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Type", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Items", wrap='clip'), 'node_header'),
        ]
        return urwid.Columns(self.item, dividechars=1)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class SwitchesBox(urwid.ListBox):
    """
    SwitchesBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = SwitchesTree(window, parent.walker, self)
        self.__super.__init__(self.walker)

class SwitchesTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
        self.subdirs = ['..']
        self.childrens = { '..' : {'id':'..',
                                    'name':'..',
                                    'help':'Go to previous directory',
                                    'widget_box' : None},
                }
        self._path = "switches"
        self.switch_header = SwitchesItem()
        self.definition = {'id':'switches',
                                'name':'switches',
                                'help':'All switches on the network',
                                'widget_box': self.widget_box
        }
        if parent != None :
            parent.add_child('switches', self.definition)
        self.usage.append("set <nodeid:Label> to <data> : change value <label> of node <nodeid> to data")
#        self.usage.append("set <label> to <data> : change value <label> to data")
        dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.refresh()
        dispatcher.connect(self._louie_value_update, ZWaveNetwork.SIGNAL_VALUE)
        dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE)

    def _louie_value_update(self, network, node, value_id):
        self.refresh()

    def _louie_node_update(self, network, node, node_id):
        self.refresh()

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        if self.window.network == None:
            return
        self.show_directories()
        self.lines.append(self.switch_header.get_header())
        self.size += 1
        for node in self.window.network.nodes :
            switches = self.window.network.nodes[node].get_switches()
            if len(switches) != 0 :
                self.lines.append(urwid.Text(    "      %s - %s" % (self.window.network.nodes[node].node_id,self.window.network.nodes[node].name), align='left'))
                self.size += 1
                for switch in switches:
                    self.lines.append(SwitchesItem(switches[switch].value_id, \
                        switches[switch].label, \
                        switches[switch].help, \
                        switches[switch].data, \
                        switches[switch].type, \
                        switches[switch].data_items, \
                        ))
                    self.size += 1
        self._modified()

    def exist(self, directory):
        """
        List directory content
        """
        if OldestTree.exist(self, directory):
            return True
        return False

    def cd(self, directory):
        """
        Change to directory and return the widget to display
        """
        if self.exist(directory) :
            if directory == '..':
                return self.parent.widget_box
            if directory in self.childrens:
                self.window.log.info("cd %s" %directory)
                return self.childrens[directory]['widget_box']
        return None

    def set(self, param, value):
        try:
            self.window.log.info("SwitchesTree set %s" % param)
            node,switch = param.split(':',1)
            node = int(node)
        except:
            self.window.status_bar.update(status="Invalid node:label %s" % (param))
            return False
        ok = False
        for val in self.window.network.nodes[int(node)].values:
            self.window.log.info("SwitchesTree set %s val %s" % (node,val))
            if self.window.network.nodes[node].values[val].label == switch:
                switch = val
                ok = True
                exit
        if not ok :
            self.window.status_bar.update(status="Invalid label %s on node %s" % (switch,node))
            return False
        if node in self.window.network.nodes:
            if self.window.network.nodes[node].values[switch].check_data(value) :
                self.window.network.nodes[node].values[switch].data=value
                self.window.status_bar.update(status='Value %s on node %s updated' % (switch,node))
                return True
            else :
                self.window.status_bar.update(status='Invalid data value : "%s"' % value)
            return False
        else :
            self.window.status_bar.update(status="Can't find node %s" % (node))
            return False

class SwitchesItem (urwid.WidgetWrap):

    def __init__ (self, id=0, name=None, help=None, value=0, type='All', selection='All'):
        self.id = id
        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
        value_widget = urwid.AttrWrap(urwid.Edit(edit_text='%s' % value, wrap='space'), 'body')
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % str(id), wrap='space'), 'body', 'focus'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % name, wrap='space'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % help, wrap='space'), 'body'),
                value_widget,
                urwid.AttrWrap(urwid.Text('%s' % type, wrap='clip'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % selection, wrap='space'), 'body'),
        ]
        w = urwid.Columns(self.item, dividechars=1 )
        self.__super.__init__(w)

    def get_header (self):
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % "Id", wrap='clip'), 'node_header'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % "Label", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Help", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Value", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Type", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Items", wrap='clip'), 'node_header'),
        ]
        return urwid.Columns(self.item, dividechars=1)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class SensorsBox(urwid.ListBox):
    """
    SensorsBox show the walker
    """
    def __init__(self, window, parent, framefocus):
        self.window = window
        self.parent = parent
        self._framefocus = framefocus
        self.walker = SensorsTree(window, parent.walker, self)
        self.__super.__init__(self.walker)

class SensorsTree(OldestTree):

    def __init__(self, window, parent, widget_box):
        OldestTree.__init__(self, window, parent, widget_box)
        self.subdirs = ['..']
        self.childrens = { '..' : {'id':'..',
                                    'name':'..',
                                    'help':'Go to previous directory',
                                    'widget_box' : None},
                }
        self._path = "sensors"
        self.sensor_header = SensorsItem()
        self.definition = {'id':'sensors',
                                'name':'sensors',
                                'help':'All sensors on the network',
                                'widget_box': self.widget_box
        }
        if parent != None :
            parent.add_child('sensors', self.definition)
#        self.usage.append("set <nodeid:Label> to <data> : change value <label> of node <nodeid> to data")
#        self.usage.append("set <label> to <data> : change value <label> to data")
        dispatcher.connect(self._louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

    def _louie_network_ready(self, network):
        self.refresh()
        dispatcher.connect(self._louie_value_update, ZWaveNetwork.SIGNAL_VALUE)
        dispatcher.connect(self._louie_node_update, ZWaveNetwork.SIGNAL_NODE)

    def _louie_value_update(self, network, node, value_id):
        self.refresh()

    def _louie_node_update(self, network, node, node_id):
        self.refresh()

    def read_lines(self):
        self.size = 0
        #self.focus, self.oldfocus = self.oldfocus, self.focus
        self.lines = []
        if self.window.network == None:
            return
        self.show_directories()
        self.lines.append(self.sensor_header.get_header())
        self.size += 1
        for node in self.window.network.nodes :
            sensors = self.window.network.nodes[node].get_sensors()
            if len(sensors) != 0 :
                self.lines.append(urwid.Text(    "      %s - %s" % (self.window.network.nodes[node].node_id,self.window.network.nodes[node].name), align='left'))
                self.size += 1
                for sensor in sensors:
                    self.lines.append(SensorsItem(sensors[sensor].value_id, \
                        sensors[sensor].label, \
                        sensors[sensor].help, \
                        sensors[sensor].data, \
                        sensors[sensor].type, \
                        sensors[sensor].units, \
                    ))
                    self.size += 1
        self._modified()

    def exist(self, directory):
        """
        List directory content
        """
        if OldestTree.exist(self, directory):
            return True
        return False

    def cd(self, directory):
        """
        Change to directory and return the widget to display
        """
        if self.exist(directory) :
            if directory == '..':
                return self.parent.widget_box
            if directory in self.childrens:
                self.window.log.info("cd %s" %directory)
                return self.childrens[directory]['widget_box']
        return None

class SensorsItem (urwid.WidgetWrap):

    def __init__ (self, id=0, name=None, help=None, value=0, type='All', units=""):
        self.id = id
        #self.content = 'item %s: %s - %s...' % (str(id), name[:20], product_name[:20] )
        value_widget = urwid.AttrWrap(urwid.Text('%s' % value, wrap='space'), 'body')
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % str(id), wrap='space'), 'body', 'focus'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % name, wrap='space'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % help, wrap='space'), 'body'),
                urwid.AttrWrap(urwid.Text('%s' % type, wrap='clip'), 'body'),
                value_widget,
                urwid.AttrWrap(urwid.Text('%s' % units, wrap='space'), 'body'),
        ]
        w = urwid.Columns(self.item, dividechars=1 )
        self.__super.__init__(w)

    def get_header (self):
        self.item = [
            ('fixed', 19, urwid.Padding(
                urwid.AttrWrap(urwid.Text('%s' % "Id", wrap='clip'), 'node_header'), left=2)),
                urwid.AttrWrap(urwid.Text('%s' % "Label", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Help", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Type", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Value", wrap='clip'), 'node_header'),
                urwid.AttrWrap(urwid.Text('%s' % "Units", wrap='clip'), 'node_header'),
        ]
        return urwid.Columns(self.item, dividechars=1)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key
