from xml.dom.minidom import parse, parseString
import types
import gettext
from gettext import gettext as _
from Tkinter import *
#from ttk import *
from ttk import Separator, Labelframe
#from Tkinter import Scale, Button
import os
try:
    import Image, ImageTk
except ImportError, e:
    print 'ImportError %s' % e
    USE_IMAGE = FALSE
else:
    USE_IMAGE = TRUE
import pdb

class Log():
    def d(self, msg):
        print msg
    def i(self, msg):
        print msg
logger = Log()
def __(str):
    if not str:
        return str
    if str[:2] == '((' and str[-2:] == '))':
        return gettext.gettext(str[2:-2])
    return str

def N_(str):
    return str
   
def xgc_get_bool(str):
    if str == 'false':
        return False
    return True

#def xgc_get_position_type(str):
#    if str == 'left':
#        return gtk.POS_LEFT
#    elif str == 'right':
#        return gtk.POS_RIGHT
#    elif str == 'bottom':
#        return gtk.POS_BOTTOM
#    else:
#        return gtk.POS_TOP

class TkXml(object):
    def __init__(self, master, uixmlfile, uixml_rootname=None):
        self.master = master
        self.uixmldoc = parse(uixmlfile)
        self.id_map = {}
        self.widget_info_map = {}
        self.name_map = {}
        self.name_value_map = {}
        self.checked_list = []
        
        self.group_map = {}
        self.readonly_map = {}
        self.togglebutton_map = {}
        self.checkbutton_map = {}
        self.radiobutton_map = {}
        #self.radiogroup_map = {}
        self.range_map = {}
        self.optionmenu_map = {}
        self.list_map = {}
        self.choose_list_map = {}
        self.entry_map = {}
        self.spinbutton_map = {}
        self.combo_map = {}
        self.tooltips_map = {}
        self.enable_map = {}
        self.disable_map = {}
        self.mnemonic_label_map = {}
        self.pixbuf_map = {}  # Use to convert from string to pixbuf.
        self.pixbuf_revmap = {}  # Use to convert from pixbuf to string.
        self.anonymous_tooltips = [] # Use to keep the anonymous alive.

        if not uixml_rootname:
            uixml_rootnode = self.uixmldoc.documentElement
        else:
            uixml_rootnodes = self.uixmldoc.getElementsByTagName(uixml_rootname)
            if uixml_rootnodes == []:
                uixml_rootnode = self.uixmldoc.documentElement
            else:
                for uixml_rootnode in uixml_rootnodes[0].childNodes:
                    if uixml_rootnode.nodeType == uixml_rootnode.ELEMENT_NODE:
                        break
        self.widget = self.xgcwidget_create(self.master, uixml_rootnode)
        self.widget.pack()

        connected_widget = []
        def connect_btn(widget, func, data):
            if os.name == 'nt':
                # on windows platform have bugs on bind method (variable do not change before event, so get variable value is incorrect)
                widget.config(command=lambda : func(data))
            else:
                widget.bind("<ButtonRelease-1>", lambda event: func(data))
            
        for id_ in self.enable_map.keys():
            w = self.id_map[id_]
            id_, name = self.widget_info_map[w]
            for widget in self.name_map[name]:
                if widget not in connected_widget:
                    connected_widget.append(widget)
                    connect_btn(widget, self.enable_toggle, widget)
                    
        for widget in self.checked_list:
            self.enable_toggle(widget)
            
        for widget in self.checkbutton_map.keys():
            self.enable_toggle(widget)
            
    def enable_toggle(self, widget):
        id_, name = self.widget_info_map[widget]
        value = self.name_value_map[name]
        
        for widget in self.name_map[name]:
            if widget.widgetName == 'radiobutton' or widget.widgetName == 'ttk::radiobutton':
                if value.get() == widget.cget('value'):
                    state = NORMAL;
                else:
                    state = DISABLED
            elif widget.widgetName == 'checkbutton' or widget.widgetName == 'ttk::checkbutton':
                if value.get():
                    state = NORMAL
                else:
                    state = DISABLED
            id_, name = self.widget_info_map[widget]
            if self.enable_map.has_key(id_):
                for w in self.enable_map[id_]:
                    w.config(state=state)
            
    def _xgc_attr(self, node, attrname, attrdefault):
        attrval = node.getAttribute(attrname)
        if not attrval:
            attrval = attrdefault
        return  attrval
    
    def _xgc_container_public(self, widget, node):
        margin = node.getAttribute('margin')
        if margin:
            widget.config(borderwidth=int(margin))
        for subnode in node.childNodes:
            if subnode.nodeType == subnode.ELEMENT_NODE:
                subwidget = self.xgcwidget_create(widget, subnode)
                if subwidget:
                    subwidget.pack()
                #break
            
    def _xgc_box_public(self, widget, node, box_type='hbox'):
        margin = node.getAttribute('margin')
        if margin:
            widget.config(borderwidth=int(margin))
            
        #def_pack = self._xgc_attr(node, 'def_pack', 'start')
        def_expand = self._xgc_attr(node, 'def_expand', 'false')
        #def_fill = self._xgc_attr(node, 'def_fill', 'false')
        def_padding = self._xgc_attr(node, 'def_padding', '0')
        row = 0
        column = 0
        for subnode in node.childNodes:
            if subnode.nodeType == subnode.ELEMENT_NODE:
                child = self.xgcwidget_create(widget, subnode)
                if child is None:
                    continue
                #pack = self._xgc_attr(subnode, 'pack', def_pack)
                expand = xgc_get_bool(self._xgc_attr(subnode, 'expand', def_expand))
                #fill = xgc_get_bool(self._xgc_attr(subnode, 'fill', def_fill))
                padding = int(self._xgc_attr(subnode, 'padding', def_padding))
                
                logger.d('pack %s grid row %s col %s padx %s pady %s sticky %s' % (box_type, row, column, padding, padding, expand))
                if expand:
                    child.grid(row=row, column=column, padx=padding, pady=padding, sticky=N+W+S+E)
                else:
                    child.grid(row=row, column=column, padx=padding, pady=padding, sticky=N+W)

                if box_type == 'hbox':
                    column += 1
                else:
                    row += 1
                    

    def _xgc_connect(self, widget, node, attrname, data=None):
        attrsignal = node.getAttribute(attrname)
        if attrsignal:
            if attrname == 'clicked' or attrname == 'value-changed' \
                or attrname == 'toggled':
                # bind clicked
                if data:
                    widget.config(command=lambda: getattr(self, attrsignal)(data))
                else:
                    widget.config(command=getattr(self, attrsignal))
            else:
                raise Exception('no this connect %s' % attrname)
            
    def xgc_vbox(self, parent, node):
        #homogeneous = xgc_get_bool(self._xgc_attr(node, 'homogeneous', 'false'))
        spacing = int(self._xgc_attr(node, 'spacing', '0'))
        widget = Frame(parent, borderwidth=spacing)
        self._xgc_box_public(widget, node, 'vbox')
        return widget
    
    def xgc_hbox(self, parent, node):
        spacing = int(self._xgc_attr(node, 'spacing', '0'))
        widget = Frame(parent, borderwidth=spacing)
        self._xgc_box_public(widget, node, 'hbox')
        return widget
    
    def xgc_frame(self, parent, node):
        label = node.getAttribute('label')
        title=__(label) # not support
        if title:
            widget = Labelframe(parent, text=label)
        else:
            widget = Frame(parent)
        
#        label_align = node.getAttribute('label_align')
#        if label_align:
#            widget.set_label_align(float(label_align), 0.5)

#        type = xgc_get_shadow_type(self._xgc_attr(node, 'type', 'etched_in'))
#        widget.set_shadow_type(type)
        self._xgc_container_public(widget, node)
        #self._xgc_box_public(widget, node)
        return widget
    
    def xgc_label(self, parent, node):
        label = __(node.getAttribute('text'))
        widget = Label(parent, text=label)
        return widget
    
    def xgc_button(self, parent, node):
        label = __(node.getAttribute('label'))
        v = StringVar()
        widget = Button(parent, text=label, textvariable=v)
        widget.ext_var = v
        if label:
            v.set(label)
        else:
            pass
#            widget = Button(parent)
        self._xgc_connect(widget, node, 'clicked')
        if USE_IMAGE:
            for subnode in node.getElementsByTagName('image'):
                if subnode and subnode.nodeType == subnode.ELEMENT_NODE:
                    imgfile = self._xgc_attr(subnode, 'file', '')
                    if imgfile:
                        bitmap = ImageTk.PhotoImage(Image.open(imgfile)) #@UndefinedVariable
                        widget.config(image=bitmap, compound=CENTER)
                        widget.image = bitmap
                break # only first
                
        for subnode in node.getElementsByTagName('label'):
            if subnode and subnode.nodeType == subnode.ELEMENT_NODE:
                text = self._xgc_attr(subnode, 'text', '')
                if text:
                    widget.config(text=text, compound=CENTER)
            break # only first
        width = self._xgc_attr(node, 'width', '')
        if width:
            widget.config(width=int(width))
        height = self._xgc_attr(node, 'height', '')
        if height:
            widget.config(height=int(height))
        
        return widget
    
    def xgc_image(self, parent, node):
        if USE_IMAGE:
            imgfile = self._xgc_attr(node, 'file', '')
            #bitmap = BitmapImage(file=imgfile)
            bitmap = ImageTk.PhotoImage(Image.open(imgfile)) #@UndefinedVariable
            label = Label(parent, image=bitmap)
            label.image = bitmap # keep a reference!
            #label.pack()
            return label
        else:
            return None
    
    def xgc_entry(self, parent, node):
#        max = int(self._xgc_attr(node, 'max', 0))
        v = StringVar()
        widget = Entry(parent, textvariable=v)
        widget.ext_var = v
#        visible = node.getAttribute('visible')
#        if visible == 'false':
#            widget.set_visibility(False)
        editable = xgc_get_bool(self._xgc_attr(node, 'editable', 'true'))
        if not editable:
            widget.config(state=DISABLED)
        width = node.getAttribute('width')
        if width:
            widget.config(width=int(width))
        value = node.getAttribute('value')
        if value:
            self.entry_map[widget] = value
        return widget
    
    def _xgc_range_public(self, widget, node, attrname):
        value = node.getAttribute('value')
        if value:
            self.range_map[widget] = value
        self._xgc_connect(widget, node, attrname)

    def _xgc_scale_public(self, widget, node, attrname):
        self._xgc_range_public(widget, node, attrname)
        # <digits> The way your program reads the current value shown in a scale widget is through a control variable; 
        # see Section 28, "Control variables: the values behind the widgets". The control variable for a scale can be an IntVar, 
        # a DoubleVar (float), or a StringVar. If it is a string variable, the digits option controls 
        # how many digits to use when the numeric scale value is converted to a string.
        #digits = node.getAttribute('digits')
        #if digits:
        #    widget.config(digits=int(digits))
        lower = float(self._xgc_attr(node, 'lower', '0'))
        widget.config(from_=lower)
        upper = float(self._xgc_attr(node, 'upper', '31'))
        widget.config(to=upper)
        stepinc = float(self._xgc_attr(node, 'stepinc', '1'))
        if stepinc:
            widget.config(resolution=stepinc)
        length = float(self._xgc_attr(node, 'length', '0'))
        if length:
            widget.config(length=length)
        width = float(self._xgc_attr(node, 'width', '0'))
        if width:
            widget.config(width=width)
#        pagesize = float(self._xgc_attr(node, 'pagesize', '0'))
#        pageinc = float(self._xgc_attr(node, 'pageinc', '4'))
        
#        valuepos = node.getAttribute('valuepos')
#        if valuepos:
#            widget.set_value_pos(xgc_get_position_type(valuepos))
            
    def xgc_hscale(self, parent, node):
        widget = Scale(parent, orient=HORIZONTAL)
        self._xgc_scale_public(widget, node, 'value-changed')
        return widget

    def xgc_vscale(self, parent, node):
        widget = Scale(parent, orient=VERTICAL)
        self._xgc_scale_public(widget, node, 'value-changed')
        return widget
    
    # This text widget is used for show some text only.
    def xgc_text(self, parent, node):
        # Make the filename translatable let us can provide files in different language.
        filename = __(node.getAttribute('filename'))
        try:
            f = file(filename, 'r')
        except IOError:
            data = _("File is not found: ") + filename
        else:
            data = f.read()
            f.close()

#        hpolicy = xgc_get_policy(self._xgc_attr(node, 'hpolicy', 'never'))
#        vpolicy = xgc_get_policy(self._xgc_attr(node, 'vpolicy', 'automatic'))
#        shadow_type = xgc_get_shadow_type(self._xgc_attr(node, 'shadow_type', 'in'))
#        wrap_mode = xgc_get_wrap_mode(self._xgc_attr(node, 'wrap_mode', 'word'))

#        widget = gtk.ScrolledWindow()
#        widget.set_policy(hpolicy, vpolicy)
#        widget.set_shadow_type(shadow_type)
        width = self._xgc_attr(node, 'width', 80)
        height = self._xgc_attr(node, 'height', 15)

        text_box_frame = Frame(parent)
        tv = Text(text_box_frame, width=width, height=height)
        scroll = Scrollbar(text_box_frame)
        scroll.pack(side=RIGHT, fill=Y)
        tv.pack(side=LEFT, fill=Y)
        scroll.config(command=tv.yview)
        tv.config(yscrollcommand=scroll.set)
#        buffer = gtk.TextBuffer(None)
#        tv.set_buffer(buffer)
#        tv.set_editable(False)
#        tv.set_cursor_visible(False)
#        tv.set_wrap_mode(wrap_mode)
        
#        iter = buffer.get_iter_at_offset(0)
#        buffer.insert(iter, data)
        return  text_box_frame
    
    def xgc_table(self, parent, node):
#        rows = int(self._xgc_attr(node, 'rows', '1'))
#        columns = int(self._xgc_attr(node, 'columns', '1'))
        widget = Frame(parent)
#        colspacings = node.getAttribute('colspacings')
#        if colspacings:
#            widget.set_col_spacings(int(colspacings))
#        rowspacings = node.getAttribute('rowspacings')
#        if rowspacings:
#            widget.set_row_spacings(int(rowspacings))
        margin = node.getAttribute('margin')
        if margin:
            #widget.set_border_width(int(margin))
            widget.config(borderwidth=margin)
        
        cur_row = -1
        cur_col = -1
        
        def do_each_node(widget, subnode, cur_row, cur_col):
            child = self.xgcwidget_create(widget, subnode)
            if child is None:
                return cur_col
            cur_col += 1
                
            padx = int(self._xgc_attr(subnode, 'padx', 0))
            pady = int(self._xgc_attr(subnode, 'pady', 0))

            rowspan = int(self._xgc_attr(subnode, 'rowspan', '1'))
            columnspan = int(self._xgc_attr(subnode, 'colspan', '1'))
            expand = self._xgc_attr(subnode, 'expand', '')
            if expand == 'fill':
                sticky = N+W+S+E
            else:
                sticky = N+W
            child.grid(row=cur_row, column=cur_col, padx=padx, pady=pady, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
            
            return cur_col
        
        for trnode in node.childNodes:
            if trnode.nodeType != trnode.ELEMENT_NODE:
                continue
            cur_row += 1
            cur_col = -1
            if trnode.tagName == 'tr':
                # do td in tr parse
                for tdnode in trnode.childNodes:
                    if tdnode.nodeType != tdnode.ELEMENT_NODE:
                        continue
                    if tdnode.tagName == 'td':
                        for subnode in tdnode.childNodes:
                            if subnode.nodeType != subnode.ELEMENT_NODE:
                                continue
                            cur_col = do_each_node(widget, subnode, cur_row, cur_col)
                    else:
                         cur_col = do_each_node(widget, tdnode, cur_row, cur_col)
            else:
                # do one row
                cur_col = do_each_node(widget, trnode, cur_row, cur_col)
            
        return widget
    
    def xgc_radiobutton(self, parent, node):
        label = __(node.getAttribute('label'))
        widget = None
        name = self._xgc_attr(node, 'name', '')
        value = node.getAttribute('value')
        if name and value:
            if self.name_value_map.has_key(name):
                widget = Radiobutton(parent, text=label, variable=self.name_value_map[name], value=value)
            else:
                v = StringVar()
                widget = Radiobutton(parent, text=label, variable=v, value=value)
                self.name_value_map[name] = v
        else:
            raise Exception('radio button should have name and value attr for group')

        if node.hasAttribute('checked'):
            self.name_value_map[name].set(value)
            self.checked_list.append(widget)
            
        self._xgc_connect(widget, node, 'toggled')
        #self._xgc_container_public(widget, node)
        return widget
    
    def xgc_checkbutton(self, parent, node):
        label = __(node.getAttribute('label'))
        widget = None
        name = self._xgc_attr(node, 'name', '')
        value = node.getAttribute('value')        
        if name:
            if self.name_value_map.has_key(name):
                widget = Checkbutton(parent, text=label, variable=self.name_value_map[name], onvalue = 1, offvalue = 0)
                widget.ext_var = self.name_value_map[name]
            else:
                v = IntVar()
                widget = Checkbutton(parent, text=label, variable=v, onvalue = 1, offvalue = 0)
                self.name_value_map[name] = v
                widget.ext_var = v
        else:
            raise Exception('check button should have name attr for group')

        if node.hasAttribute('checked'):
            self.name_value_map[name].set(1)
            self.checked_list.append(widget)
            
        self._xgc_connect(widget, node, 'toggled')
#        self._xgc_container_public(widget, node)
        value = node.getAttribute('value')
        self.checkbutton_map[widget] = value

        return widget
    
#        Checkbutton(self.frame1, text='Update USB Serial Number', onvalue = 1, offvalue = 0, variable=self.usb_serial_check_val)
#        
#        
#        label = __(node.getAttribute('label'))
#        widget = Checkbutton(label)
#        self._xgc_connect(widget, node, 'toggled')
#        self._xgc_container_public(widget, node)
#        value = node.getAttribute('value')
#        if value:
#            self.checkbutton_map[widget] = value
#        return widget
    
    def xgc_hseparator(self, parent, node):
        return Separator(parent, orient=HORIZONTAL)

    def xgc_vseparator(self, parent, node):
        return Separator(parent, orient=VERTICAL)
    
    def xgcwidget_create(self, parent, node):
        if node.nodeType != node.ELEMENT_NODE:
            return None
        xgcfunc = getattr(self, 'xgc_' + node.tagName, None)
        if xgcfunc:
            widget = xgcfunc(parent, node)
        else:
            logger.d("Can't create widget for node: %s" % node.tagName)
            widget = None
        if widget is None:
            widget = Label(parent, text='Not support %s' % node.tagName)
            return widget
            #return None
            
        name = node.getAttribute('name')
        if name:
            self.name_map.setdefault(name, []).append(widget)
            
        id_ = node.getAttribute('id')
        if id_:
            self.id_map[id_] = widget
        self.widget_info_map[widget] = (id_, name)
        
#        group = node.getAttribute('group')
#        if group:
#            if self.group_map.has_key(group):
#                self.group_map[group].append(widget)
#            else:
#                self.group_map[group] = [widget]
#        show = node.getAttribute('show')
#        if not show or show == 'true':
#            widget.show()
#        sensitive = node.getAttribute('sensitive')
#        if sensitive == 'false':
#            widget.set_sensitive(False)
        enable = node.getAttribute('enable')
        if enable:
            self.enable_map.setdefault(enable, []).append(widget)
#        disable = node.getAttribute('disable')
#        if disable:
#            if self.disable_map.has_key(disable):
#                self.disable_map[disable].append(widget)
#            else:
#                self.disable_map[disable] = [widget]
#        desclabel = node.getAttribute('desclabel')
#        desctext = node.getAttribute('desctext')
#        if desclabel and desctext:
#            widget.connect('enter-notify-event', self.set_desc_label,
#                           (desclabel, __(desctext)))
#            widget.connect('leave-notify-event', self.set_desc_label,
#                           (desclabel, ''))
        return widget

    
    def fill_values(self, data_xml):
#        for widget in self.togglebutton_map.keys():
#            value = self.get_data(data_xml, self.togglebutton_map[widget])
#            if value == 'true':
#                widget.set_active(True)
#            else:
#                widget.set_active(False)
#        for widget in self.checkbutton_map.keys():
#            value = self.get_data(data_xml, self.checkbutton_map[widget])
#            if value == 'true':
#                widget.set_active(True)
#            else:
#                widget.set_active(False)

#        for name in self.radiobutton_map.keys():
#            for widget in self.name_map():
#                if node.hasAttribute('checked'):
#                    self.radiogroup_map[name].set(value)
#            value = self.get_data(data_xml, self.radiobutton_map[widget][0])
#            if value == self.radiobutton_map[widget][1]:
#                widget.set_active(True)
#            else:
#                widget.set_active(False)

#        for widget in self.optionmenu_map.keys():
#            value = self.get_data(data_xml, self.optionmenu_map[widget][0])
#            for i in range(len(self.optionmenu_map[widget][1])):
#                if self.optionmenu_map[widget][1][i] == value:
#                    widget.set_active(i)
#                    break
#        for model in self.list_map.keys():
#            cur_node = self.srh_data_node(data_xml, self.list_map[model][0])
#            if cur_node:
#                model.clear()
#                storelist = self.list_map[model][1]
#                for subnode in cur_node.getElementsByTagName('row'):
#                    collist = self.create_collist_from_node(subnode, storelist)
#                    iter = model.append()
#                    model.set(iter, *collist)
#        for model in self.choose_list_map.keys():
#            (choose_value, choose_id, selection) = self.choose_list_map[model]
#            cur_node = self.srh_data_node(data_xml, choose_value)
#            if cur_node:
#
#                selection.unselect_all()
#                id_map = {}
#                for subnode in cur_node.getElementsByTagName('select'):
#                    id = subnode.getAttribute('id')
#                    id_map[id] = 'y'
#                iter = model.get_iter_first()
#                while iter:
#                    id = model.get_value(iter, choose_id)
#                    if id_map.has_key(id):
#                        selection.select_iter(iter)
#                    iter = model.iter_next(iter)
#                del(id_map)
        for widget in self.entry_map.keys():
            widget.set_text(self.get_data(data_xml, self.entry_map[widget]))
#        for widget in self.spinbutton_map.keys():
#            widget.set_value(float(self.get_data(data_xml, self.spinbutton_map[widget])))
#        for widget in self.combo_map.keys():
#            value = self.get_data(data_xml, self.combo_map[widget][0])
#            has_find = False
#            for i in range(len(self.combo_map[widget][1])):
#                if self.combo_map[widget][1][i] == value:
#                    widget.set_active(i)
#                    has_find = True
#                    break
#            if not has_find:
#                widget.child.set_text(self.get_data(data_xml, self.combo_map[widget][0]))
#        for enable in self.enable_map.keys():
#            self.enable_toggle(self.name_map[enable], enable)
#        for disable in self.disable_map.keys():
#            self.disable_toggle(self.name_map[disable], disable)
#        # SO STRANGE: widget.set_value will change data_xml. Can't understand.
        for widget in self.range_map.keys():
            value = self.get_data(data_xml, self.range_map[widget])
            widget.set(float(value))
            
    def get_variable_by_widget(self, widget):
        id_, name = self.widget_info_map[widget]
        return self.name_value_map[name]
    def get_variable_by_id(self, id_):
        widget = self.id_map[id]
        return self.get_variable_by_widget(widget)
        
    def get_variable_by_name(self, name):
        return self.name_value_map[name]
    
class TestTkXml(TkXml):
    def __init__(self, master, uixmlfile):
        TkXml.__init__(self, master, uixmlfile)
        
    def test_clicked(self):
        pdb.set_trace()
        print 'test_clicked'
        
    def test_toggled(self):
        print "It is toggled."
        
if __name__ == '__main__':
    window = Tk()
    tkxml = TestTkXml(window, 'test-xmlgtk.xml')
    print '----------------'
    window.mainloop()
