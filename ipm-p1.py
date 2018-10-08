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
    
    def añadir(self, data, store):
        if data is not None:
            store.append(data)

    def eliminar(self, treeiter, store):
        if treeiter != None:
            store.remove(treeiter)

    def editar(self, treeiter, data, store):
        if data != None:
            store.set(treeiter, list(range(0,4)), data)


class ViewController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        view.connect(self)

    def on_create_clicked(self, w, fecha, duracion, categoria, descripcion):
        data = self.view.run_add(fecha, duracion, categoria, descripcion)
        self.model.añadir(data, self.view.store)

    def on_update_clicked(self, w):
        selection = self.view.get_selection()
        if selection is None:
            return
        data = self.view.run_dialog_edit(selection)        
        if data is None:
            return
        (fecha, duracion, categoria, descripcion) = data
        if ((fecha == "") or (duracion == "") or (categoria == "") or (descripcion == "")):
            return

        model, filteriter = self.view.entries.get_selection().get_selected()
        if filteriter == None:
            return
        treeiter = model.convert_iter_to_child_iter(filteriter)
        self.model.editar(treeiter, data, self.view.store)
    
        
    def on_delete_clicked(self, w):
        model, filteriter = self.view.entries.get_selection().get_selected()
        if filteriter == None:
            return
        treeiter = model.convert_iter_to_child_iter(filteriter)
        self.model.eliminar(treeiter, self.view.store)

    
    def on_entries_selection_changed(self, selection):
        sensitive = self.view.get_selection() is not None
        self.view.update.set_sensitive(sensitive)
        self.view.delete.set_sensitive(sensitive)

class View:
    def __init__(self):
        self.prefix  = Gtk.Entry(width_chars=10)
    
        today = datetime.datetime.today()
        self.fecha = Gtk.Entry()
        self.fecha.set_placeholder_text(_("Ex. {}").format(today.strftime("%x")))
        self.duracion = Gtk.Entry()
        categoria_store = Gtk.ListStore(str)
        categoria_store.append([_("categoria1")])
        categoria_store.append([_("categoria2")])
        categoria_store.append([_("categoria3")])
        categoria_store.append([_("categoria4")])
        categoria_store.append([_("categoria5")])
        self.categoria = Gtk.ComboBoxText(model=categoria_store, entry_text_column=0, active=0)
        renderer_text = Gtk.CellRendererText()
        self.categoria.pack_start(renderer_text, True)
        self.categoria.add_attribute(renderer_text, "text", 0)
        self.descripcion = Gtk.Entry()

        self.create = Gtk.Button(label="Añadir")
        self.update = Gtk.Button(label="Editar")
        self.delete = Gtk.Button(label="Eliminar")

        self.store = Gtk.ListStore(str, str, str, str)
        self.store.append([ datetime.date(2018,2,3).strftime("%x"), "20", "categoria1", "Calentamiento previo"])
        self.store.append([ today.strftime("%x"), "12", "categoria2", "Yoga"])
        self.store.append([ datetime.date(2019,5,3).strftime("%x"), "5", "categoria3", "Pilates"])
        self.store.append([ datetime.date(2019,12,23).strftime("%x"), "16", "categoria5", "Natación"])
        self.store.append([ today.strftime("%x"), "42", "categoria4", "Running"])
        filter = self.store.filter_new()
        filter.set_visible_func(self._entries_visible_func)
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

        boxFormulario = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=10)
        boxFormulario.pack_start(Gtk.Label(_("Fecha:"), xalign=0), False, False, 0)
        boxFormulario.pack_start(self.fecha, False, False, 0)
        boxFormulario.pack_start(Gtk.Label(_("Duración:"), xalign=0), False, False, 0)
        boxFormulario.pack_start(self.duracion, False, False, 0)
        boxFormulario.pack_start(Gtk.Label(_("Categoría:"), xalign=0), False, False, 0)
        boxFormulario.pack_start(self.categoria, False, False, 0)
        boxFormulario.pack_start(Gtk.Label(_("Descripción:"), xalign=0), False, False, 0)
        boxFormulario.pack_start(self.descripcion, False, False, 0)

        boxButtonAdd = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=1)
        boxButtonAdd.pack_start(self.create, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow(expand=True)
        scrolled_window.set_size_request(250, 300)
        scrolled_window.add(entries)

        boxButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=1)
        boxButtons.pack_start(self.update, False, False, 0)
        boxButtons.pack_start(self.delete, False, False, 0)

        grid = Gtk.Grid(margin=10, column_spacing=10, row_spacing=10)
        grid.attach(boxFormulario, 0, 0, 1, 1)
        grid.attach(boxButtonAdd, 0, 1, 1, 1)
        grid.attach(scrolled_window, 0, 2, 1, 1)
        grid.attach(boxButtons, 0, 3, 1, 1)

        self.update.set_sensitive(False) #Botón ensombrecido y sin poder interactuar
        self.delete.set_sensitive(False)

        self.prefix.connect('changed', self.on_prefix_changed)
        
        win = Gtk.Window(title="ipm1-p1")
        win.connect('delete-event', Gtk.main_quit)
        win.add(grid)
        win.show_all()
        self.win = win

    def connect(self, vc):
        self.create.connect('clicked', vc.on_create_clicked, self.fecha, self.duracion, self.categoria, self.descripcion) #Haga alguna acción cuando pulsas uno de los botones
        self.update.connect('clicked', vc.on_update_clicked)
        self.delete.connect('clicked', vc.on_delete_clicked)
        self.entries.get_selection().connect("changed", vc.on_entries_selection_changed)

    def get_selection(self):
        model, filteriter = self.entries.get_selection().get_selected()
        if filteriter == None:
        	return None
        treeiter = model.convert_iter_to_child_iter(filteriter)
        return (model.get_model()[treeiter][0], model.get_model()[treeiter][1], model.get_model()[treeiter][2], model.get_model()[treeiter][3])
        
    def on_prefix_changed(self, entry): #No se que es lo que hace
        self.filter_prefix = entry.get_text()
        self.entries.get_model().refilter()        

    def _entries_visible_func(self, model, iter, data):
        if (self.filter_prefix == ""):
            return True
        else:
            return self._fullname(model[iter]).startswith(self.filter_prefix)

    #def _fullname(self, item):
    #    return "{},{}".format(*item)

    def run_add(self, fecha, duracion, categoria, descripcion):
        return [datetime.datetime.strptime(fecha.get_text(), "%x").strftime("%x"), duracion.get_text().strip(), categoria.get_active_text(), descripcion.get_text().strip()]

    def run_dialog_edit(self, data):
        return self._run_formulario_("Editar",data)

    def _run_formulario_(self, title, data):
        dialog = Gtk.Dialog(title, self.win, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dialog.get_content_area()
        grid = Gtk.Grid(margin=20, column_spacing=10, row_spacing=10)
        fecha = Gtk.Entry()
        duracion = Gtk.Entry()
        categoria_store = Gtk.ListStore(str)
        categoria_store.append([_("categoria1")])
        categoria_store.append([_("categoria2")])
        categoria_store.append([_("categoria3")])
        categoria_store.append([_("categoria4")])
        categoria_store.append([_("categoria5")])
        categoria = Gtk.ComboBoxText(model=categoria_store, entry_text_column=0, active=0)
        renderer_text = Gtk.CellRendererText()
        categoria.pack_start(renderer_text, True)
        categoria.add_attribute(renderer_text, "text", 0)
        descripcion = Gtk.Entry()
        
        fecha.set_text(data[0])
        duracion.set_text(data[1])
        categoria.append_text(data[2])
        descripcion.set_text(data[3])

        grid.attach(Gtk.Label("Fecha"), 0, 0, 1, 1)
        grid.attach(fecha, 1, 0, 1, 1)
        grid.attach(Gtk.Label("Duracion"), 0, 1, 1, 1)
        grid.attach(duracion, 1, 1, 1, 1)
        grid.attach(Gtk.Label("Categoría"), 0, 2, 1, 1)
        grid.attach(categoria, 1, 2, 1, 1)
        grid.attach(Gtk.Label("Descripión"), 0, 3, 1, 1)
        grid.attach(descripcion, 1, 3, 1, 1)
        box.pack_start(grid, True, True, 0)
        box.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = (datetime.datetime.strptime(fecha.get_text(), "%x").strftime("%x"), duracion.get_text().strip(), categoria.get_active_text(), descripcion.get_text().strip())
        else:
            result = None
        dialog.destroy()
        return result


                                   
if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    vc = ViewController(View(), Model())
    Gtk.main()
