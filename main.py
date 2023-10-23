import os
from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from config import app,mysql, conn
from forms import EditForm, LoginForm, NewPostForm, RegistrationForm, ResponsePostForm, UpdateDataForm
from models.models import Usuario, Post, Respuesta
from sqlalchemy import text
import re
from werkzeug.utils import secure_filename


patron = re.compile(r"[<>']")
p_email = re.compile(r'^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,100}$')
contra_segura = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")

@app.route('/', methods=['get', 'post'])
def index():
    post = mysql.session.execute(
        text('''
            select p.id_usuario, titulo, contenido, id_post, fecha, us.usuario
             from posts p
             join usuarios us using(id_usuario)
             order by id_post desc'''
        ))
    return render_template('index.html', post=post)

@app.route('/post=<id>', methods=['GET'])
def post(id):
    try:
        post = mysql.session.execute(
        text(f'''
            select p.id_usuario, titulo, contenido, ruta, id_post, fecha, us.usuario
            from posts p
            join usuarios us using(id_usuario)
            where id_post={id}'''
        ))
        respuesta = mysql.session.execute(
        text(f'''
            select res.contenido, ruta, res.fecha, user.usuario, res.id_usuario, res.id_respuesta
            from usuarios user
            join respuestas res using(id_usuario)
            where res.id_post={id}
        '''))
        if not Post.query.filter_by(id_post=id).first():
            return render_template('404.html'), 404
        return render_template('post.html',post=post, respuesta=respuesta)
    except:
        flash('Error')
        return redirect(url_for('index'))
        

@app.route('/respuesta=<id>', methods=['GET', 'POST'])
@login_required
def respuesta(id):
        ruta_html = ""
        form = ResponsePostForm()
        post = mysql.session.execute(
            text(f'''
                select p.id_usuario, ruta, titulo, contenido, id_post, fecha, us.usuario
                from posts p
                join usuarios us using(id_usuario)
                where id_post={id}'''
            ))    
        if not Post.query.filter_by(id_post=id).first():
            return render_template('404.html'), 404
        if form.validate_on_submit():
            if patron.search(form.contenido.data):
                flash("Introducir solo letras y números.")
                return render_template('respuesta.html', id=id, form=form, post=post)
            if form.foto.data:
                imagen = form.foto.data
                nombre_imagen = secure_filename(str(current_user.id_usuario) + '_ResPost_'+ str(id) + imagen.filename)
                ruta_imagen = os.path.abspath('./static/img/{}'.format(nombre_imagen))
                imagen.save(ruta_imagen)
                ruta_html = "./static/img/{}".format(nombre_imagen)
            resp = Respuesta(ruta=ruta_html, id_post=id, fecha=form.fecha.data, id_usuario=current_user.id_usuario, contenido=form.contenido.data)
            mysql.session.add(resp)
            mysql.session.commit()
            respuesta = mysql.session.execute(
            text(f'''
                select res.contenido, ruta, res.fecha, user.usuario, res.id_usuario, res.id_respuesta
                from usuarios user
                join respuestas res using(id_usuario)
                where res.id_post={id}
            '''))        
            return render_template('post.html',post=post, id=id, respuesta=respuesta)
        return render_template('respuesta.html', id=id, form=form, post=post)



@app.route('/editarid=<id>', methods=['POST', 'GET'])
@login_required
def editar(id):
    try:
        post = mysql.session.execute(
            text(f'''
                select p.id_usuario, titulo, contenido, id_post,   fecha, us.usuario
                from posts p
                join usuarios us using(id_usuario)
                where id_post={id}'''
            ))
        post2 = Post.query.filter_by(id_post=id).first()
        form = EditForm()
        if not Post.query.filter_by(id_post=id).first():
            return render_template('404.html'), 404
        if post2.id_usuario == current_user.id_usuario or current_user.id_rol == 2 or current_user.id_rol == 3:
            if form.is_submitted():
                if patron.search(form.contenido.data):
                    flash("Introducir solo letras y números.")
                    return render_template('editarres.html', form=form, post=post)
                else:
                    post2.contenido = form.contenido.data+'\n""Editado""'
                    mysql.session.commit()               
                    return redirect(url_for('post',id=id))      
            return render_template('editar.html', form=form, post=post)    
        else:
            return redirect(url_for('index'))
    except:
        flash('Error')
        return redirect(url_for('index'))
    
@app.route('/borrarid=<id>')
@login_required
def borrar(id):
        post = Post.query.filter_by(id_post=id).first()
        if not Post.query.filter_by(id_post=id).first():
            return render_template('404.html'), 404
        if post.id_usuario == current_user.id_usuario or current_user.id_rol == 2 or current_user.id_rol == 3:
            if post.ruta != "":
                os.remove(post.ruta)
            res = Respuesta.query.filter_by(id_post=id).all()
            for r in res:
                if r.ruta != "":
                    os.remove(r.ruta)
            mysql.session.delete(post)
            mysql.session.commit()
            flash('Post borrado correctamente')
            return redirect(url_for('index'))
        else:
            flash('¿Qué estas haciendo?')
            return redirect(url_for('index'))

    
@app.route('/editarresid=<id>postid=<id2>', methods=['POST', 'GET'])
@login_required
def editarres(id,id2):
    try:
        res=Respuesta.query.filter_by(id_respuesta=id).first()
        form = EditForm()
        if not Post.query.filter_by(id_post=id2).first() or not Respuesta.query.filter_by(id_respuesta=id).first():
            return render_template('404.html'), 404
        if res.id_usuario == current_user.id_usuario or current_user.id_rol == 2 or current_user.id_rol == 3:
            if form.is_submitted():
                if patron.search(form.contenido.data):
                    flash("Introducir solo letras y números.")
                    return render_template('editarres.html', form=form, post=res)
                else:
                    res.contenido = form.contenido.data+'\n""Editado""'
                    mysql.session.commit()
                    return redirect(url_for('post',id=id2))      
            return render_template('editarres.html', form=form, post=res)    
        else:
            return redirect(url_for('index'))
    except:
        flash('Error')
        return redirect(url_for('index'))
    
@app.route('/borrarresid=<id>id2=<id2>')
@login_required
def borrarres(id,id2):
    try:
        post = Respuesta.query.filter_by(id_respuesta=id).first()
        if not Post.query.filter_by(id_post=id2).first() or not Respuesta.query.filter_by(id_respuesta=id).first():
            return render_template('404.html'), 404
        if post.id_usuario == current_user.id_usuario or current_user.id_rol == 2 or current_user.id_rol == 3:
            if post.ruta != "":
                os.remove(post.ruta)
            mysql.session.delete(post)
            mysql.session.commit()
            flash('Respuesta borrada correctamente')
            return redirect(url_for('post',id=id2))   
        else:
            flash('¿Qué estas haciendo?')
            return redirect(url_for('index'))
    except:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            flash('Ya has iniciado sesión')
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            if patron.search(form.usuario.data):
                flash("Introducir solo letras y números.")
                return render_template('login.html', form=form)
            user = Usuario.query.filter_by(usuario=form.usuario.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Usuario o contraseña inválidos')
                return render_template('login.html', form=form)
            login_user(user, remember=True)
            return redirect(url_for('index'))
        return render_template('login.html', form=form)
    except:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Sesión cerrada correctamente')
        return redirect(url_for('login'))
    except:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
        if current_user.is_authenticated:
            flash('Ya estas registrado')
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.is_submitted():
            if form.password.data != form.password2.data:
                flash('Las contraseñas no coinciden')
                return render_template('registro.html', form=form)
            elif Usuario.query.filter_by(usuario=form.usuario.data).first():
                flash('Nombre de usuario no disponible elije otro')
                return render_template('registro.html', form=form)
            elif Usuario.query.filter_by(email=form.email.data).first():
                flash('Email no disponible, elije otro')        
                return render_template('registro.html', form=form)
            elif p_email.match(form.email.data) == None:
                flash('Formato de email inválido')
                return render_template('registro.html', form=form)
            elif patron.search(form.usuario.data) or patron.search(form.email.data):
                flash("Introducir solo letras y números.")
                return render_template('registro.html', form=form)
            elif contra_segura.match(form.password.data) == None:
                flash("La contraseña debe incluir mayúsculas, minúsculas, un numero y un carácter especial (@$!%*#?&) como mínimo y tener una longitud minima de 8 caracteres y maxima de 40.")
                return render_template('registro.html', form=form)
            elif form.validate():
                nuevo_usuario = form.usuario.data.replace(" ", "_")
                user = Usuario(usuario=nuevo_usuario, email=form.email.data, id_rol=form.id_rol)
                user.set_password(form.password.data)
                mysql.session.add(user)
                mysql.session.commit()
                flash('Usuario registrado correctamente')
                login_user(user, remember=True)
                return redirect(url_for('index'))
            return render_template('registro.html', form=form)
        return render_template('registro.html', form=form)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    try:
        post = conn.execute(
            text(f'''select p.id_usuario, titulo, contenido, id_post, fecha, us.usuario
                from posts p
                join usuarios us using(id_usuario)
                where id_usuario={current_user.id_usuario}
                order by id_post desc''')
            )
        form=UpdateDataForm()
        user = Usuario.query.filter_by(id_usuario=current_user.id_usuario).first()
        if form.is_submitted():
            if not user.check_password(form.actual_pass.data):
                flash('Contraseña incorrecta')
                return render_template('home.html', form=form, post=post)
            else:
                if Usuario.query.filter_by(usuario=form.usuario.data).first():
                    flash('Nombre de usuario no disponible elije otro')
                    return render_template('home.html', form=form, post=post)
                elif Usuario.query.filter_by(email=form.email.data).first():
                    flash('Email no disponible, elije otro')        
                    return render_template('home.html', form=form, post=post)
                elif form.password.data != form.password2.data:
                    flash('Las contraseñas no coinciden')
                    return render_template('home.html', form=form, post=post)
                elif patron.search(form.usuario.data) or patron.search(form.email.data):
                    flash("Introducir solo letras y números.")
                    return render_template('home.html', form=form, post=post)
                elif form.password.data and contra_segura.match(form.password.data) == None:
                    flash("La contraseña debe incluir mayúsculas, minúsculas, un numero y un carácter especial (@$!%*#?&) como mínimo y tener una longitud minima de 8 caracteres y maxima de 40.")
                    return render_template('home.html', form=form, post=post)
                else:
                    nuevo_usuario = form.usuario.data.replace(" ", "_")
                    if form.usuario.data and form.email.data and form.password.data:
                        user.usuario = nuevo_usuario
                        user.email = form.email.data
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Usuario, email y contraseña actualizados correctamente')
                    elif form.usuario.data and form.email.data:
                        user.usuario = nuevo_usuario
                        user.email = form.email.data
                        mysql.session.commit()
                        flash('Usuario e email actualizados correctamente')
                    elif form.usuario.data and form.password.data:
                        user.usuario = nuevo_usuario
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Usuario y contraseña actualizados correctamente')
                    elif form.email.data and form.password.data:
                        user.email = form.email.data
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Email y contraseña actualizados correctamente')
                    elif form.usuario.data:
                        user.usuario = nuevo_usuario
                        mysql.session.commit()
                        flash('Usuario actualizado correctamente')
                    elif form.email.data:
                        user.email = nuevo_usuario
                        mysql.session.commit()
                        flash('Email actualizado correctamente')
                    elif form.password.data:
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Contraseña actualizada correctamente')
                    else:
                        flash('Error desconocido')
                return render_template('home.html', form=form, post=post)
        return render_template('home.html', form=form, post=post)
    except:
        flash('Error')
        return redirect(url_for('index'))
    
@app.route('/nuevoPost', methods=['GET', 'POST'])
@login_required
def nuevoPost():
    try:
        ruta_html=""
        form = NewPostForm()
        if form.validate_on_submit():
            if patron.search(form.titulo.data) or patron.search(form.contenido.data):
                flash("Introducir solo letras y números.")
                return render_template('nuevoPost.html', form=form)
            if form.foto.data:
                imagen = form.foto.data
                nombre_imagen = secure_filename(str(current_user.id_usuario) + '_'+ form.titulo.data + '_' + imagen.filename)
                ruta_imagen = os.path.abspath('./static/img/{}'.format(nombre_imagen))
                imagen.save(ruta_imagen)
                ruta_html = "./static/img/{}".format(nombre_imagen)
            post = Post(ruta=ruta_html, fecha=form.fecha.data, id_usuario=current_user.id_usuario, titulo=form.titulo.data, contenido=form.contenido.data, id_tema=form.id_tema.data)
            mysql.session.add(post)
            mysql.session.commit()
            return redirect(url_for('index'))
        return render_template('nuevoPost.html', form=form)
    except:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    try:
        if current_user.id_rol == 3:
            users = Usuario.query.all()
            return render_template('admin.html', users=users)
        else:
            flash("Ahí no puedes entrar")
            return redirect(url_for('index'))
    except:
        flash('Error')
        return redirect(url_for('index'))
    
@app.route('/admineditusuario=<id>', methods=['GET', 'POST'])
@login_required
def admineditusuario(id):
    try:
        if current_user.id_rol == 3:
            post = conn.execute(
            text(f'''select p.id_usuario, titulo, contenido, id_post, fecha, us.usuario
                from posts p
                join usuarios us using(id_usuario)
                where id_usuario={id}
                order by id_post desc''')
            )
            if not Usuario.query.filter_by(id_usuario=id).first():
                return render_template('404.html'), 404
            form=UpdateDataForm()
            user = Usuario.query.filter_by(id_usuario=id).first()
            if form.is_submitted():
                if Usuario.query.filter_by(usuario=form.usuario.data).first():
                    flash('Nombre de usuario no disponible elije otro')
                    return render_template('admineditusuario.html', form=form, post=post,user=user)
                elif Usuario.query.filter_by(email=form.email.data).first():
                    flash('Email no disponible, elije otro')        
                    return render_template('admineditusuario.html', form=form, post=post,user=user)
                elif form.password.data != form.password2.data:
                    flash('Las contraseñas no coinciden')
                    return render_template('admineditusuario.html', form=form, post=post,user=user)
                elif patron.search(form.usuario.data) or patron.search(form.email.data):
                    flash("Introducir solo letras y números.")
                    return render_template('admineditusuario.html', form=form, post=post,user=user)
                elif form.password.data and contra_segura.match(form.password.data) == None:
                    flash("La contraseña debe incluir mayúsculas, minúsculas, un numero y un carácter especial (@$!%*#?&) como mínimo y tener una longitud minima de 8 caracteres y maxima de 40.")
                    return render_template('admineditusuario.html', form=form, post=post,user=user)
                else:
                    nuevo_usuario = form.usuario.data.replace(" ", "_")
                    if form.usuario.data and form.email.data and form.password.data:
                        user.usuario = nuevo_usuario
                        user.email = form.email.data
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Usuario, email y contraseña actualizados correctamente')
                    elif form.usuario.data and form.email.data:
                        user.usuario = nuevo_usuario
                        user.email = form.email.data
                        mysql.session.commit()
                        flash('Usuario e email actualizados correctamente')
                    elif form.usuario.data and form.password.data:
                        user.usuario = nuevo_usuario
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Usuario y contraseña actualizados correctamente')
                    elif form.email.data and form.password.data:
                        user.email = form.email.data
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Email y contraseña actualizados correctamente')
                    elif form.usuario.data:
                        user.usuario = nuevo_usuario
                        mysql.session.commit()
                        flash('Usuario actualizado correctamente')
                    elif form.email.data:
                        user.email = form.email.data
                        mysql.session.commit()
                        flash('Email actualizado correctamente')
                    elif form.password.data:
                        user.contrasena = user.return_password(form.password.data)
                        mysql.session.commit()
                        flash('Contraseña actualizada correctamente')
                    else:
                        flash('Error desconocido')
                return render_template('admineditusuario.html', form=form, post=post, user=user)
            return render_template('admineditusuario.html', form=form, post=post,user=user)
        else:
            flash("¿Donde ibas?")
            return redirect(url_for('index'))
    except:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/borrauserid=<id>')
@login_required
def borraruser(id):
    try:
        if not Usuario.query.filter_by(id_usuario=id).first():
            return render_template('404.html'), 404
        if current_user.id_rol == 3:
            user = Usuario.query.filter_by(id_usuario=id).first()
            mysql.session.delete(user)
            mysql.session.commit()
            flash('Usuario borrado correctamente')
            return redirect(url_for('admin'))
        else:
            flash('¿Qué estas haciendo?')
            return redirect(url_for('index'))
    except:
        flash('Error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")

@app.errorhandler(401)
def unauthorized(e):
    flash('Para continuar en la aplicación regístrate o inicia sesión')
    return redirect(url_for('index'))

if __name__=="__main__":
    app.run(host= '0.0.0.0', port=5000, debug=True)