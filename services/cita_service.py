from config.db import conectar


def insertar_cita(paciente_id, fecha, hora, notas="", estado="Pendiente"):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO citas (paciente_id, fecha, hora, notas, estado)
        VALUES (?, ?, ?, ?, ?)
        """,
        (paciente_id, fecha, hora, notas, estado),
    )

    conn.commit()
    conn.close()


def obtener_citas_por_paciente(paciente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, fecha, hora, notas, estado
        FROM citas
        WHERE paciente_id = ?
        ORDER BY fecha, hora
        """,
        (paciente_id,),
    )
    datos = cursor.fetchall()

    conn.close()
    return datos
