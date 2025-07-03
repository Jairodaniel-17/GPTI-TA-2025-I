from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import db, User, Project, Task, PMBOK_PROCESSES
from config import Config
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

app = Flask(__name__)
app.config.from_object(Config)

# Inicialización de extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
@login_required
def index():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", projects=projects)


@app.route("/project/new", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        end_date = (
            datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
            if request.form.get("end_date")
            else None
        )

        project = Project(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id,
        )
        db.session.add(project)

        # Crear las 49 tareas PMBOK para el proyecto
        for process in PMBOK_PROCESSES:
            task = Task(
                process_name=process["name"],
                process_group=process["group"],
                knowledge_area=process["area"],
                project=project,
            )
            db.session.add(task)

        db.session.commit()
        flash("Proyecto creado exitosamente", "success")
        return redirect(url_for("index"))

    return render_template("create_project.html")


@app.route("/project/<int:project_id>")
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash("No tienes permiso para ver este proyecto", "danger")
        return redirect(url_for("index"))
    return render_template("project.html", project=project)


@app.route("/task/update/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.project.user_id != current_user.id:
        flash("No tienes permiso para modificar esta tarea", "danger")
        return redirect(url_for("index"))

    status = request.form.get("status")
    file = request.files.get("evidence")

    if status == "Terminado" and not (file or task.evidence_file):
        flash(
            "Debes subir una evidencia para marcar la tarea como terminada", "warning"
        )
        return redirect(url_for("project_detail", project_id=task.project_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{task.id}_{file.filename}")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        task.evidence_file = filename

    task.status = status
    if status == "Terminado":
        task.completion_date = datetime.utcnow()

    db.session.commit()
    flash("Tarea actualizada exitosamente", "success")
    return redirect(url_for("project_detail", project_id=task.project_id))


@app.route("/uploads/<filename>")
@login_required
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        if User.query.filter_by(username=request.form["username"]).first():
            flash("El nombre de usuario ya existe", "danger")
            return redirect(url_for("register"))

        user = User(username=request.form["username"])
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()

        flash("Registro exitoso. Por favor inicia sesión", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=7860)
