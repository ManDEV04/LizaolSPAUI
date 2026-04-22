from config.db import conectar


def obtener_pacientes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes")
    datos = cursor.fetchall()

    conn.close()
    return datos


def obtener_paciente_por_id(paciente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nombre, edad, telefono, foto FROM pacientes WHERE id = ?",
        (paciente_id,),
    )
    dato = cursor.fetchone()

    conn.close()
    return dato


def insertar_paciente(nombre, edad, telefono, foto=None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pacientes (nombre, edad, telefono, foto)
    VALUES (?, ?, ?, ?)
    """, (nombre, edad, telefono, foto))

    conn.commit()
    conn.close()


def actualizar_paciente(paciente_id, nombre, edad, telefono, foto=None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE pacientes
        SET nombre = ?, edad = ?, telefono = ?, foto = ?
        WHERE id = ?
        """,
        (nombre, edad, telefono, foto, paciente_id),
    )

    conn.commit()
    conn.close()


def eliminar_paciente(paciente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM pacientes WHERE id = ?",
        (paciente_id,),
    )

    conn.commit()
    conn.close()
