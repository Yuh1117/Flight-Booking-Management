from flask import Blueprint, render_template

from . import auth_bp


@auth_bp.get("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.get("/signup")
def signup():
    return render_template("auth/signup.html")
