def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/home', methods=['GET'])
    def home():
        if 'token' in session:
            session['username'] = check_token(session['token'])
            if 'username' in session:
                if session['username'] == 'admin':
                    return render_template('home_admin.html', flag=FLAG)
                else:
                    return render_template('home.html', cvs_list=db_get_user_cv(session['username']))
            else:
                session.pop('username', None)
                session.pop('token', None)
        else:
            return redirect(url_for('main'))


    @app.route("/cv/<cvid>", methods=['GET', 'DELETE'])
    def work_cv(cvid):
        if 'token' in session:
            session['username'] = check_token(session['token'])
            if 'username' in session:
                if session['username'] == 'admin':
                    db_check_cv(cvid)
                    cv_work = db_get_cv(cvid)
                    if cv:
                        cv_data = []
                        k = cv_work.keys()
                        for key in k:
                            temp = {"key": key, "value": cv_work[key]}
                            cv_data.append(temp)
                        return render_template('cv_admin.html', id=cvid, cv_data=cv_data)
            session.pop('username', None)
            session.pop('token', None)
        return redirect(url_for('main'))

    @app.route("/cv_list", methods=['GET', 'DELETE'])
    def cv_list():
        if 'token' in session:
            session['username'] = check_token(session['token'])
            if 'username' in session:
                if session['username'] == 'admin':
                    # TODO
                    return render_template('all_cvs.html', cvs_list=db_get_new_cv())
            session.pop('username', None)
            session.pop('token', None)
        return redirect(url_for('main'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'token' in session:
            return redirect(url_for('home'))
        if request.method == 'GET':
            return render_template('login.html')
        else:
            u_login = request.form.get('login')
            u_password = request.form.get('password')
            if u_login and u_password:
                user = db_find_user(u_login, u_password)
                if user:
                    session['username'] = u_login
                    session['token'] = token_generator()
                    db_update_user_token(u_login, u_password, session['token'])
                    return redirect(url_for('home'))

        session['last_error'] = "Username or password wrong :("
        session['last_url'] = "/login"
        return redirect(url_for('error'))

    @app.route('/', methods=['GET'])
    def main():
        if 'token' in session:
            session['username'] = check_token(session['token'])
            if 'username' in session:
                if session['username'] == 'admin':
                    return redirect(url_for('home'))
                return render_template('main_auth.html')
            else:
                session.pop('username', None)
                session.pop('token', None)
        else:
            return render_template('main.html')

    @app.route('/registration', methods=['GET', 'POST'])
    def registration():
        if 'token' in session:
            return redirect(url_for('home'))
        if request.method == 'GET':
            return render_template('registration.html')
        else:
            u_login = request.form.get('username')
            u_password = request.form.get('password')
            if u_login and u_password:
                user = db_find_user(u_login, u_password)
                if user:
                    session['last_error'] = "User already exist :("
                    session['last_url'] = "/registration"
                    return redirect(url_for('error'))
                else:
                    session['username'] = u_login
                    session['token'] = token_generator()
                    db_add_user(u_login, u_password, session['token'])
                    return redirect(url_for('home'))
            return redirect(url_for('error'))

    @app.route('/logout', methods=['GET'])
    def logout():
        session.pop('username', None)
        session.pop('token', None)
        return redirect(url_for('main'))

    @app.route('/error', methods=['GET'])
    def error():
        if 'last_error' in session and 'last_url' in session:
            if 'token' in session:
                session['username'] = check_token(session['token'])
                if 'username' in session:
                    return render_template('error_auth.html', error=session['last_error'], back_url=session['last_url'])
                else:
                    session.pop('username', None)
                    session.pop('token', None)
            else:
                return render_template('error.html', error=session['last_error'], back_url=session['last_url'])
        else:
            return render_template('error.html')

    @app.route('/cv', methods=['GET', 'POST'])
    def cv():
        if 'token' in session:
            session['username'] = check_token(session['token'])
            if 'username' in session:
                if session['username'] == 'admin':
                    return redirect(url_for('home'))
                if request.method == 'GET':
                    return render_template('cv.html')
                else:
                    cv_firstname = request.form.get('firstname')
                    cv_lastname = request.form.get('lastname')
                    cv_email = request.form.get('email')
                    cv_phone = request.form.get('phone')
                    cv_message = request.form.get('message')
                    if cv_firstname and cv_lastname and cv_email and cv_phone and cv_message:
                        cv = request.form.to_dict()
                        cv['user'] = session['username']
                        cv['status'] = 'Wait'
                        cv['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if db_count_user_cv(cv['user']) > 9:
                            session['last_error'] = "Maximum of request reached :("
                            session['last_url'] = "/home"
                            return redirect(url_for('error'))
                        db_add_cv(cv)
                        return redirect(url_for('home'))
                    else:
                        session['last_error'] = "The request is not correct :("
                        session['last_url'] = "/cv"
                        return redirect(url_for('error'))
            session.pop('username', None)
            session.pop('token', None)
        return redirect(url_for('main'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error="404: Page not found!", back_url="/"), 404

    return app

