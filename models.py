from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    projects = db.relationship("Project", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tasks = db.relationship(
        "Task", backref="project", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def progress(self):
        if not self.tasks:
            return 0
        completed_tasks = sum(1 for task in self.tasks if task.status == "Terminado")
        return round((completed_tasks / len(self.tasks)) * 100, 2)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_name = db.Column(db.String(200), nullable=False)
    process_group = db.Column(db.String(50), nullable=False)
    knowledge_area = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Pendiente")
    evidence_file = db.Column(db.String(255))
    completion_date = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)


# Lista de procesos PMBOK 6th Edition
PMBOK_PROCESSES = [
    # Inicio
    {
        "group": "Inicio",
        "area": "Integración",
        "name": "Desarrollar Acta de Constitución del Proyecto",
    },
    {"group": "Inicio", "area": "Interesados", "name": "Identificar a los Interesados"},
    # Planificación
    {
        "group": "Planificación",
        "area": "Integración",
        "name": "Desarrollar el Plan para la Dirección del Proyecto",
    },
    {
        "group": "Planificación",
        "area": "Alcance",
        "name": "Planificar la Gestión del Alcance",
    },
    {"group": "Planificación", "area": "Alcance", "name": "Recopilar Requisitos"},
    {"group": "Planificación", "area": "Alcance", "name": "Definir el Alcance"},
    {"group": "Planificación", "area": "Alcance", "name": "Crear la EDT/WBS"},
    {
        "group": "Planificación",
        "area": "Tiempo",
        "name": "Planificar la Gestión del Cronograma",
    },
    {"group": "Planificación", "area": "Tiempo", "name": "Definir las Actividades"},
    {"group": "Planificación", "area": "Tiempo", "name": "Secuenciar las Actividades"},
    {
        "group": "Planificación",
        "area": "Tiempo",
        "name": "Estimar la Duración de las Actividades",
    },
    {"group": "Planificación", "area": "Tiempo", "name": "Desarrollar el Cronograma"},
    {
        "group": "Planificación",
        "area": "Costos",
        "name": "Planificar la Gestión de Costos",
    },
    {"group": "Planificación", "area": "Costos", "name": "Estimar los Costos"},
    {"group": "Planificación", "area": "Costos", "name": "Determinar el Presupuesto"},
    {
        "group": "Planificación",
        "area": "Calidad",
        "name": "Planificar la Gestión de Calidad",
    },
    {
        "group": "Planificación",
        "area": "Recursos Humanos",
        "name": "Planificar la Gestión de Recursos",
    },
    {
        "group": "Planificación",
        "area": "Comunicaciones",
        "name": "Planificar la Gestión de Comunicaciones",
    },
    {
        "group": "Planificación",
        "area": "Riesgos",
        "name": "Planificar la Gestión de Riesgos",
    },
    {"group": "Planificación", "area": "Riesgos", "name": "Identificar los Riesgos"},
    {
        "group": "Planificación",
        "area": "Riesgos",
        "name": "Realizar Análisis Cualitativo de Riesgos",
    },
    {
        "group": "Planificación",
        "area": "Riesgos",
        "name": "Realizar Análisis Cuantitativo de Riesgos",
    },
    {
        "group": "Planificación",
        "area": "Riesgos",
        "name": "Planificar la Respuesta a los Riesgos",
    },
    {
        "group": "Planificación",
        "area": "Adquisiciones",
        "name": "Planificar la Gestión de las Adquisiciones",
    },
    {
        "group": "Planificación",
        "area": "Interesados",
        "name": "Planificar la Participación de los Interesados",
    },
    # Ejecución
    {
        "group": "Ejecución",
        "area": "Integración",
        "name": "Dirigir y Gestionar el Trabajo del Proyecto",
    },
    {
        "group": "Ejecución",
        "area": "Integración",
        "name": "Gestionar el Conocimiento del Proyecto",
    },
    {"group": "Ejecución", "area": "Calidad", "name": "Gestionar la Calidad"},
    {"group": "Ejecución", "area": "Recursos Humanos", "name": "Adquirir Recursos"},
    {"group": "Ejecución", "area": "Recursos Humanos", "name": "Desarrollar el Equipo"},
    {"group": "Ejecución", "area": "Recursos Humanos", "name": "Dirigir el Equipo"},
    {
        "group": "Ejecución",
        "area": "Comunicaciones",
        "name": "Gestionar las Comunicaciones",
    },
    {
        "group": "Ejecución",
        "area": "Riesgos",
        "name": "Implementar la Respuesta a los Riesgos",
    },
    {
        "group": "Ejecución",
        "area": "Adquisiciones",
        "name": "Efectuar las Adquisiciones",
    },
    {
        "group": "Ejecución",
        "area": "Interesados",
        "name": "Gestionar la Participación de los Interesados",
    },
    # Monitoreo y Control
    {
        "group": "Monitoreo",
        "area": "Integración",
        "name": "Monitorear y Controlar el Trabajo del Proyecto",
    },
    {
        "group": "Monitoreo",
        "area": "Integración",
        "name": "Realizar el Control Integrado de Cambios",
    },
    {"group": "Monitoreo", "area": "Alcance", "name": "Validar el Alcance"},
    {"group": "Monitoreo", "area": "Alcance", "name": "Controlar el Alcance"},
    {"group": "Monitoreo", "area": "Tiempo", "name": "Controlar el Cronograma"},
    {"group": "Monitoreo", "area": "Costos", "name": "Controlar los Costos"},
    {"group": "Monitoreo", "area": "Calidad", "name": "Controlar la Calidad"},
    {
        "group": "Monitoreo",
        "area": "Recursos Humanos",
        "name": "Controlar los Recursos",
    },
    {
        "group": "Monitoreo",
        "area": "Comunicaciones",
        "name": "Monitorear las Comunicaciones",
    },
    {"group": "Monitoreo", "area": "Riesgos", "name": "Monitorear los Riesgos"},
    {
        "group": "Monitoreo",
        "area": "Adquisiciones",
        "name": "Controlar las Adquisiciones",
    },
    {
        "group": "Monitoreo",
        "area": "Interesados",
        "name": "Monitorear la Participación de los Interesados",
    },
    # Cierre
    {"group": "Cierre", "area": "Integración", "name": "Cerrar el Proyecto o Fase"},
]
