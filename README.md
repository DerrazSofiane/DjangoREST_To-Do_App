# Introduction

[![Build Status](https://travis-ci.com/DerrazSofiane/DjangoREST_To-Do_App.svg??branch=master)](https://travis-ci.com/DerrazSofiane/DjangoREST_To-Do_App)

This is a RESTful **API** for a **To-do app**.
The **API** is designed using **Django** and **Postgres** database.
The Project is completely done and the fully documented.
The Project is **open-source** and not used commercially be any means.
The **API** is fully tested with **100% Code coverage** with automated **tests** in a separate folder.
The **docker** and **docker-compose** image configuration files are stored within the project so that you can use it and test it from anywhere with no problems.
You can freely use, edit and learn from this project.

## Documentation

**Firstly we Create a new user profile:**

    POST www.todo.com/users/signup/
    
    {
        "account": {
            "username": "my_user_name",
            "first_name": "test",
            "last_name": "account",
            "password": "my_super_secret_password"
        }
    }

* Note
    1. the URL domain names used in this doc are NOT real and used only for demonstrations.
    2. you can add another field "profile photo,” but the request format will be multipart/form-data.

**For retrieving, updating or deleting your profile, you can use:**

    GET, PUT, PATCH, DELETE www.todo.com/users/{username}/

**And for Logging in you can use:**

    POST www.todo.com/users/login/

    {
        "username": "my_user_name",
        "password": "my_super_secret_password"
    }

**And similarly for logging out you use:**

    POST www.todo.com/users/logout/

* No data in the request body.

**Now we have created a user account, we can start by adding new Todo Categories and Items:**

    POST www.todo.com/users/{username}/todo-groups/
    
    {
        "title": "my first todo Category"
    }

* Note
   1. every user can have many to-do categories (groups), and each category can contain many to-do items.
   2. every to-do group or to-do item will be identified with its sort number which defines its order on the list, it's like a primary key but unique to its own container, the sort is sent in the response, you can specify the sort number only on update not create, the sort number will also be used in ordering the items or groups in the list response.

**To update a specific to-do category:**

    PUT www.todo.com/users/{username}/todo-groups/{group_sort}/

    {
        "sort": 1,
        "title": "my updated to-do category"
    }

**And likewise for deleting a to-do Category:**

    DELETE www.todo.com/users/{username}/todo-groups/{group_sort}/

**After We Created a to-do Category, Now we can add to-do items as follows:**

    POST www.todo.com/users/{username}/todo-groups/{group_sort}/todo-items/
    
    {
        "title": "my first to-do item",
        "description": "my first to-do item description",
        "status": "U"
    }

* Note: the status field can only hold two values U or C which means unchecked or checked, and it indicates whether that to-do task is finished or not.

**To List all to-do tasks the user has, we use:**

    GET www.todo.com/users/{username}/todo-items/

**To Update a specific to-do item:**

    PUT, PATCH www.todo.com/users/{username}/todo-groups/{group_sort}/{todo_sort}/

    {
        "sort": 1,
        "title": "my updated and done to-do task",
        "description": "my updated and done to-do task description",
        "status": "C"
    }

**And likewise for retrieving and deleting a specific to-do item:**

    GET, DELETE www.todo.com/users/{username}/todo-groups/{group_sort}/{todo_sort}/

**A User might want to add an attachment in a to-do item. For this you can do:**

    POST www.todo.com/users/{username}/todo-groups/{group_sort}/{todo_sort}/

**And if the user wants to delete the attachment, he can use:**
    DELETE www.todo.com/users/{username}/todo-groups/{group_sort}/{todo_sort}/{attachment_sort}/

* Note:
    1. the uploaded file can be of any format, the file can't be any larger than 2 MB.
    2. the request body must contain a field called "file" which contains the attachment's file, the request format must be multipart/form-data.
    3. the sort field is also used with attachment as used with to-do categories and items.
