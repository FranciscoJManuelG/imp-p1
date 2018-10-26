#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject
import datetime
import time
import gettext
_ = gettext.gettext

class Model():

    def add(self, data):
        if data is not None:
           return "200"

    def remove(self, treeiter):
        if treeiter != None:
            return "200"

    def edit(self, treeiter, data):
        if data != None:
            return "200"

class ViewController:
    def __init__(self, model):
        self.model = model
        self.view = View()
        self.view.connect(self)

    def on_create_clicked(self, w):
        data = self.view.get_data()
        r = self.model.add(data)
        if r == "200":
        	self.view.add_act_list(data)

    def on_update_clicked(self, w):
        selection = self.view.get_selection()
        if selection is None:
            return 
        data = self.view.run_edit(selection)
        sensitive = self.view.get_selection() is not None
        self.view.modify.set_sensitive(sensitive)
        self.view.update.set_sensitive(False) 

    def on_modify_clicked(self, w):
        data = self.view.get_data()
        if data is None:
            return 
        (date, duration, category, description) = data
        if ((date == "") or (duration == "") or (category == "") or (description == "")):
            return 
        model, filteriter = self.view.entries.get_selection().get_selected()
        if filteriter == None:
            return 
        treeiter = model.convert_iter_to_child_iter(filteriter)
        r = self.model.edit(treeiter, data)
        if r == "200":
            self.view.modify_act_list(treeiter, data)
    
    def on_delete_clicked(self, w):
        model, filteriter = self.view.entries.get_selection().get_selected()
        if filteriter == None:
            return 
        treeiter = model.convert_iter_to_child_iter(filteriter)
        r = self.model.remove(treeiter)
        if r == "200":
        	self.view.remove_act_list(treeiter)

    def on_entries_selection_changed(self, selection):
        sensitive = self.view.get_selection() is not None
        self.view.update.set_sensitive(sensitive)
        self.view.delete.set_sensitive(sensitive)
        
    def update_view(self,v):
        duracion_aux = self.view.get_duration()
        duration_error = duracion_aux ==""
        try:
                t = float(duracion_aux)
        except ValueError:
            duration_error=True       
        descripcion_aux = self.view.get_description()
        description_error = descripcion_aux ==""
        date = self.view.get_date()
        date_error = date is None
        categoria_aux=self.view.get_category()
        category_error= categoria_aux is None
        self.view.handle_errors (date_error,duration_error,description_error,category_error)
    
	
class View:
    def __init__(self):
    
        today = datetime.datetime.today()
        self.date = Gtk.Entry()
        self.date.set_placeholder_text(_("Ex. {}").format(today.strftime("%x")))
        self.duration = Gtk.Entry()
        self.duration.set_placeholder_text(_("Ex. 16"))
        category_store = Gtk.ListStore(str)
        category_store.append([_("categoria1")])
        category_store.append([_("categoria2")])
        category_store.append([_("categoria3")])
        category_store.append([_("categoria4")])
        category_store.append([_("categoria5")])
        self.category = Gtk.ComboBoxText(model=category_store, entry_text_column=0, active=0)
        self.description = Gtk.Entry()

        self.create = Gtk.Button(label="Añadir nueva entrada")
        self.update = Gtk.Button(label="Editar")
        self.modify = Gtk.Button(label="Modificar datos")
        self.delete = Gtk.Button(label="Eliminar")

        self.store = Gtk.ListStore(str, str, str, str)
        self.store.append([ datetime.date(2018,2,3).strftime("%x"), "20", "categoria1", "Calentamiento previo"])
        self.store.append([ today.strftime("%x"), "12", "categoria2", "Yoga"])
        self.store.append([ datetime.date(2019,5,3).strftime("%x"), "5", "categoria3", "Pilates"])
        self.store.append([ datetime.date(2019,12,23).strftime("%x"), "16", "categoria5", "Natación"])
        self.store.append([ today.strftime("%x"), "42", "categoria4", "Running"])
        filter = self.store.filter_new()
        self.filter = filter
        self.filter_prefix = ""
        
        entries = Gtk.TreeView(filter, headers_visible=True)

        renderer0 = Gtk.CellRendererText()
        column0 = Gtk.TreeViewColumn("Fecha", renderer0, text=0)

        renderer1 = Gtk.CellRendererText()
        column1 = Gtk.TreeViewColumn("Duración", renderer1, text=1)

        renderer2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn("Categoría", renderer2, text=2)

        renderer3 = Gtk.CellRendererText()
        column3 = Gtk.TreeViewColumn("Descripción", renderer3, text=3)
        
        entries.append_column(column0)
        entries.append_column(column1)
        entries.append_column(column2)
        entries.append_column(column3)
        self.entries = entries

        boxForm = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=10)
        boxForm.pack_start(Gtk.Label(_("Fecha:"), xalign=0), False, False, 0)
        boxForm.pack_start(self.date, False, False, 0)
        boxForm.pack_start(Gtk.Label(_("Duración (min.):"), xalign=0), False, False, 0)
        boxForm.pack_start(self.duration, False, False, 0)
        boxForm.pack_start(Gtk.Label(_("Categoría:"), xalign=0), False, False, 0)
        boxForm.pack_start(self.category, False, False, 0)
        boxForm.pack_start(Gtk.Label(_("Descripción:"), xalign=0), False, False, 0)
        boxForm.pack_start(self.description, False, False, 0)

        boxButtonAdd = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=1)
        boxButtonAdd.pack_start(self.create, False, False, 0)

        boxButtonModify = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=1)
        boxButtonModify.pack_start(self.modify, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow(expand=True)
        scrolled_window.set_size_request(250, 300)
        scrolled_window.add(entries)

        boxButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=1)
        boxButtons.pack_start(self.update, False, False, 0)
        boxButtons.pack_start(self.delete, False, False, 0)

        grid = Gtk.Grid(margin=10, column_spacing=10, row_spacing=10)
        grid.attach(boxForm, 0, 0, 1, 1)
        grid.attach(boxButtonAdd, 0, 1, 1, 1)
        grid.attach(boxButtonModify, 0, 2, 1, 1)
        grid.attach(scrolled_window, 0, 3, 1, 1)
        grid.attach(boxButtons, 0, 4, 1, 1)

        self.modify.set_sensitive(False)
        self.update.set_sensitive(False) 
        self.delete.set_sensitive(False)

        win = Gtk.Window(title="ipm1-p1")
        win.connect('delete-event', Gtk.main_quit)
        win.add(grid)
        win.show_all()
        self.win = win
        
        self.date.get_style_context().add_class('error')
        self.category.get_style_context().add_class('error')
        self.description.get_style_context().add_class('error')
        self.duration.get_style_context().add_class('error')
        self.create.set_sensitive(False)
        
        self.mode = "a" ##modo que indica si estamos en modo actualizar datos (u) o añadir datos (a)

    def connect(self, vc):
        self.create.connect('clicked', vc.on_create_clicked) 
        self.update.connect('clicked', vc.on_update_clicked)
        self.update.connect('clicked', self.quit_add_button)
        self.delete.connect('clicked', vc.on_delete_clicked)
        self.modify.connect('clicked', vc.on_modify_clicked)
        self.modify.connect('clicked', self.quit_modify_button)
        self.entries.get_selection().connect("changed", vc.on_entries_selection_changed)
        
        self.date.connect('changed', vc.update_view)
        self.duration.connect('changed', vc.update_view)
        self.category.connect('changed',  vc.update_view)
        self.description.connect('changed', vc.update_view)
    
    def quit_add_button(self, x):
        self.create.set_sensitive(False)
        self.mode = "u"
      
    def quit_modify_button(self, x):
        self.create.set_sensitive(True)
        self.modify.set_sensitive(False)
        self.mode = "a"
		
    def set_error(self, entry, error):
        if error:
            entry.get_style_context().add_class('error')
        else:
            entry.get_style_context().remove_class('error')
    
    def  handle_errors (self,date_error,duration_error,description_error,category_error):
        self.set_error(self.date,date_error)
        self.set_error(self.duration,duration_error)
        self.set_error(self.description,description_error)
        self.set_error(self.category,category_error)
        if self.mode == "a":
            if not date_error and not duration_error and not description_error and not category_error:
                self.create.set_sensitive(True)
            else:
                self.create.set_sensitive(False)
        if self.mode == "u":
            if not date_error and not duration_error and not description_error and not category_error:
                self.modify.set_sensitive(True)
            else:
                self.modify.set_sensitive(False)
            
    def get_data(self):
    	date = datetime.datetime.strptime(self.date.get_text(), "%x").strftime("%x")
    	duration = self.duration.get_text().strip()
    	category = self.category.get_active_text()
    	description = self.description.get_text().strip()
    	return date, duration, category, description

    def run_edit(self, data):
        self.date.set_text(data[0])
        self.duration.set_text(data[1])
        self.category.append_text(data[2])
        self.description.set_text(data[3])

    def add_act_list(self, data):
    	self.store.append(data)

    def remove_act_list(self, data):
    	self.store.remove(data)

    def modify_act_list(self, treeiter, data):
        self.store.set(treeiter, list(range(0,4)), data)

    def get_selection(self):
        model, filteriter = self.entries.get_selection().get_selected()
        if filteriter == None:
        	return None
        treeiter = model.convert_iter_to_child_iter(filteriter)
        return (model.get_model()[treeiter][0], model.get_model()[treeiter][1], model.get_model()[treeiter][2], model.get_model()[treeiter][3])

    def _date(self, text):
        try:
            return datetime.datetime.strptime(text, "%x")
        except ValueError:
            return None

    def get_date(self):
        return (self._date(self.date.get_text().strip()))
        
    def get_duration(self):
        return self.duration.get_text().strip()
        
    def get_description(self):
        return self.description.get_text().strip()
        
    def get_category(self):
        return self.category.get_active_text()
                  
if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    vc = ViewController(Model())
    Gtk.main()
