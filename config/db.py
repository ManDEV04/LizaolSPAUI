import os
import sqlite3

DB_PATH = "database/spa.db"


def conectar():
    if not os.path.exists("database"):
        os.makedirs("database")

    return sqlite3.connect(DB_PATH)


def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER,
            telefono TEXT,
            foto TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS expedientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            diagnostico TEXT,
            tratamiento TEXT,
            notas TEXT,
            tipo_sangre TEXT,
            genero TEXT,
            alergias TEXT,
            enfermedades_previas TEXT,
            antecedentes_cardiacos TEXT,
            lesiones_previas TEXT,
            cirugias_previas TEXT,
            medicamentos_actuales TEXT,
            contraindicaciones TEXT,
            objetivo_fisioterapia TEXT,
            fecha TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            notas TEXT,
            estado TEXT DEFAULT 'Pendiente',
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
        """
    )

    columnas_expedientes = {
        "tipo_sangre": "TEXT",
        "genero": "TEXT",
        "alergias": "TEXT",
        "enfermedades_previas": "TEXT",
        "antecedentes_cardiacos": "TEXT",
        "lesiones_previas": "TEXT",
        "cirugias_previas": "TEXT",
        "medicamentos_actuales": "TEXT",
        "contraindicaciones": "TEXT",
        "objetivo_fisioterapia": "TEXT",
    }
    _asegurar_columnas(cursor, "expedientes", columnas_expedientes)

    conn.commit()
    conn.close()


def _asegurar_columnas(cursor, tabla, columnas):
    cursor.execute(f"PRAGMA table_info({tabla})")
    existentes = {fila[1] for fila in cursor.fetchall()}

    for nombre, tipo in columnas.items():
        if nombre not in existentes:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {tipo}")
