import hashlib
from config.db import conectar

# 🔐 Encriptar password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 👤 Crear usuario (solo para pruebas)
def crear_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


# ✅ Validar login
def validar_login(username, password):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()

    return user is not None