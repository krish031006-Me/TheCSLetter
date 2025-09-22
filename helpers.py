"""The sole purpose if this file is to have the helper function for the project..."""
# importing the necessary libraries-
from flask import render_template, session, redirect
from functools import wraps

# the functions-

# login_required to check if the user is logined or not
def login_required(f):
    """ *args is just a tuple used to store all the positional arguments passed to the function and 
    **kwargs is used to store all the keyqord arguments in the form of a dict."""
    @wraps(f) # used this to not clear the metadata of the original function.
    def decorated_function(*args, **kwargs): # this is actually the wraper around our f functions
        # checking if the user_id is stored in cookies
        if session.get("user_id") == None:
            return redirect("/login")
        # returning the actula function od the user is already logged in.
        return f(*args, **kwargs)
    
    return decorated_function 

# function to add commas in stats-
def comma(number):
    ...
