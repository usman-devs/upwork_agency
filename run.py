from flask import redirect, url_for, create_app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def root():
    return redirect(url_for('auth.login'))  # Replace 'auth.login' with your login route