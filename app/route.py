from flask import Flask, app, redirect, url_for, Blueprint
from app import db, Jobs

main = Blueprint('main', __name__)

@app.route('/')
def root():
    return redirect(url_for('main.home'))