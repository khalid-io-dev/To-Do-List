# 📝 To-Do List Application  

## 📌 Project Overview  
This project is a simple **Task Management (To-Do List) application** built with **Python** and **Tkinter** for the graphical user interface.  
Tasks are stored in a **MySQL** or **PostgreSQL** database using **SQLAlchemy ORM**, ensuring persistence across sessions.  

The application allows users to add, view, delete, and mark tasks as completed, with a minimal and intuitive interface.  

---

## 🕒 Duration  
This project is designed to be completed within **2 days**.  

---

## ✨ Features  
- ✅ **Add Tasks**: Users can create new tasks with a description.  
- 📋 **View Tasks**: Displays all tasks in a list, showing:  
  - Task ID  
  - Description  
  - Priority  
  - Status (In Progress / Completed)  
- ❌ **Delete Tasks**: Users can remove tasks from the list.  
- ✔️ **Mark as Completed**: Update the status of a selected task.  
- 💾 **Persistent Storage**: Tasks are stored in a relational database via **SQLAlchemy ORM**.  
- 🖥️ **User Interface**: Clean and simple UI using **Tkinter**.  

---

## 🛠️ Technologies Used  
- **Python 3**  
- **Tkinter** (GUI)  
- **SQLAlchemy ORM** (Database interaction)  
- **MySQL** or **PostgreSQL** (Relational database)  

---

## ⚙️ Setup Instructions  

### 1. Clone the Repository  
```bash
git clone https://github.com/yourusername/todo-list-tkinter.git
cd todo-list-tkinter


### 2. Install Dependencies

Make sure you have Python 3 installed, then install the required libraries:

pip install sqlalchemy psycopg2 mysqlclient

### 3. Database Setup

You can use either MySQL or PostgreSQL.

Example connection URL formats:

## PostgreSQL

postgresql+psycopg2://username:password@localhost/todo_db


## MySQL

mysql+mysqlclient://username:password@localhost/todo_db


The application will automatically create the tasks table if it does not exist.

### 4. Run the Application
python app.py

📦 Example SQLAlchemy Model
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    priority = Column(String, default='Normal')
    status = Column(String, default='In Progress')
