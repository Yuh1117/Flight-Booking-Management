from flask import render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required


from app import login_manager, db
from .forms import SignUpForm, LogInForm, UpdateAccountForm
from . import auth_bp, dao
from . import decorators


@auth_bp.route("/login", methods=["GET", "POST"])
@decorators.anonymous_user
def login():
    form = LogInForm()
    # if method is POST and form is valid
    if form.validate_on_submit():
        print("!!!!!!!!!!!!!!!!!form validated")
        user = dao.authenticate_user(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            flash(
                f"Welcome back, {user.first_name} {user.last_name}!",
                category="success",
            )
            return redirect(url_for("main.home"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/signup", methods=["GET", "POST"])
@decorators.anonymous_user
def signup():
    form = SignUpForm()
    # if method is POST and form is valid
    if form.validate_on_submit():
        print("!!!!!!!!!!!!!!!!!form validated")
        dao.add_user(
            form.email.data,
            form.password.data,
            form.citizen_id.data,
            form.first_name.data,
            form.last_name.data,
            form.phone.data,
        )
        flash(
            f"Account created successfully for {form.email.data}!", category="success"
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/signup.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@auth_bp.route("/logout")
def logout_process():
    logout_user()
    return redirect("/login")


@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html")


@auth_bp.route("/update_account", methods=["GET", "POST"])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("auth.profile"))
    return render_template("user/update_account.html", form=form)
