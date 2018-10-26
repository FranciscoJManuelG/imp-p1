#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject
from datetime import timedelta
import threading
import os
import datetime
import time
import gettext
import locale
import requests
_ = gettext.gettext

class Model():

	def add(self, dataAdd):
		r = requests.post("http://localhost:5000/worktime", data={'startDate': dataAdd[0], 'endDate' : dataAdd[1], 'category' : dataAdd[2], 'description' : dataAdd[3]})
		j = r.json()
		idEntry = j['id']
		return r.status_code, idEntry

	def remove(self, idEntry):
		r = requests.delete("http://localhost:5000/worktime/" + str(idEntry))
		return r.status_code

	def edit(self, dataEdit, idEntry):
		r = requests.put("http://localhost:5000/worktime/" + str(idEntry), data={'startDate': dataEdit[0], 'endDate' : dataEdit[1], 'category' : dataEdit[2], 'description' : dataEdit[3]})
		return r.status_code

	def find(self, startDate, endDate):
		r = requests.get("http://localhost:5000/worktime?startDate=" + startDate + "&endDate=" + endDate)
		store = r.json()
		return r.status_code, store 

	def find_month(self, startDate, endDate):
		r = requests.get("http://localhost:5000/worktime?startDate=" + startDate + "&endDate=" + endDate)
		store = r.json()
		return r.status_code, store


class ViewController:
    def __init__(self):
        self.model = Model()
        self.view = View()
        self.view.connect(self)

    def on_create_clicked(self, w):
        data = self.view.get_data()
        t = threading.Thread(target=self.on_create_clicked_thread, args=(w, data))  
        t.start()

    def on_create_clicked_thread(self, w, data):
        r = self.model.add(data)
        if r[0] == 200:
        	self.view.add_act_list_thread(data, r[1])
        elif r[0] == 400:
        	self.view.show_error(r[0])
        elif r[0] == 500:
        	self.view.show_error(r[0])

    def on_update_clicked(self, w):
        selection = self.view.get_selection()
        if selection is None:
            return 
        self.view.run_edit(selection)

    def on_modify_clicked(self, w):
        selection = self.view.get_selection()
        data = self.view.get_data()
        idEntry = self.view.get_id(selection)
        if data is None:
            return 
        (date, duration, category, description) = data
        if ((date == "") or (duration == "") or (category == "") or (description == "")):
            return 
        model, filteriter = self.view.entries.get_selection().get_selected()
        if filteriter == None:
            return self.view.get_data
        treeiter = model.convert_iter_to_child_iter(filteriter)
        t = threading.Thread(target=self.on_modify_clicked_thread, args=(w, treeiter, data, idEntry))  
        t.start()

    def on_modify_clicked_thread(self, w, treeiter, data, idEntry):
        r = self.model.edit(data, idEntry)
        if r == 200:
            self.view.modify_act_list_thread(treeiter, data)
        elif r == 400:
            self.view.show_error(r)
        elif r == 404:
            self.view.show_error(r)
        elif r == 400:
            self.view.show_error(r)
    
    def on_delete_clicked(self, w):
        selection = self.view.get_selection()
        model, filteriter = self.view.entries.get_selection().get_selected()
        idEntry = self.view.get_id(selection)
        if filteriter == None:
            return 
        treeiter = model.convert_iter_to_child_iter(filteriter)
        t = threading.Thread(target=self.on_delete_clicked_thread, args=(w, treeiter, idEntry))  
        t.start()

    def on_delete_clicked_thread(self, w, treeiter,  idEntry):
        r = self.model.remove(idEntry)
        if r == 200:
            self.view.remove_act_list_thread(treeiter)
        elif r == 400:
            self.view.show_error(r)
        elif r == 404:
            self.view.show_error(r)
        elif r == 400:
            self.view.show_error(r)

    def on_find_day_clicked(self, w):
        date = self.view.get_date_filter()
        start = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M")
        startDate = start.strftime("%Y-%m-%dT%H:%M")
        end = start + timedelta(days = 1) - timedelta(seconds = 1)
        endDate = end.strftime("%Y-%m-%dT%H:%M")
        t = threading.Thread(target=self.on_find_day_clicked_thread, args=(w, startDate, endDate))  
        t.start()

    def on_find_day_clicked_thread(self, w, startDate, endDate):
        r = self.model.find(startDate, endDate)
        if r[0] == 200:
            self.view.show_in_local_store_thread(r[1])
        elif r[0] == 400:
            self.view.show_error(r[0])
        elif r[0] == 500:
            self.view.show_error(r[0])

    def on_find_entries_clicked(self, w):
        month = self.view.get_month()
        start = datetime.datetime.strptime(month, "%Y-%m-%dT%H:%M")
        startDate = start.strftime("%Y-%m-%dT%H:%M")
        end = start + timedelta(days = self.last_day_of_month(start)) - timedelta(seconds = 1)
        endDate = end.strftime("%Y-%m-%dT%H:%M")
        t = threading.Thread(target=self.on_find_entries_clicked_thread, args=(w, startDate, endDate))  
        t.start()

    def on_find_entries_clicked_thread(self, w, startDate, endDate):
        r = self.model.find_month(startDate, endDate)
        if r[0] == 200:
            self.view.entries_by_month_thread(r[1])
        elif r[0] == 400:
            self.view.show_error(r[0])
        elif r[1] == 500:
            self.view.show_error(r[0])

    def on_summary_month_clicked(self, w):
        month = self.view.get_month()
        start = datetime.datetime.strptime(month, "%Y-%m-%dT%H:%M")
        startDate = start.strftime("%Y-%m-%dT%H:%M")
        end = start + timedelta(days = self.last_day_of_month(start)) - timedelta(seconds = 1)
        endDate = end.strftime("%Y-%m-%dT%H:%M")
        t = threading.Thread(target=self.on_summary_month_clicked_thread, args=(w, startDate, endDate))  
        t.start() 

    def on_summary_month_clicked_thread(self, w, startDate, endDate):
        r = self.model.find_month(startDate, endDate)
        if r[0] == 200:
            self.view.show_in_local_store_thread(r[1])
        if r[0] == 400:
            self.view.show_error(r[0])
        if r[0] == 500:
            self.view.show_error(r[0])


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

    def convert_min_to_s(self, min):
    	s = min * 60
    	return s

    def last_day_of_month(self, date):
    	next_month = date.replace(day=28) + timedelta(days=4)
    	lastDay = next_month - timedelta(days=next_month.day)
    	return lastDay.day
	
class View:
    def __init__(self):
		
        today = datetime.datetime.today()
        self.calendar = Gtk.Calendar()
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
        self.summary = Gtk.Button(label=_("Resumen del mes"))
        self.filter_day = Gtk.Button(label=_("Filtrar dia"))
        self.entry = Gtk.Button(label=_("Días con entradas"))

        self.create = Gtk.Button(label=_("Añadir nueva entrada"))
        self.update = Gtk.Button(label=_("Editar"))
        self.modify = Gtk.Button(label=_("Modificar datos"))
        self.delete = Gtk.Button(label=_("Eliminar"))

        self.store = Gtk.ListStore(int, str, str, str, str)

        filter = self.store.filter_new()
        self.filter = filter
        self.filter_prefix = ""
        entries = Gtk.TreeView(filter, headers_visible=True)

        renderer0 = Gtk.CellRendererText()
        column0 = Gtk.TreeViewColumn(_("Id"), renderer0, text=0)

        renderer1 = Gtk.CellRendererText()
        column1 = Gtk.TreeViewColumn(_("Fecha"), renderer1, text=1)

        renderer2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn(_("Duración"), renderer2, text=2)

        renderer3 = Gtk.CellRendererText()
        column3 = Gtk.TreeViewColumn(_("Categoría"), renderer3, text=3)

        renderer4 = Gtk.CellRendererText()
        column4 = Gtk.TreeViewColumn(_("Descripción"), renderer4, text=4)
        
        entries.append_column(column0)
        entries.append_column(column1)
        entries.append_column(column2)
        entries.append_column(column3)
        entries.append_column(column4)
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

        boxFilter = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=10)
        boxFilter.pack_start(self.filter_day, False, False, 0)
        boxFilter.pack_start(self.summary, False, False, 0)
        boxFilter.pack_start(self.entry, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow(expand=True)
        scrolled_window.set_size_request(250, 300)
        scrolled_window.add(entries)

        boxCalendar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=10)
        boxCalendar.pack_start(self.calendar, False, False, 0)

        boxButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=1)
        boxButtons.pack_start(self.update, False, False, 0)
        boxButtons.pack_start(self.delete, False, False, 0)

        grid = Gtk.Grid(margin=10, column_spacing=10, row_spacing=10)
        grid.attach(boxForm, 0, 0, 1, 1)
        grid.attach(boxButtonAdd, 0, 1, 1, 1)
        grid.attach(boxButtonModify, 0, 2, 1, 1)
        grid.attach(boxFilter, 0, 3, 1, 1)
        grid.attach(scrolled_window, 0, 4, 1, 1)
        grid.attach(boxCalendar, 1, 4, 1, 1)
        grid.attach(boxButtons, 0, 5, 1, 1)

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
        
        #modo que indica si estamos en modo actualizar datos (u) o añadir datos (a)
        self.mode = "a" 
          
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
        
        self.filter_day.connect('clicked', vc.on_find_day_clicked)
        self.summary.connect('clicked',vc.on_summary_month_clicked)
        self.entry.connect('clicked',vc.on_find_entries_clicked)
    
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
        start = datetime.datetime.strptime(self.date.get_text(), "%x")
        start = start + timedelta(seconds = 660 * 60) #660 min son 11 horas
        day = start.day
        month = start.month
        year = start.year
        startDate = str(year) +"-"+ str(month) +"-"+ str(day) + "T11:00"
        end = start + timedelta(seconds = int(self.duration.get_text()) * 60)
        endDate = end.strftime("%Y-%m-%dT%H:%M")
        category = self.category.get_active_text()
        description = self.description.get_text().strip()
        return startDate, endDate, category, description

    def get_id(self, data):
    	return data[0]

    def calc_min(self, data, posStartDate, posEndDate):
    	date = datetime.datetime.strptime(data[posStartDate], "%Y-%m-%dT%H:%M")
    	duration = datetime.datetime.strptime(data[posEndDate], "%Y-%m-%dT%H:%M")
    	hourEnd = duration.hour
    	hToMin = hourEnd * 60
    	minuteEnd = duration.minute
    	totalEnd = hToMin +minuteEnd
    	hourStart = date.hour
    	hToM = hourStart * 60
    	minuteStart = date.minute
    	totalStart = hToM +minuteStart
    	dur = totalEnd - totalStart
    	return dur

    def run_edit(self, data):
        dateStart = data[1][0:10]
        self.date.set_text(dateStart)
        self.duration.set_text(data[2])
        self.category.append_text(data[3])
        self.description.set_text(data[4])

        sensitive = self.get_selection() is not None
        self.modify.set_sensitive(sensitive)
        self.update.set_sensitive(False)

    def add_act_list(self, data, idEntry):
        data = list(data)
        data.insert(0, idEntry)
        dur = self.calc_min(data, 1, 2)
        data[2] = str(dur)
        date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M")
        dateStart = date.strftime("%x")
        data[1] = dateStart
        self.store.append(data)

    def add_act_list_thread(self, data, idEntry):
        GLib.idle_add(self.add_act_list, data, idEntry)

    def remove_act_list(self, data):
    	self.store.remove(data)

    def remove_act_list_thread(self, data):
        GLib.idle_add(self.remove_act_list, data)

    def modify_act_list(self, treeiter, data):
        data = list(data)
        dur = self.calc_min(data, 0, 1)
        data[1] = str(dur)
        date = datetime.datetime.strptime(data[0], "%Y-%m-%dT%H:%M")
        dateStart = date.strftime("%x")
        data[0] = dateStart
        self.store.set(treeiter, list(range(1,5)), data)

    def modify_act_list_thread(self, treeiter, data):
        GLib.idle_add(self.modify_act_list, treeiter, data)

    def show_in_local_store(self, store):
        self.store.clear()
        for row in store:
            category = row['category']
            description = row['description']
            endDate = row['end_date']
            idEntry = row['id']
            startDate = row['start_date']
            storeAux = [idEntry, startDate, endDate, category, description]
            dur = self.calc_min(storeAux, 1, 2)
            storeAux[2] = str(dur)
            date = datetime.datetime.strptime(storeAux[1], "%Y-%m-%dT%H:%M")
            dateStart = date.strftime("%x")
            storeAux[1] = dateStart
            self.store.append(storeAux)

    def show_in_local_store_thread(self, store):
        GLib.idle_add(self.show_in_local_store, store)

    def entries_by_month(self, store):
        self.calendar.clear_marks()
        for row in store:
        	category = row['category']
        	description = row['description']
        	endDate = row['end_date']
        	idEntry = row['id']
        	startDate = row['start_date']
        	storeAux = [idEntry, startDate, endDate, category, description]
        	dates = datetime.datetime.strptime(storeAux[1], "%Y-%m-%dT%H:%M")
        	self.calendar.mark_day(dates.day)
        self.calendar.select_month(dates.month-1, dates.year)

    def entries_by_month_thread(self, store):
        GLib.idle_add(self.entries_by_month, store)

    def get_selection(self):
        model, filteriter = self.entries.get_selection().get_selected()
        if filteriter == None:
        	return None
        treeiter = model.convert_iter_to_child_iter(filteriter)
        return (model.get_model()[treeiter][0], model.get_model()[treeiter][1], model.get_model()[treeiter][2], model.get_model()[treeiter][3], model.get_model()[treeiter][4])        

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
           
    def get_date_filter(self):
        dialog = Gtk.Dialog("", self.win, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dialog.get_content_area()
        calendar = Gtk.Calendar()
        grid = Gtk.Grid(margin=20, column_spacing=10, row_spacing=10)
        grid.attach(calendar, 0, 0, 1, 1)
        box.pack_start(grid, True, True, 0)
        box.show_all()
        response = dialog.run()
        aDate, mDate, dDate  = calendar.get_date()
        mDate = mDate+1        
        if response == Gtk.ResponseType.OK:
            result =  str(aDate) + "-" + str(mDate) + "-" + str(dDate) + "T00:00"            
        else:
            result = None
        dialog.destroy()
        return result

    def get_month(self):
        	dialog = Gtk.Dialog("", self.win, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        	box = dialog.get_content_area()
        	grid = Gtk.Grid(margin=20, column_spacing=10, row_spacing=10)
        	month_store = Gtk.ListStore(str)
        	month_store.append([_("01")])
        	month_store.append([_("02")])
        	month_store.append([_("03")])
        	month_store.append([_("04")])
        	month_store.append([_("05")])
        	month_store.append([_("06")])
        	month_store.append([_("07")])
        	month_store.append([_("08")])
        	month_store.append([_("09")])
        	month_store.append([_("10")])
        	month_store.append([_("11")])
        	month_store.append([_("12")])
        	month = Gtk.ComboBoxText(model=month_store, entry_text_column=0, active=0)
        	year = Gtk.Entry()
        	grid.attach(Gtk.Label(_("Mes: ")), 0, 0, 1, 1)
        	grid.attach(month, 1, 0, 1, 1)
        	grid.attach(Gtk.Label(_("Año")), 0, 1, 1, 1)
        	grid.attach(year, 1, 1, 1, 1)
        	box.pack_start(grid, True, True, 0)
        	box.show_all()
        	response = dialog.run()      
        	if response == Gtk.ResponseType.OK:
        		result = year.get_text().strip() + "-" + month.get_active_text() + "-" + "01T00:00"        
        	else:
        		result = None
        	dialog.destroy()
        	return result

    def show_error(self, code):
        	dialog = Gtk.Dialog("", self.win, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        	box = dialog.get_content_area()
        	grid = Gtk.Grid(margin=20, column_spacing=10, row_spacing=10)
        	if code == 400:
        		error = Gtk.Label(label = "Incorrect Params")
        	elif code == 500:
        		error =  Gtk.Label(label = "Entry could not be inserted")
        	elif code == 404:
        		error =  Gtk.Label(label = "Entry not found")
        	grid.attach(Gtk.Label(_("Error: ")), 0, 0, 1, 1)
        	grid.attach(error, 1, 0, 1, 1)
        	box.pack_start(grid, True, True, 0)
        	box.show_all()
        	response = dialog.run()      
        	dialog.destroy()

if __name__ == '__main__':
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	APP = "ipm-p1-server"
	locale.setlocale(locale.LC_ALL, '')
	LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
	locale.bindtextdomain(APP, LOCALE_DIR)
	gettext.bindtextdomain(APP, LOCALE_DIR)
	gettext.textdomain(APP)
	vc = ViewController()
	Gtk.main()