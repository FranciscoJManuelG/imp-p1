#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import datetime

class ViewController:
    def __init__(self, view):
        self.view = view
        view.connect(self)

    def on_create_clicked(self, w):
        data = self.view.run_dialog_add()
        if data is None:
            return
        (duracion, categoria, descripcion) = data
        if ((duracion == "") or (categoria == "") or (descripcion == "")):
            return
        self.view.filter.get_model().append([duracion, categoria, descripcion])

    def on_update_clicked(self, w):
        selection = self.view.get_selection()
        if selection is None:
            return
        data = self.view.run_dialog_edit(selection)        
        if data is None:
            return
        (duracion, categoria, descripcion) = data
        if ((duracion == "") or (categoria == "") or (descripcion == "")):
            return

        model, filteriter = self.view.entries.get_selection().get_selected()
        if filteriter == None:
            return
        treeiter = model.convert_iter_to_child_iter(filteriter)
        model.get_model().set(treeiter, list(range(0,3)), [duracion, categoria, descripcion])
    
        
    def on_delete_clicked(self, w):
        model, filteriter = self.view.entries.get_selection().get_selected()
        if filteriter == None:
            return
        treeiter = model.convert_iter_to_child_iter(filteriter)
        model.get_model().remove(treeiter)

    
    def on_entries_selection_changed(self, selection):
        sensitive = self.view.get_selection() is not None
        self.view.update.set_sensitive(sensitive)
        self.view.delete.set_sensitive(sensitive)

class View:
    def __init__(self):
        self.prefix  = Gtk.Entry(width_chars=10)
    
        self.create = Gtk.Button(label="Añadir")
        self.update = Gtk.Button(label="Editar")
        self.delete = Gtk.Button(label="Eliminar")

        store = Gtk.ListStore(str, str, str)
        store.append(["20", "WU", "Calentamiento previo"])
        store.append(["12", "WU", "Calentamiento posterior"])
        self.store = store

        filter = store.filter_new()
        filter.set_visible_func(self._entries_visible_func)
        self.filter = filter
        self.filter_prefix = ""
        
        entries = Gtk.TreeView(filter, headers_visible=False)

        renderer1 = Gtk.CellRendererText()
        column1 = Gtk.TreeViewColumn("Duracion", renderer1, text=0)

        renderer2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn("Categoría", renderer2, text=1)

        renderer3 = Gtk.CellRendererText()
        column3 = Gtk.TreeViewColumn("Descripción", renderer3, text=2)
        entries.append_column(column1)
        entries.append_column(column2)
        entries.append_column(column3)
        self.entries = entries

        boxButtonAdd = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=1)
        boxButtonAdd.pack_start(self.create, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow(expand=True)
        scrolled_window.set_size_request(250, 300)
        scrolled_window.add(entries)

        boxButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=1)
        boxButtons.pack_start(self.update, False, False, 0)
        boxButtons.pack_start(self.delete, False, False, 0)

        grid = Gtk.Grid(margin=10, column_spacing=10, row_spacing=10)
        grid.attach(boxButtonAdd, 0, 0, 1, 1)
        grid.attach(scrolled_window, 0, 1, 1, 1)
        grid.attach(boxButtons, 0, 2, 1, 1)
    
        self.update.set_sensitive(False) #Botón ensombrecido y sin poder interactuar
        self.delete.set_sensitive(False)

        self.prefix.connect('changed', self.on_prefix_changed)
        
        win = Gtk.Window(title="ipm1-p1")
        win.connect('delete-event', Gtk.main_quit)
        win.add(grid)
        win.show_all()
        self.win = win

    def connect(self, vc):
        self.create.connect('clicked', vc.on_create_clicked) #Haga alguna acción cuando pulsas uno de los botones
        self.update.connect('clicked', vc.on_update_clicked)
        self.delete.connect('clicked', vc.on_delete_clicked)
        self.entries.get_selection().connect("changed", vc.on_entries_selection_changed)


    def get_selection(self):
        model, filteriter = self.entries.get_selection().get_selected()
        if filteriter == None:
        	return None
        treeiter = model.convert_iter_to_child_iter(filteriter)
        return (model.get_model()[treeiter][0], model.get_model()[treeiter][1], model.get_model()[treeiter][2])#cambio
        
    def on_prefix_changed(self, entry): #No se que es lo que hace
        self.filter_prefix = entry.get_text()
        self.entries.get_model().refilter()        

    def _entries_visible_func(self, model, iter, data):
        if (self.filter_prefix == ""):
            return True
        else:
            return self._fullname(model[iter]).startswith(self.filter_prefix)

    def _fullname(self, item):
        return "{},{}".format(*item)

    def run_dialog_add(self):
        return self._run_dialog_formulario_form("Añadir", None)

    def run_dialog_edit(self, data):
        return self._run_dialog_formulario_form("Editar", data)
    
    def _run_dialog_formulario_form(self, title, data=None):
        dialog = Gtk.Dialog(title, self.win, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dialog.get_content_area()
        grid = Gtk.Grid(margin=20, column_spacing=10, row_spacing=10)
        duracion = Gtk.Entry()
        categoria = Gtk.Entry()
        descripcion = Gtk.Entry()
        if data is not None:
            duracion.set_text(data[0])
            categoria.set_text(data[1])
            descripcion.set_text(data[2])
        grid.attach(Gtk.Label("Duracion"), 0, 0, 1, 1)
        grid.attach(duracion, 1, 0, 1, 1)
        grid.attach(Gtk.Label("Categoría"), 0, 1, 1, 1)
        grid.attach(categoria, 1, 1, 1, 1)
        grid.attach(Gtk.Label("Descripión"), 0, 2, 1, 1)
        grid.attach(descripcion, 1, 2, 1, 1)
        box.pack_start(grid, True, True, 0)
        box.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = (duracion.get_text().strip(), categoria.get_text().strip(), descripcion.get_text().strip())
        else:
            result = None
        dialog.destroy()
        return result


                                   
if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    vc = ViewController(View())
    Gtk.main()
