from config.db import conectar
from datetime import datetime

def obtener_expedientes(paciente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, motivo, diagnostico, tratamiento, notas,
           tipo_sangre, genero, alergias, enfermedades_previas,
           antecedentes_cardiacos, lesiones_previas, cirugias_previas,
           medicamentos_actuales, contraindicaciones, objetivo_fisioterapia,
           fecha
    FROM expedientes
    WHERE paciente_id = ?
    ORDER BY fecha DESC, id DESC
    """, (paciente_id,))

    datos = cursor.fetchall()
    conn.close()

    return datos


def insertar_expediente(
    paciente_id,
    motivo,
    diagnostico,
    tratamiento,
    notas,
    tipo_sangre="",
    genero="",
    alergias="",
    enfermedades_previas="",
    antecedentes_cardiacos="",
    lesiones_previas="",
    cirugias_previas="",
    medicamentos_actuales="",
    contraindicaciones="",
    objetivo_fisioterapia="",
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expedientes 
    (
        paciente_id, motivo, diagnostico, tratamiento, notas,
        tipo_sangre, genero, alergias, enfermedades_previas,
        antecedentes_cardiacos, lesiones_previas, cirugias_previas,
        medicamentos_actuales, contraindicaciones, objetivo_fisioterapia, fecha
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        paciente_id,
        motivo,
        diagnostico,
        tratamiento,
        notas,
        tipo_sangre,
        genero,
        alergias,
        enfermedades_previas,
        antecedentes_cardiacos,
        lesiones_previas,
        cirugias_previas,
        medicamentos_actuales,
        contraindicaciones,
        objetivo_fisioterapia,
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()


def eliminar_expedientes_por_paciente(paciente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expedientes WHERE paciente_id = ?",
        (paciente_id,),
    )

    conn.commit()
    conn.close()


def actualizar_expediente(
    expediente_id,
    motivo,
    diagnostico,
    tratamiento,
    notas,
    tipo_sangre="",
    genero="",
    alergias="",
    enfermedades_previas="",
    antecedentes_cardiacos="",
    lesiones_previas="",
    cirugias_previas="",
    medicamentos_actuales="",
    contraindicaciones="",
    objetivo_fisioterapia="",
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE expedientes
        SET motivo = ?, diagnostico = ?, tratamiento = ?, notas = ?,
            tipo_sangre = ?, genero = ?, alergias = ?, enfermedades_previas = ?,
            antecedentes_cardiacos = ?, lesiones_previas = ?, cirugias_previas = ?,
            medicamentos_actuales = ?, contraindicaciones = ?, objetivo_fisioterapia = ?
        WHERE id = ?
        """,
        (
            motivo,
            diagnostico,
            tratamiento,
            notas,
            tipo_sangre,
            genero,
            alergias,
            enfermedades_previas,
            antecedentes_cardiacos,
            lesiones_previas,
            cirugias_previas,
            medicamentos_actuales,
            contraindicaciones,
            objetivo_fisioterapia,
            expediente_id,
        ),
    )

    conn.commit()
    conn.close()


def eliminar_expediente(expediente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expedientes WHERE id = ?",
        (expediente_id,),
    )

    conn.commit()
    conn.close()
