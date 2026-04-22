import customtkinter as ctk
from PIL import Image
from config.db import crear_tablas
from services.auth_service import validar_login
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class LoginApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        crear_tablas()

        # =========================
        # CONFIG VENTANA
        # =========================
        self.title("LizaolaSPAUI")
        self.geometry("1000x600")
        self.resizable(False, False)

        # GRID PRINCIPAL
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =========================
        # 🔵 LADO IZQUIERDO
        # =========================
        left_frame = ctk.CTkFrame(self, corner_radius=0)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # FONDO
        try:
            bg_img = ctk.CTkImage(
                Image.open("assets/spa_bg.png"),
                size=(500, 600)
            )
            bg_label = ctk.CTkLabel(left_frame, image=bg_img, text="")
            bg_label.place(relwidth=1, relheight=1)
        except:
            left_frame.configure(fg_color="#EAF5EF")

        # OVERLAY
        overlay = ctk.CTkFrame(left_frame, fg_color="#EAF5EF")
        overlay.place(relwidth=1, relheight=1)

        # CONTENIDO CENTRADO
        content_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # LOGO
        try:
            logo_img = ctk.CTkImage(
                Image.open("assets/logo.png"),
                size=(180, 180)
            )
            logo_label = ctk.CTkLabel(content_frame, image=logo_img, text="")
            logo_label.pack(pady=20)
        except:
            pass

        # TEXTOS
        ctk.CTkLabel(
            content_frame,
            text="LIZAOLA SPA",
            font=("Arial", 30, "bold"),
            text_color="#1E7F5C"
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            content_frame,
            text="Bienestar, belleza y confianza",
            font=("Arial", 14),
            text_color="#555"
        ).pack()

        ctk.CTkLabel(
            content_frame,
            text="Sistema de Gestión de Pacientes",
            font=("Arial", 13),
            text_color="#777"
        ).pack(pady=10)

        # =========================
        # 🟢 LADO DERECHO
        # =========================
        right_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        right_frame.grid(row=0, column=1, sticky="nsew")

        # CARD LOGIN
        container = ctk.CTkFrame(
            right_frame,
            width=380,
            height=440,
            corner_radius=25,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E5E5E5"
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        # TITULOS
        ctk.CTkLabel(
            container,
            text="Bienvenida",
            font=("Arial", 14),
            text_color="#666"
        ).pack(pady=(25, 0))

        ctk.CTkLabel(
            container,
            text="LizaolaSPAUI",
            font=("Arial", 26, "bold"),
            text_color="#222"
        ).pack(pady=(0, 15))

        # USUARIO
        self.entry_user = ctk.CTkEntry(
            container,
            placeholder_text="Usuario",
            width=280,
            height=45,
            corner_radius=12,
            border_width=1,
            border_color="#D1D5DB"
        )
        self.entry_user.pack(pady=8)

        # PASSWORD
        self.entry_pass = ctk.CTkEntry(
            container,
            placeholder_text="Contraseña",
            show="*",
            width=280,
            height=45,
            corner_radius=12,
            border_width=1,
            border_color="#D1D5DB"
        )
        self.entry_pass.pack(pady=8)

        # MOSTRAR PASSWORD
        self.show_pass = False
        ctk.CTkButton(
            container,
            text="👁 Mostrar contraseña",
            fg_color="transparent",
            text_color="#1E7F5C",
            hover=False,
            command=self.toggle_password
        ).pack()

        # BOTON LOGIN
        ctk.CTkButton(
            container,
            text="Iniciar sesión",
            width=280,
            height=50,
            corner_radius=12,
            fg_color="#2E8B57",
            hover_color="#1E6F46",
            font=("Arial", 14, "bold"),
            command=self.login
        ).pack(pady=15)

        # FOOTER
        ctk.CTkLabel(
            container,
            text="© 2025 LizaolaSPAUI",
            font=("Arial", 10),
            text_color="#999"
        ).pack(side="bottom", pady=10)

    # =========================
    # FUNCIONES
    # =========================
    def toggle_password(self):
        if self.show_pass:
            self.entry_pass.configure(show="*")
            self.show_pass = False
        else:
            self.entry_pass.configure(show="")
            self.show_pass = True

    def login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()

        if not user or not password:
            messagebox.showwarning("Campos vacíos", "Ingresa usuario y contraseña")
            return

        if validar_login(user, password):
            messagebox.showinfo("Éxito", f"Bienvenido {user} 👌")

            # 🔥 AQUÍ LUEGO ABRIMOS EL DASHBOARD
            self.destroy()

            from ui.dashboard import Dashboard
            app = Dashboard()
            app.mainloop()

        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
