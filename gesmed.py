from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from config import Config
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import Response
import MySQLdb


gesmed = Flask(__name__)
gesmed.config.from_object(Config)

mysql = MySQL(gesmed)

@gesmed.route("/DBCheck")
def dbCheck():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        return jsonify({"status": "Ok", "message": "Conectado con exitote!!! ;)"}), 200
    except MySQLdb.MySQLError as e:
        return jsonify({"status": "Error", "message": str(e)}), 500





@gesmed.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        rfc = request.form.get("rfc")
        password = request.form.get("password")

        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT ID_Medico, Nombre_Medico, AP_Medico, AM_Medico, Contrasena, Rol
            FROM Medicos
            WHERE RFC_Medico = %s
        """, (rfc,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            stored_password = user[4]
            if password == stored_password:
                session["user_id"] = user[0]
                session["nombre_medico"] = f"Dr. {user[1]} {user[2]} {user[3]}"
                session["rol"] = user[5]
                flash("¡Login exitoso!", "success")

                if user[5] == "admin":
                    return redirect(url_for("dashboard"))
                else:
                    return redirect(url_for("index"))
            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

    return render_template("login.html")



@gesmed.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()

    # Médicos
    cursor.execute("SELECT ID_Medico, Nombre_Medico, AP_Medico, AM_Medico, RFC_Medico, Cedula, Correo_Medico, Rol FROM Medicos")
    medicos = cursor.fetchall()

    # Pacientes
    cursor.execute("SELECT ID_Paciente, ID_Medico, Nombre_Paciente, AP_Paciente, AM_Paciente, FechaNacimiento FROM Pacientes")
    pacientes = cursor.fetchall()

    # Citas
    cursor.execute("""
        SELECT
            C.ID_Cita, P.Nombre_Paciente, P.AP_Paciente, P.AM_Paciente,
            C.Fecha,
            M.Nombre_Medico, M.AP_Medico, M.AM_Medico
        FROM Citas C
        JOIN Pacientes P ON C.ID_Paciente = P.ID_Paciente
        JOIN Medicos M ON C.ID_Medico = M.ID_Medico
    """)
    citas = cursor.fetchall()

    cursor.close()

  
    citas = [dict(zip(
        ["ID_Cita", "Nombre_Paciente", "AP_Paciente", "AM_Paciente", "Fecha", "Nombre_Medico", "AP_Medico", "AM_Medico"],
        cita)) for cita in citas]

    return render_template(
        "dashboard.html",
        nombre_medico=session.get("nombre_medico"),
        rol=session.get("rol"),
        user_id=session.get("user_id"),
        medicos=medicos,
        pacientes=pacientes,
        citas=citas
    )


@gesmed.route("/index")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()

    # Médicos
    cursor.execute("""
        SELECT ID_Medico, Nombre_Medico, AP_Medico, AM_Medico, RFC_Medico, Cedula, Correo_Medico, Rol
        FROM Medicos
    """)
    medicos = cursor.fetchall()

    # Pacientes
    cursor.execute("""
        SELECT ID_Paciente, ID_Medico, Nombre_Paciente, AP_Paciente, AM_Paciente, FechaNacimiento 
        FROM Pacientes
    """)
    pacientes = cursor.fetchall()

    # Citas
    cursor.execute("""
        SELECT
            C.ID_Cita, P.Nombre_Paciente, P.AP_Paciente, P.AM_Paciente,
            C.Fecha,
            M.Nombre_Medico, M.AP_Medico, M.AM_Medico
        FROM Citas C
        JOIN Pacientes P ON C.ID_Paciente = P.ID_Paciente
        JOIN Medicos M ON C.ID_Medico = M.ID_Medico
    """)
    citas = cursor.fetchall()
    cursor.close()

    # Formatear citas como diccionarios
    citas = [dict(zip(
        ["ID_Cita", "Nombre_Paciente", "AP_Paciente", "AM_Paciente", "Fecha", "Nombre_Medico", "AP_Medico", "AM_Medico"],
        cita)) for cita in citas]

    return render_template("index.html",
        nombre_medico=session.get("nombre_medico"),
        rol=session.get("rol"),
        user_id=session.get("user_id"),
        medicos=medicos,
        pacientes=pacientes,
        citas=citas
    )











@gesmed.route("/agregar_medico", methods=["POST"])
def agregar_medico():
    if "user_id" not in session or session.get("rol") != "admin":
        flash("No tienes permisos para agregar médicos.", "error")
        return redirect(url_for("dashboard"))

    # Obtener datos del formulario
    nombre = request.form.get("nombre")
    apellido_paterno = request.form.get("apellido_paterno")
    apellido_materno = request.form.get("apellido_materno")
    cedula = request.form.get("cedula")
    correo = request.form.get("correo")
    contrasena = request.form.get("contrasena")
    verif_contrasena = request.form.get("verif_contrasena")
    rfc = request.form.get("rfc")
    rol = request.form.get("rol")


    if contrasena != verif_contrasena:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("dashboard"))


    imagen = None
    if "imagen_medico" in request.files:
        file = request.files["imagen_medico"]
        if file.filename != '':
            imagen = file.read()  # Leemos el contenido binario

    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO Medicos (RFC_Medico, Nombre_Medico, AP_Medico, AM_Medico, Cedula, Correo_Medico, Contrasena, Rol, Imagen_Medico)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (rfc, nombre, apellido_paterno, apellido_materno, cedula, correo, contrasena, rol, imagen))

        mysql.connection.commit()
        flash("Médico agregado correctamente.", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al agregar médico: {str(e)}", "error")

    finally:
        cursor.close()

    return redirect(url_for("dashboard"))

@gesmed.route("/agregar_paciente", methods=["POST"])
def agregar_paciente():
    if "user_id" not in session:
        flash("Debes iniciar sesión para registrar pacientes.", "error")
        return redirect(url_for("login"))

    nombre_medico = request.form.get("medico_nombre")  # solo informativo
    nombre = request.form.get("nombre")
    apellido_paterno = request.form.get("apellido_paterno")
    apellido_materno = request.form.get("apellido_materno")
    fecha_nacimiento = request.form.get("fecha_nacimiento")
    alergias = request.form.get("alergias")
    antecedentes = request.form.get("antecedentes_familiares")
    enfermedades = request.form.get("enfermedades_cronicas")

    id_medico = session.get("user_id")  # este es el médico que está logueado

    if not nombre or not apellido_paterno or not fecha_nacimiento:
        flash("Faltan campos obligatorios.", "error")
        return redirect(url_for("dashboard"))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (ID_Medico, Nombre_Paciente, AP_Paciente, AM_Paciente, FechaNacimiento,
                                   EnfermedadesCronicas, Alergias, AntecedentesFamiliares)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_medico, nombre, apellido_paterno, apellido_materno,
              fecha_nacimiento, enfermedades, alergias, antecedentes))
        mysql.connection.commit()
        flash("Paciente registrado correctamente.", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al registrar paciente: {str(e)}", "error")

    finally:
        cursor.close()

    return redirect(url_for("dashboard"))

@gesmed.route("/agregar_cita", methods=["POST"])
def agregar_cita():
    if "user_id" not in session:
        flash("Debes iniciar sesión", "error")
        return redirect(url_for("login"))

    id_medico = session.get("user_id")
    id_paciente = request.form.get("id_paciente")
    fecha = request.form.get("fecha")
    altura = request.form.get("altura")
    peso = request.form.get("peso")
    temperatura = request.form.get("temperatura")
    latidos = request.form.get("latidos")
    saturacion = request.form.get("saturacion")
    glucosa = request.form.get("glucosa")
    sintomas = request.form.get("sintomas")
    diagnostico = request.form.get("diagnostico")
    tratamiento = request.form.get("tratamiento")
    estudios = request.form.get("estudios")

   
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Receta Médica")

    pdf.drawString(100, 750, f"Fecha: {fecha}")
    pdf.drawString(100, 730, f"Médico ID: {id_medico}")
    pdf.drawString(100, 710, f"Paciente ID: {id_paciente}")
    pdf.drawString(100, 690, f"Altura: {altura} m")
    pdf.drawString(100, 670, f"Peso: {peso} kg")
    pdf.drawString(100, 650, f"Temperatura: {temperatura} °C")
    pdf.drawString(100, 630, f"Latidos: {latidos} bpm")
    pdf.drawString(100, 610, f"Saturación: {saturacion} %")
    pdf.drawString(100, 590, f"Glucosa: {glucosa} mg/dl")

    pdf.drawString(100, 560, "Síntomas:")
    pdf.drawString(120, 540, sintomas[:80])  # solo primera línea

    pdf.drawString(100, 510, "Diagnóstico:")
    pdf.drawString(120, 490, diagnostico[:80])

    pdf.drawString(100, 460, "Tratamiento:")
    pdf.drawString(120, 440, tratamiento[:80])

    pdf.drawString(100, 410, "Estudios:")
    pdf.drawString(120, 390, estudios[:80])

    pdf.showPage()
    pdf.save()
    pdf_data = buffer.getvalue()
    buffer.close()

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO Citas (ID_Paciente, ID_Medico, Fecha, Peso, Altura, Temperatura, 
            LatidosPorMinuto, SaturacionOxigeno, Glucosa, Sintomas, Diagnostico, Tratamiento, 
            SolicitudEstudios, PDF_Receta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            id_paciente, id_medico, fecha, peso, altura, temperatura,
            latidos, saturacion, glucosa, sintomas, diagnostico,
            tratamiento, estudios, pdf_data
        ))
        mysql.connection.commit()
        flash("Cita registrada con PDF generado.", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al guardar cita: {str(e)}", "error")

    finally:
        cursor.close()

    return redirect(url_for("dashboard"))

@gesmed.route("/cita/pdf/<int:id>")
def ver_pdf(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT PDF_Receta FROM Citas WHERE ID_Cita = %s", (id,))
    resultado = cursor.fetchone()
    cursor.close()

    if resultado and resultado[0]:
        return Response(resultado[0], mimetype='application/pdf')
    else:
        return "PDF no encontrado", 404


@gesmed.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada exitosamente", "info")
    return redirect(url_for("login"))


@gesmed.route("/medicos")
def listar_medicos():
    if "user_id" not in session or session.get("rol") != "admin":
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT ID_Medico, Nombre_Medico, AP_Medico, AM_Medico, RFC_Medico, Cedula, Correo_Medico, Rol
        FROM Medicos
    """)
    medicos = cursor.fetchall()
    cursor.close()

    return render_template("medicos.html", medicos=medicos)




if __name__ == "__main__":
    gesmed.run(port=3000, debug=True)