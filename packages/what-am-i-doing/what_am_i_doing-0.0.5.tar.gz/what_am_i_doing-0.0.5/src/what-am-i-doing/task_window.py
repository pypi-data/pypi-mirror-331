import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import conf
import utils
from utils import *

class TaskWindow(Gtk.Window):
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path("styles.css")
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    _instance = None

    def __init__(self,app,passed_data=None):

        if TaskWindow._instance:
        
            if TaskWindow._instance.taskEntry.get_text():
                # Present existing window if there is anything in task entry
                TaskWindow._instance.present()
                self = TaskWindow._instance
                self.show_all()
                return None

                
            TaskWindow._instance.destroy() # get rid of old window instance 
            # TaskWindow._instance.present()
            # return None

        TaskWindow._instance = self

        Gtk.Window.__init__(self, title="What Am I Doing?")

        self.search_cache = {}

        self.app = app
        session = app.session
        self.set_name("TaskWindow") # set css id

        self.fullscreen()
        self.get_style_context().add_class("large")

        # self.present() # try to focus the window
        # self.focus_force() # try to focus the window

        self.shown_tasks = {}
        
        self.set_border_width(20)
        self.set_position(position=1) # Works on x11 but not wayland (ubuntu 22.04)

        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        box = Gtk.VBox(spacing=10)
        box.set_halign(Gtk.Align.CENTER)
        # box.set_valign(Gtk.Align.CENTER)
        
        self.add(box)

        self.session_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15, border_width=10)

        # self.session_box.set_halign(Gtk.Align.CENTER)
        # box.add(self.session_box)
        box.pack_start(self.session_box,False, False, 0)


        # if self.app.is_running == "boo": #For testing
        if self.app.is_running == True: 

            self.session_label = Gtk.Button(label=session['label']+" "+sec_to_time(session['duration']) )
            # self.session_label.set_relief(Gtk.RELIEF_NONE)
            self.session_label.set_relief(Gtk.ReliefStyle.NONE)
            self.session_label.connect("clicked", self.app.open_session_options_dialog)
            self.session_label.set_property("tooltip-text", "Edit session")

            self.session_box.pack_start(self.session_label, False, False, 0)

            self.session_box.pack_start(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15, border_width=10),True, True, 0)

            pause_button = Gtk.Button()
            # pause_button.set_image(Gtk.Image.new_from_file(os.path.abspath('icon/pause.svg'))) 
            pause_button.set_image(Gtk.Image.new_from_file(os.path.abspath('icon/pause.png')))
            pause_button.connect("clicked", self.app.stop_task)
            pause_button.connect("clicked", self.session_box.hide)

            pause_button.connect("clicked", self.refresh_search_cache) 
            pause_button.set_property("tooltip-text", "Pause Task (Ctrl + P)")
            pause_button.set_relief(Gtk.ReliefStyle.NONE)
            self.session_box.add(pause_button)

            done_button = Gtk.Button()
            # done_button.set_image(Gtk.Image.new_from_file(os.path.abspath('icon/mark-done.svg')))
            done_button.set_image(Gtk.Image.new_from_file(os.path.abspath('icon/mark-done.png')))
            done_button.set_property("tooltip-text", "Mark Task Done (Ctrl + D)")
            done_button.connect("clicked", self.app.stop_task,'mark_done')
            done_button.connect("clicked", self.refresh_search_cache) 
            done_button.set_relief(Gtk.ReliefStyle.NONE)
            self.session_box.add(done_button)


            cancel_button = Gtk.Button()
            # cancel_button.set_image(Gtk.Image.new_from_file(os.path.abspath('icon/cancel.svg'))) 
            cancel_button.set_image(Gtk.Image.new_from_file(os.path.abspath('icon/cancel.png'))) 
            cancel_button.connect("clicked", self.app.stop_task,"cancel")
            cancel_button.set_property("tooltip-text", "Discard timer (Ctrl + X)")
            cancel_button.set_relief(Gtk.ReliefStyle.NONE)
            self.session_box.add(cancel_button)


            # self.notes_text_buffer = Gtk.TextBuffer()
            # if 'notes' in self.session:
            #     self.notes_text_buffer.set_text(session['notes'])
            # else:
            #     self.notes_text_buffer.set_text('\n\n') # hack to give it some height

            # self.notes = Gtk.TextView(buffer=self.notes_text_buffer)
            # box.add(self.notes)
                

            self.tick_timer = GLib.timeout_add_seconds(1, self.tick)

        else:
            # RelevantQuestion prompt
            print("show the question")
            # self.session_box.foreach(lambda child: child.destroy()) # for testing

            lines = conf.user['prompts'].split("\n")
            p = lines.pop(0)
            lines.append(p)
            conf.user['prompts'] = "\n".join(lines)
            self.the_question = Gtk.Label(p)
            self.the_question.set_name("RelevantQuestion")
            self.session_box.pack_start(self.the_question, True, True, 0)

                            
        # Large fuzzy task input 
        self.taskEntry = Gtk.Entry()
        self.taskEntry.set_name("FuzzyTask") # set css id
        self.taskEntry.set_width_chars(59)
        self.taskEntry.set_placeholder_text("Find Task [Ctrl+F], press Enter to start work on the first task in the list ")
        self.taskEntry.set_property("tooltip-text", "Find Task [Ctrl+F], press Enter to start work on the first task in the list")
        
        # box.add(self.taskEntry)
        box.pack_start(self.taskEntry,False, False, 0)

        self.taskEntry.grab_focus()

        if passed_data:
            dbg('taskwindow passed_data',passed_data,s='taskwindow')
            if 'afk_time' in passed_data:

                last_active_time = datetime.now() - timedelta(seconds=passed_data['afk_time'])
                # utc_last_active_time = datetime.now(timezone.utc) - timedelta(seconds=passed_data['afk_time'])

                last_active_str = time.strftime('%H:%M', last_active_time.timetuple())

                afk_label = Gtk.Label()
                afk_label.set_markup("<b>Inactive Since "+" "+str(last_active_str) +"</b>")
                self.session_box.add(afk_label)

                pause_then_button = Gtk.Button(label="Finish Then")

                pause_then_button.connect("clicked", self.pause_then, last_active_time)
                self.session_box.add(pause_then_button)

            if 'task' in passed_data:
                self.taskEntry.set_text(passed_data['task']['label'])
        

        # box.add(Gtk.Box(border_width=10)) # Spacer

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(self.scrolled_window, True, True, 0)
        # self.scrolled_window.set_size_request(-1, -1)
        self.scrolled_window.set_size_request(-1, 400)
        # self.scrolled_window.set_hexpand(True)
        # self.scrolled_window.set_vexpand(True)
        
        self.tasks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        self.tasks_box.set_halign(Gtk.Align.START)

        self.scrolled_window.add(self.tasks_box)

        self.total_duration_label = Gtk.Label()
        self.timesheet_to_button = Gtk.Button()
        self.timesheet_to_button.set_relief(Gtk.ReliefStyle.NONE)
        self.timesheet_to_button.add(self.total_duration_label)
        self.timesheet_to_button.connect("clicked",self.timesheet_to_clipboard)
        self.timesheet_to_button.set_name("Footer")
        self.timesheet_to_button.set_property("tooltip-text","Click to copy CSV timesheet to clipboard")
            # done_button.set_property("tooltip-text", "Mark Task Done (Ctrl + D)")



        box.pack_start(self.timesheet_to_button,False, False, 0)

        self.buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.buttons_box.set_halign(Gtk.Align.CENTER)
        self.buttons_box.set_name("Footer")


        # box.add(Gtk.Box(border_width=10)) # Spacer

        # box.add(self.buttons_box)
        box.pack_start(self.buttons_box,False, False, 0)

        self.settings_button = Gtk.Button(label="Settings")
        self.settings_button.connect("clicked",self.app.open_settings_window)
        self.buttons_box.add(self.settings_button)

        self.refresh_button = Gtk.Button(label="Refresh")
        self.refresh_button.set_property("tooltip-text","Reload all todolists (Ctrl + R)")
        self.refresh_button.connect("clicked",self.app.async_refresh)
        self.buttons_box.add(self.refresh_button)

        # Todolist openables
        openables = []
        for id, todolist in conf.user['todolists'].items():
            if todolist['status']:
                openable = get_connector_openable(None, todolist,False)
                if openable not in openables:            
                    openables.append(openable)
                    # TODO: encode label
                    openable_button = Gtk.Button(label=GLib.markup_escape_text(todolist['label']))
                    openable_button.connect("clicked", get_connector_openable, todolist)
                    openable_button.set_property("tooltip-text","Open "+GLib.markup_escape_text(todolist['label']))
                    self.buttons_box.add(openable_button)
            

        self.new_task_button = Gtk.Button(label="New Task")
        self.new_task_button.set_property("tooltip-text","Add a new task to an existing list (Ctrl + N)")
        self.new_task_button.connect("clicked",self.open_new_task_dialog)
        self.buttons_box.add(self.new_task_button)


        key, mod = Gtk.accelerator_parse('<Control>n')
        self.new_task_button.add_accelerator("clicked", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)

        key, mod = Gtk.accelerator_parse('<Control>r')
        self.refresh_button.add_accelerator("clicked", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)        
        
        # key, mod = Gtk.accelerator_parse('<Control>l')
        # self.taskEntry.add_accelerator("clicked", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        # dbg('new_task_button accel','key',key, 'mod',mod,s='taskwindow',l=2)

        if self.app.is_running == True: 

            key, mod = Gtk.accelerator_parse('<Control>p')
            pause_button.add_accelerator("clicked", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)

            key, mod = Gtk.accelerator_parse('<Control>x')
            cancel_button.add_accelerator("clicked", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)

            key, mod = Gtk.accelerator_parse('<Control>d')
            done_button.add_accelerator("clicked", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)


        self.connect("key-press-event", self.on_win_key_press_event)
        self.connect("window-state-event", self.on_window_state_event)

        self.taskEntry.connect("changed",self.task_search)
        
        self.refresh_search_cache()

        self.show_all()


    def refresh_search_cache(self,w = None):
        self.search_cache = {}
        # self.default_tasks = {}
        # self.default_tasks = utils.get_priority_tasks(50) | utils.get_recent_tasks(30)

        self.task_search(self.taskEntry)
        

    def open_new_task_dialog(self,w = None):
        passed_data = {"label":self.taskEntry.get_text()}
        self.app.open_new_task_dialog(self, passed_data)
    

    def tick(self):

        if(self.app.is_running == True):
            self.session_label.set_label(self.app.session['label'] + ": " + sec_to_time(self.app.session['duration']))
            self.session_label.show()
            return True
        else:
            self.session_box.hide()
            return False


    def pause_then(self, widget = None, utc_last_active_time = None):
        self.app.stop_task(None,"save",utc_last_active_time)
        self.session_box.destroy()
        self.refresh_search_cache()


    def task_search(self,widget):

        self.tasks_box.foreach(lambda child: child.destroy()) 
        self.tasks_box.show_all()

        self.shown_tasks.clear()

        i = widget.get_text()

        # TODO: add "default time tracking range" to settings then add " WHERE sessions.start_time > conf.get_default_tracking_range_as_time('sql')" 

        utils.dbg({"task search":i},s='taskwindow')

        
        # if len(i) == 0 and self.default_tasks:
        #     tasks = self.default_tasks        
        
        if i in self.search_cache:
            tasks = self.search_cache[i]

        else:
            params = None
            conditions = ''
            limit = '5000'

            print("search len",len(i))

            if len(i) == 0:
                # Set default_tasks
                limit = '500'

                # TODO: figgure out how to insure that all time_target tasks are selected?
                # Probably with an if/select in the order by block (Which )
                # tt_task_ids = list(conf.user['time_targets']['tasks'].keys())
                # tt_list_ids = list(conf.user['time_targets']['lists'].keys())
                
                conditions = ' AND status = 1 '
                
            elif  i == '*':
                limit = "5000"

            elif len(i) < 4:
                #  look ahead, if less than 4 chars
                conditions = " AND (label like ? OR parent_label like ? OR extended_label like ? ) "
                params = (i+'%',i+'%',i+'%',)

                print("lookahead search")

            else:
                conditions = " AND extended_label like ? "
                params = ('%'+i+'%',)

            # NOTE: Can't use "AND status >= 0" because, for some reason, some (Most?) completed asks are status NULL, also status != '-1' omits NULL (completed) row (because NULL is never 'equal' OR 'not equal' to anything)

            timeframe = hours_search_timeframes(conf.user['hours_search_timeframe'])

            timeframe_sql = " sessions.start_time > '"+timeframe[0].strftime("%Y-%m-%d %H:%M:%S")+"' AND sessions.start_time < '"+timeframe[1].strftime("%Y-%m-%d %H:%M:%S")+"' " 

            
            data = utils.db_query("SELECT tasks.*, SUM(sessions.duration) as duration FROM tasks LEFT JOIN (SELECT duration, start_time, task_id FROM sessions WHERE "+timeframe_sql+") as sessions ON sessions.task_id = tasks.id WHERE tasks.status IS NOT '-1' "+str(conditions)+"  GROUP BY tasks.id ORDER BY tasks.status DESC, tasks.priority DESC, MAX(sessions.start_time) DESC, tasks.extended_label ASC LIMIT  "+str(limit)+"",params)

            non_priority_tasks = {}
            priority_tasks = {}

            for row in data:
                t = proc_db_item(row)
                # Handle non-db prioritization 
                if t['priority'] > 0 and t['status']:
                    priority_tasks[t['id']] = t
                else:
                    non_priority_tasks[t['id']] = t
            tasks = priority_tasks | non_priority_tasks

            # cache default_tasks 
            # if len(i) == 0:
            #     self.default_tasks = tasks 
            # else:
            self.search_cache[i] = tasks


            # self.new_task_button.show()

        utils.dbg('task_window search tasks',tasks,s='taskwindow',l=3)

        total_duration = 0

        for id, t in tasks.items():
            self.add_task_to_list(t,GLib.markup_escape_text(i))
            if 'duration' in t and t['duration']:
                total_duration += int(t['duration'])

        if total_duration:
            self.total_duration_label.set_markup('<b>'+str(round(total_duration / 60 / 60,3))+'</b> hours '+conf.user['hours_search_timeframe'] )

        else:
            self.total_duration_label.set_markup('')

        self.tasks_box.show_all()
        # TODO: Show 


    def add_task_to_list(self,t,search_str = None):

        try:
            utils.dbg("add_task_to_list "+ str(t['label']), "status",t['status'], s='taskwindow',l=3)

            self.shown_tasks[t['id']] = Gtk.Button()
            self.shown_tasks[t['id']].set_halign(Gtk.Align.START)
            self.shown_tasks[t['id']].set_hexpand(True)

            label = Gtk.Label()

            # self.shown_tasks[t['id']].set_label(label)
            # button_context = self.shown_tasks[t['id']].get_style_context().add_class("large")
            extended_label = GLib.markup_escape_text(t['extended_label'])
            
            if search_str:
                extended_label = extended_label.replace(search_str,"<b>"+search_str+"</b>")
                extended_label = extended_label.replace(search_str.capitalize(),"<b>"+search_str.capitalize()+"</b>") # Cheesy
            if "duration" in t and t['duration']:
                extended_label += " ("+sec_to_time(t['duration'])+")"

            if not t['status']:
                utils.dbg("add strikethrough to done task "+t['label'],l=3,s="taskwindow")
                # button_context.add_class("done")
                label.set_markup('<s>'+extended_label+'</s>')

            elif t['label'] == self.taskEntry.get_text() or t['priority'] > 0:
                # button_context.add_class("bold")
                label.set_markup('<b>'+extended_label+'</b>')
            else:
                label.set_markup(extended_label)

            self.shown_tasks[t['id']].add(label)

            # self.shown_tasks[t['id']].set_size_request(955, -1)
            self.shown_tasks[t['id']].connect("clicked", self.select_task,None,t)
            self.shown_tasks[t['id']].connect("button-release-event", self.select_task,t)
            self.shown_tasks[t['id']].set_relief(Gtk.ReliefStyle.NONE)
            self.tasks_box.add(self.shown_tasks[t['id']])
            # self.shown_tasks[t['id']].show() # This doesn't work
            self.tasks_box.show_all()


        except Exception as e:
            utils.dbg("Error adding task to list"+ str(t['label']), t, e, l=0, s='taskwindow')


    def select_task(self,widget,event=None,t=None):
        print('event',event)
        if event:  # Right-click (button 3)
            if event.button == 3:  # Right-click (button 3)
                # error_notice("Thank you for right clicking!", "Watch this space for exciting new features!")
                # TODO: Context menu with: Modify session to this task, mark_done, start, edit?, and get_times? (from time tracker)

                try:
                    c = conf.user['todolists'][t['todolist']]
                    conf.todo_connectors[c['type']].open(c,t,'task')
                    return
                except Exception as e:
                    error_notice('Bonk', "error with "+ c['type']+ " open function ")


        self.app.start_task(None,t) 
        self.destroy()


    def timesheet_to_clipboard(self,widget = None):

        search_term = self.taskEntry.get_text()
        tasks = self.search_cache[search_term]

        print("timesheet for "+search_term, len(tasks))
        dbg("timesheet for "+search_term, len(tasks),l=1,s='taskwindow')


        o = '"Project","Task","Hours"\n'  
        total_hours = 0

        for t_id, t in tasks.items():
            if t['duration']:
                rounded_hours = round(force_number(t['duration']) / 60 / 60, 3)
                total_hours += rounded_hours

                o +=  '"'+str(t['parent_label'])+'","'+str(t['label'])+'","'+str(rounded_hours)+'"\n'
        

        o +=  ", Total,"+str(total_hours)+"\n"

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(o, -1)
        clipboard.store()
        error_notice("Timesheet for '"+search_term+"' copied to clipboard")


    def toggle_fullscreen(self):

        if self.__is_fullscreen:
            self.unfullscreen()
            self.get_style_context().remove_class("large")

        else:
            self.fullscreen()
            self.get_style_context().add_class("large")


    def on_win_key_press_event(self, widget, ev):

        key = Gdk.keyval_name(ev.keyval)
        utils.dbg("task window key",key,s="taskwindow",l=3)
        # utils.dbg("key_press_event",ev,s="taskwindow",l=1)
        utils.dbg("ModifierType is CONTROL_MASK",Gdk.ModifierType.CONTROL_MASK,s="taskwindow",l=1)
        

        if key == "F11":
            self.toggle_fullscreen()
        elif key == "Escape":
            self.destroy()
        elif key in ['l','f'] and Gdk.ModifierType.CONTROL_MASK:
            self.taskEntry.grab_focus()

        elif key == "Return" and self.taskEntry.is_focus():
            # print("self.taskEntry has focus, do the thing")
            if self.shown_tasks:
                self.tasks_box.get_children()[0].emit('clicked')
            else:
                self.new_task_button.emit('clicked')


    def on_window_state_event(self, widget, ev):
        self.__is_fullscreen = bool(ev.new_window_state & Gdk.WindowState.FULLSCREEN)

