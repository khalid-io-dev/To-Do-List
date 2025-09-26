import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql

# ---------- CONFIG ----------
MYSQL_USER = "root"
MYSQL_PASSWORD = ""    
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
DB_NAME = "todo_db"

CONN_URL_DB = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}?charset=utf8mb4"
CONN_URL_SERVER = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/?charset=utf8mb4"

# Color Scheme
COLORS = {
    'bg_main': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_card': '#0f3460',
    'accent': '#e94560',
    'text_primary': '#ffffff',
    'text_secondary': '#b3b3b3',
    'priority_high': '#ff4757',
    'priority_medium': '#ffa502',
    'priority_low': '#2ed573',
    'column_todo': '#3742fa',
    'column_doing': '#ffa502',
    'column_done': '#2ed573',
    'hover': '#2f3542',
    'delete_btn': '#e74c3c',
    'delete_btn_hover': '#c0392b'
}

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    description = sa.Column(sa.String(1024), nullable=False)
    status = sa.Column(sa.String(20), default='todo')  
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

def ensure_database_exists():
    try:
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        conn.commit()
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Cannot create/access MySQL database: {e}")

def init_db():
    ensure_database_exists()
    engine = sa.create_engine(CONN_URL_DB, echo=False, future=True)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(sa.text("SHOW COLUMNS FROM tasks LIKE 'status'"))
            if not result.fetchone():
                conn.execute(sa.text("ALTER TABLE tasks ADD COLUMN status VARCHAR(20) DEFAULT 'todo'"))
                conn.execute(sa.text("UPDATE tasks SET status = 'done' WHERE done = 1"))
                conn.execute(sa.text("UPDATE tasks SET status = 'todo' WHERE done = 0"))
                conn.commit()
    except:
        pass  
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

class TaskCard(tk.Frame):
    def __init__(self, parent, task, app):
        super().__init__(parent, bg=COLORS['bg_card'], relief='flat', bd=0)
        self.task = task
        self.app = app
        self.pack(fill='x', padx=5, pady=6)  
        
        self.configure(cursor='hand2')
        
        main_frame = tk.Frame(self, bg=COLORS['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=12, pady=12)
        
        status_map = {'todo': 'TO-DO', 'doing': 'DOING', 'done': 'DONE'}
        status_color_map = {'todo': COLORS['column_todo'], 'doing': COLORS['column_doing'], 'done': COLORS['column_done']}
        
        status_frame = tk.Frame(main_frame, bg=COLORS['bg_card'])
        status_frame.pack(fill='x', pady=(0, 4))
        
        status_label = tk.Label(status_frame, text=status_map[self.task.status],
                               fg=status_color_map[self.task.status], bg=COLORS['bg_card'],
                               font=('Segoe UI', 8, 'bold'))
        status_label.pack(side='left')
        
        id_label = tk.Label(status_frame, text=f'#{self.task.id}',
                           fg=COLORS['text_secondary'], bg=COLORS['bg_card'],
                           font=('Segoe UI', 8))
        id_label.pack(side='right')
        
        desc_label = tk.Label(main_frame, text=task.description,
                             fg=COLORS['text_primary'], bg=COLORS['bg_card'],
                             font=('Segoe UI', 12), wraplength=400, justify='left')  # Increased wraplength for wider text area
        desc_label.pack(fill='x', pady=(0, 4))
        
        bottom_frame = tk.Frame(main_frame, bg=COLORS['bg_card'])
        bottom_frame.pack(fill='x')
        
        date_str = task.created_at.strftime('%m/%d %H:%M')
        date_label = tk.Label(bottom_frame, text=date_str,
                             fg=COLORS['text_secondary'], bg=COLORS['bg_card'],
                             font=('Segoe UI', 9))
        date_label.pack(side='left')
        
        delete_btn = tk.Button(bottom_frame, text='🗑', command=self.delete_task,
                              bg=COLORS['delete_btn'], fg='white',
                              font=('Segoe UI', 8), bd=0, width=3,
                              cursor='hand2', relief='flat')
        delete_btn.pack(side='right')
        
        def on_delete_hover(event, hover_color=COLORS['delete_btn_hover']):
            delete_btn.configure(bg=hover_color)
        def on_delete_leave(event):
            delete_btn.configure(bg=COLORS['delete_btn'])
        
        delete_btn.bind('<Enter>', on_delete_hover)
        delete_btn.bind('<Leave>', on_delete_leave)
        
        self.bind_drag_events()
        
    def bind_drag_events(self):
        widgets = [self] + list(self.winfo_children()) + [child for frame in self.winfo_children() 
                                                         if isinstance(frame, tk.Frame) 
                                                         for child in frame.winfo_children()]
        
        for widget in widgets:
            if not isinstance(widget, tk.Button):  
                widget.bind('<Button-1>', self.on_click)
                widget.bind('<B1-Motion>', self.on_drag)
                widget.bind('<ButtonRelease-1>', self.on_drop)
            widget.bind('<Enter>', self.on_hover)
            widget.bind('<Leave>', self.on_leave)
    
    def on_hover(self, event):
        self.configure(bg=COLORS['hover'])
        for child in self.winfo_children():
            child.configure(bg=COLORS['hover'])
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if not isinstance(grandchild, tk.Button):  
                        grandchild.configure(bg=COLORS['hover'])
    
    def on_leave(self, event):
        self.configure(bg=COLORS['bg_card'])
        for child in self.winfo_children():
            child.configure(bg=COLORS['bg_card'])
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if not isinstance(grandchild, tk.Button):  
                        grandchild.configure(bg=COLORS['bg_card'])
    
    def on_click(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.lift()
        
    def on_drag(self, event):
        x = self.winfo_x() + (event.x_root - self.start_x)
        y = self.winfo_y() + (event.y_root - self.start_y)
        self.place(x=x, y=y)
        
    def on_drop(self, event):
        root_x = event.x_root
        target_column = None
        
        for col_name, column in self.app.columns.items():
            col_x = column.winfo_rootx()
            col_width = column.winfo_width()
            if col_x <= root_x <= col_x + col_width:
                target_column = col_name
                break
        
        if target_column and target_column != self.task.status:
            self.app.move_task(self.task.id, target_column)
        
        self.pack(fill='x', padx=5, pady=6)
    
    def delete_task(self):
        if messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete task #{self.task.id}?'):
            self.app.delete_task(self.task.id)

class KanbanColumn(tk.Frame):
    def __init__(self, parent, title, color, status):
        super().__init__(parent, bg=COLORS['bg_secondary'], relief='flat', bd=0)
        self.status = status
        self.tasks = []
        
        header = tk.Frame(self, bg=color, height=60)
        header.pack(fill='x', padx=2, pady=(2, 0))
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title, fg=COLORS['text_primary'],
                              bg=color, font=('Segoe UI', 14, 'bold'))
        title_label.pack(expand=True)
        
        self.count_label = tk.Label(header, text='0', fg=COLORS['text_primary'],
                                   bg=color, font=('Segoe UI', 10))
        self.count_label.pack(side='bottom', pady=(0, 8))
        
        self.canvas = tk.Canvas(self, bg=COLORS['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['bg_secondary'])
        
        self.scrollable_frame.bind('<Configure>', 
                                  lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True, padx=(2, 0), pady=(0, 2))
        scrollbar.pack(side='right', fill='y', padx=(0, 2), pady=(0, 2))
        
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        
    def add_task_card(self, task, app):
        card = TaskCard(self.scrollable_frame, task, app)
        self.tasks.append(card)
        self.update_count()
        
    def clear_tasks(self):
        for card in self.tasks:
            card.destroy()
        self.tasks = []
        self.update_count()
        
    def update_count(self):
        self.count_label.configure(text=str(len(self.tasks)))

class TodoApp(tk.Tk):
    def __init__(self, Session):
        super().__init__()
        self.title('To-Do List')
        self.geometry('1400x800')
        self.configure(bg=COLORS['bg_main'])
        self.session_factory = Session
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self.setup_ui()
        self.refresh_tasks()
        
    def setup_ui(self):
        header = tk.Frame(self, bg=COLORS['accent'], height=80)
        header.grid(row=0, column=0, columnspan=3, sticky='ew', padx=8, pady=(8, 0))
        header.grid_propagate(False)
        
        title_label = tk.Label(header, text='To-Do List',
                              fg=COLORS['text_primary'], bg=COLORS['accent'],
                              font=('Segoe UI', 20, 'bold'))
        title_label.pack(side='left', padx=20, pady=20)
        
        btn_frame = tk.Frame(header, bg=COLORS['accent'])
        btn_frame.pack(side='right', padx=20, pady=10)
        
        add_btn = tk.Button(btn_frame, text='+ Add Task', command=self.add_task,
                           bg=COLORS['bg_main'], fg=COLORS['text_primary'],
                           font=('Segoe UI', 11, 'bold'), bd=0, padx=16, pady=8,
                           cursor='hand2', relief='flat')
        add_btn.pack(side='left', padx=(0, 8))
        
        refresh_btn = tk.Button(btn_frame, text='🔄 Refresh', command=self.refresh_tasks,
                               bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
                               font=('Segoe UI', 11), bd=0, padx=16, pady=8,
                               cursor='hand2', relief='flat')
        refresh_btn.pack(side='left')
        
        self.columns = {}
        
        # To-Do Column
        self.columns['todo'] = KanbanColumn(self, 'TO-DO', COLORS['column_todo'], 'todo')
        self.columns['todo'].grid(row=1, column=0, sticky='nsew', padx=(8, 4), pady=8)
        
        # Doing Column
        self.columns['doing'] = KanbanColumn(self, 'DOING', COLORS['column_doing'], 'doing')
        self.columns['doing'].grid(row=1, column=1, sticky='nsew', padx=4, pady=8)
        
        # Done Column
        self.columns['done'] = KanbanColumn(self, 'DONE', COLORS['column_done'], 'done')
        self.columns['done'].grid(row=1, column=2, sticky='nsew', padx=(4, 8), pady=8)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set('Ready')
        status_bar = tk.Label(self, textvariable=self.status_var,
                             bg=COLORS['bg_secondary'], fg=COLORS['text_secondary'],
                             font=('Segoe UI', 9), anchor='w', padx=10)
        status_bar.grid(row=2, column=0, columnspan=3, sticky='ew', padx=8, pady=(0, 8))
        
    def add_task(self):
        task_dialog = tk.Toplevel(self)
        task_dialog.title('Create New Task')
        task_dialog.geometry('600x450')
        task_dialog.configure(bg='#f8f9fa')
        task_dialog.resizable(False, False)
        
        task_dialog.transient(self)
        task_dialog.grab_set()
        
        selected_status = tk.StringVar(value='todo')
        
        header_frame = tk.Frame(task_dialog, bg='#4a90e2', height=70)
        header_frame.pack(fill='x', pady=(0, 25))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text='📝 Create New Task',
                fg='white', bg='#4a90e2',
                font=('Segoe UI', 18, 'bold')).pack(expand=True)
        
        content_frame = tk.Frame(task_dialog, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, padx=35)
        
        tk.Label(content_frame, text='Task Description:',
                fg='#2c3e50', bg='#f8f9fa',
                font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 8))
        
        desc_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        desc_frame.pack(fill='x', pady=(0, 25))
        
        desc_text = tk.Text(desc_frame, height=6, font=('Segoe UI', 11),
                           bg='white', fg='#2c3e50',
                           relief='flat', bd=12, wrap='word',
                           insertbackground='#4a90e2')
        desc_text.pack(fill='both', expand=True)
        
        status_frame = tk.LabelFrame(content_frame, text=' Initial Status ',
                                    fg='#2c3e50', bg='#f8f9fa',
                                    font=('Segoe UI', 11, 'bold'), bd=1,
                                    relief='solid')
        status_frame.pack(fill='x', pady=(0, 25))
        
        status_inner = tk.Frame(status_frame, bg='#f8f9fa')
        status_inner.pack(fill='x', padx=15, pady=10)
        
        statuses = [('todo', '📋 To-Do', '#3742fa'),
                   ('doing', '⚡ Doing', '#ffa502'),
                   ('done', '✅ Done', '#2ed573')]
        
        def update_status(value):
            selected_status.set(value)
        
        for value, text, color in statuses:
            cb_frame = tk.Frame(status_inner, bg='#f8f9fa')
            cb_frame.pack(fill='x', pady=4)
            
            cb = tk.Radiobutton(cb_frame, text=text,
                               variable=selected_status, value=value,
                               fg=color, bg='#f8f9fa',
                               selectcolor='white',
                               font=('Segoe UI', 11, 'bold'), anchor='w',
                               activebackground='#f8f9fa',
                               activeforeground=color,
                               command=lambda v=value: update_status(v))
            cb.pack(side='left')
        
        # Buttons
        btn_frame = tk.Frame(task_dialog, bg='#f8f9fa')
        btn_frame.pack(pady=25)
        
        def create_task():
            description = desc_text.get('1.0', 'end-1c').strip()
            if not description:
                messagebox.showwarning('Warning', 'Please enter a task description!')
                return
            
            task_dialog.destroy()
            self._create_task(description, selected_status.get())
        
        ok_btn = tk.Button(btn_frame, text='✓ OK', command=create_task,
                          bg='#27ae60', fg='white',
                          font=('Segoe UI', 12, 'bold'), bd=0, padx=30, pady=12,
                          cursor='hand2', relief='flat')
        ok_btn.pack(side='left', padx=8)
        
        cancel_btn = tk.Button(btn_frame, text='✕ Cancel', command=task_dialog.destroy,
                              bg='#e74c3c', fg='white',
                              font=('Segoe UI', 12, 'bold'), bd=0, padx=25, pady=12,
                              cursor='hand2', relief='flat')
        cancel_btn.pack(side='left', padx=8)
        
        def on_hover(btn, hover_color):
            def enter(e):
                btn.configure(bg=hover_color)
            def leave(e):
                original_colors = {'#219a52': '#27ae60', '#c0392b': '#e74c3c'}
                btn.configure(bg=original_colors.get(hover_color, btn.cget('bg')))
            return enter, leave
        
        ok_enter, ok_leave = on_hover(ok_btn, '#219a52')
        ok_btn.bind('<Enter>', ok_enter)
        ok_btn.bind('<Leave>', ok_leave)
        
        cancel_enter, cancel_leave = on_hover(cancel_btn, '#c0392b')
        cancel_btn.bind('<Enter>', cancel_enter)
        cancel_btn.bind('<Leave>', cancel_leave)
        
        task_dialog.bind('<Return>', lambda event: create_task())
        
        desc_text.focus_set()
        
    def _create_task(self, description, status):
        session = self.session_factory()
        try:
            task = Task(description=description, status=status)
            session.add(task)
            session.commit()
            status_text = {'todo': 'TO-DO', 'doing': 'DOING', 'done': 'DONE'}[status]
            self.status_var.set(f'Task created in {status_text}: {description[:30]}...' if len(description) > 30 else f'Task created in {status_text}: {description}')
            self.refresh_tasks()
        except Exception as e:
            session.rollback()
            messagebox.showerror('Error', f'Failed to create task: {e}')
        finally:
            session.close()
            
    def move_task(self, task_id, new_status):
        session = self.session_factory()
        try:
            task = session.get(Task, task_id)
            if task:
                old_status = task.status
                task.status = new_status
                session.commit()
                self.status_var.set(f'Moved task #{task_id} from {old_status.upper()} to {new_status.upper()}')
                self.refresh_tasks()
            else:
                messagebox.showerror('Error', 'Task not found')
        except Exception as e:
            session.rollback()
            messagebox.showerror('Error', f'Failed to move task: {e}')
        finally:
            session.close()
            
    def delete_task(self, task_id):
        session = self.session_factory()
        try:
            task = session.get(Task, task_id)
            if task:
                session.delete(task)
                session.commit()
                self.status_var.set(f'Deleted task #{task_id}')
                self.refresh_tasks()
            else:
                messagebox.showerror('Error', 'Task not found')
        except Exception as e:
            session.rollback()
            messagebox.showerror('Error', f'Failed to delete task: {e}')
        finally:
            session.close()
            
    def refresh_tasks(self):
        for column in self.columns.values():
            column.clear_tasks()
            
        session = self.session_factory()
        try:
            tasks = session.query(Task).order_by(Task.created_at).all()
            
            for task in tasks:
                if task.status in self.columns:
                    self.columns[task.status].add_task_card(task, self)
                    
            total_tasks = len(tasks)
            self.status_var.set(f'Loaded {total_tasks} tasks')
            
        except Exception as e:
            messagebox.showerror('Database Error', f'Failed to load tasks: {e}')
        finally:
            session.close()

def main():
    try:
        Session = init_db()
    except Exception as e:
        messagebox.showerror('Database Error', f'Failed to initialize database:\n{e}')
        return
        
    app = TodoApp(Session)
    
    def on_btn_hover(btn, hover_color):
        def enter(e):
            btn.configure(bg=hover_color)
        def leave(e):
            btn.configure(bg=btn.original_color)
        return enter, leave
    
    app.mainloop()

if __name__ == '__main__':
    main()