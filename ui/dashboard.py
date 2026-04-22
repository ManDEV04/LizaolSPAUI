import shutil
from pathlib import Path
from uuid import uuid4

import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox, ttk

from services.expediente_service import (
    actualizar_expediente,
    eliminar_expediente,
    eliminar_expedientes_por_paciente,
    insertar_expediente,
    obtener_expedientes,
)
from services.cita_service import insertar_cita, obtener_citas_por_paciente
from services.paciente_service import (
    actualizar_paciente,
    eliminar_paciente,
    insertar_paciente,
    obtener_paciente_por_id,
    obtener_pacientes,
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LizaolaSPAUI - Dashboard")
        self.geometry("1100x650")
        self.resizable(False, False)
        self.configure(fg_color="#F3F6F4")

        self.tabla = None
        self.pacientes_data = []
        self.patient_photo_preview = None
        self.lista_preview_avatar = None
        self.lista_preview_nombre = None
        self.lista_preview_info = None
        self.lista_preview_patient_id = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._configurar_estilo_tabla()
        self._crear_sidebar()
        self._crear_contenido()
        self.mostrar_pacientes()

    def _configurar_estilo_tabla(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Patients.Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#33414A",
            rowheight=38,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 11),
        )
        style.map(
            "Patients.Treeview",
            background=[("selected", "#DDEFE5")],
            foreground=[("selected", "#1D2A33")],
        )
        style.configure(
            "Patients.Treeview.Heading",
            background="#F3F7F4",
            foreground="#1D2A33",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 11, "bold"),
        )
        style.map(
            "Patients.Treeview.Heading",
            background=[("active", "#EAF5EF")],
        )

    def _crear_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1E7F5C")
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="Lizaola SPA",
            font=("Segoe UI", 22, "bold"),
            text_color="white",
        ).pack(pady=(28, 18))

        ctk.CTkButton(
            sidebar,
            text="Pacientes",
            height=40,
            corner_radius=8,
            fg_color="#2D936C",
            hover_color="#166649",
            command=self.mostrar_pacientes,
        ).pack(fill="x", padx=18, pady=6)

        ctk.CTkButton(
            sidebar,
            text="Salir",
            height=40,
            corner_radius=8,
            fg_color="#B03A48",
            hover_color="#8D2E39",
            command=self.destroy,
        ).pack(side="bottom", fill="x", padx=18, pady=22)

    def _crear_contenido(self):
        self.content = ctk.CTkFrame(self, fg_color="#F3F6F4", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

    def mostrar_pacientes(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))

        ctk.CTkLabel(
            header,
            text="Gestión de Pacientes",
            font=("Segoe UI", 28, "bold"),
            text_color="#1D2A33",
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="+ Nuevo paciente",
            height=38,
            corner_radius=8,
            command=self.nuevo_paciente,
        ).pack(side="right")

        summary_row = ctk.CTkFrame(self.content, fg_color="transparent")
        summary_row.pack(fill="x", padx=24, pady=(0, 10))

        ctk.CTkLabel(
            summary_row,
            text="Doble clic en un paciente para abrir su expediente clínico.",
            font=("Segoe UI", 13),
            text_color="#6C7881",
        ).pack(side="left")

        pacientes = obtener_pacientes()
        self.pacientes_data = pacientes
        ctk.CTkLabel(
            summary_row,
            text=f"{len(pacientes)} pacientes registrados",
            font=("Segoe UI", 11, "bold"),
            text_color="#2D936C",
            fg_color="#EAF5EF",
            corner_radius=20,
            padx=12,
            pady=5,
        ).pack(side="right")

        search_row = ctk.CTkFrame(self.content, fg_color="transparent")
        search_row.pack(fill="x", padx=24, pady=(0, 10))

        ctk.CTkLabel(
            search_row,
            text="Buscar",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_row,
            width=320,
            height=36,
            placeholder_text="Escribe nombre, teléfono o ID",
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._filtrar_pacientes)

        ctk.CTkButton(
            search_row,
            text="Limpiar",
            width=90,
            height=36,
            fg_color="#DDEFE5",
            text_color="#1D2A33",
            hover_color="#CCE5D7",
            command=self._limpiar_busqueda,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            search_row,
            text="Editar",
            width=90,
            height=36,
            command=self.editar_paciente_seleccionado,
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            search_row,
            text="Eliminar",
            width=90,
            height=36,
            fg_color="#B03A48",
            hover_color="#8D2E39",
            command=self.eliminar_paciente_seleccionado,
        ).pack(side="right")

        body_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        body_frame.grid_columnconfigure(0, weight=1)
        body_frame.grid_columnconfigure(1, weight=0)
        body_frame.grid_rowconfigure(0, weight=1)

        table_frame = ctk.CTkFrame(body_frame, fg_color="#FFFFFF", corner_radius=14)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        columnas = ("ID", "Nombre", "Edad", "Teléfono")
        self.tabla = ttk.Treeview(
            table_frame,
            columns=columnas,
            show="headings",
            height=18,
            style="Patients.Treeview",
        )

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=130)

        self.tabla.column("ID", width=80)
        self.tabla.column("Nombre", width=260)
        self.tabla.column("Edad", width=100)
        self.tabla.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=14)
        scrollbar.pack(side="right", fill="y", padx=(8, 14), pady=14)
        self.tabla.bind("<Double-1>", self.abrir_expediente)
        self.tabla.bind("<<TreeviewSelect>>", self._mostrar_preview_paciente_lista)

        preview_frame = ctk.CTkFrame(
            body_frame,
            width=250,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#E3ECE5",
        )
        preview_frame.grid(row=0, column=1, sticky="ns")
        preview_frame.grid_propagate(False)

        ctk.CTkLabel(
            preview_frame,
            text="Vista rápida",
            font=("Segoe UI", 18, "bold"),
            text_color="#1D2A33",
        ).pack(anchor="w", padx=16, pady=(18, 4))

        ctk.CTkLabel(
            preview_frame,
            text="Selecciona un paciente para ver su foto y datos básicos.",
            font=("Segoe UI", 11),
            text_color="#6C7881",
            wraplength=210,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 14))

        self.lista_preview_avatar = ctk.CTkFrame(
            preview_frame,
            width=110,
            height=110,
            corner_radius=55,
            fg_color="#EAF5EF",
        )
        self.lista_preview_avatar.pack(pady=(0, 12))
        self.lista_preview_avatar.pack_propagate(False)
        self._render_avatar(self.lista_preview_avatar, None)

        self.lista_preview_nombre = ctk.CTkLabel(
            preview_frame,
            text="Sin selección",
            font=("Segoe UI", 18, "bold"),
            text_color="#1D2A33",
        )
        self.lista_preview_nombre.pack()

        self.lista_preview_info = ctk.CTkLabel(
            preview_frame,
            text="ID: -\nEdad: -\nTeléfono: -",
            font=("Segoe UI", 12),
            text_color="#5E6A73",
            justify="left",
        )
        self.lista_preview_info.pack(pady=(10, 0))

        preview_actions = ctk.CTkFrame(preview_frame, fg_color="transparent")
        preview_actions.pack(fill="x", padx=16, pady=(16, 0))

        ctk.CTkButton(
            preview_actions,
            text="Abrir expediente",
            height=34,
            command=self.abrir_expediente_seleccionado,
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            preview_actions,
            text="Agendar cita",
            height=34,
            fg_color="#DDEFE5",
            text_color="#1D2A33",
            hover_color="#CCE5D7",
            command=self.agendar_cita_paciente_seleccionado,
        ).pack(fill="x")

        self.cargar_pacientes(datos=pacientes)

    def cargar_pacientes(self, datos=None):
        if self.tabla is None:
            return

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        if datos is None:
            datos = obtener_pacientes()

        for index, fila in enumerate(datos):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tabla.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3]))
            item_id = self.tabla.get_children()[-1]
            self.tabla.item(item_id, tags=(tag,))

        self.tabla.tag_configure("evenrow", background="#FFFFFF")
        self.tabla.tag_configure("oddrow", background="#F9FBF9")

        if self.tabla.get_children():
            first_item = self.tabla.get_children()[0]
            self.tabla.selection_set(first_item)
            self.tabla.focus(first_item)
            self._mostrar_preview_paciente_lista()
        else:
            self._limpiar_preview_paciente_lista()

    def _filtrar_pacientes(self, _event=None):
        termino = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""

        if not termino:
            self.cargar_pacientes(datos=self.pacientes_data)
            return

        filtrados = [
            fila
            for fila in self.pacientes_data
            if termino in str(fila[0]).lower()
            or termino in str(fila[1]).lower()
            or termino in str(fila[3]).lower()
        ]
        self.cargar_pacientes(datos=filtrados)

    def _limpiar_busqueda(self):
        if hasattr(self, "search_entry"):
            self.search_entry.delete(0, "end")
        self.cargar_pacientes(datos=self.pacientes_data)

    def _mostrar_preview_paciente_lista(self, _event=None):
        if self.tabla is None or self.lista_preview_avatar is None:
            return

        selected = self.tabla.selection()
        if not selected:
            self._limpiar_preview_paciente_lista()
            return

        datos = self.tabla.item(selected[0], "values")
        paciente = obtener_paciente_por_id(datos[0])
        if not paciente:
            self._limpiar_preview_paciente_lista()
            return

        paciente_id, nombre, edad, telefono, foto = paciente
        self.lista_preview_patient_id = paciente_id
        self._render_avatar(self.lista_preview_avatar, foto)
        self.lista_preview_nombre.configure(text=nombre)
        self.lista_preview_info.configure(
            text=(
                f"ID: {paciente_id}\n"
                f"Edad: {edad if edad not in (None, '') else 'No registrada'}\n"
                f"Teléfono: {telefono if telefono not in (None, '') else 'No registrado'}"
            )
        )

    def _limpiar_preview_paciente_lista(self):
        if self.lista_preview_avatar is None:
            return
        self.lista_preview_patient_id = None
        self._render_avatar(self.lista_preview_avatar, None)
        self.lista_preview_nombre.configure(text="Sin selección")
        self.lista_preview_info.configure(text="ID: -\nEdad: -\nTeléfono: -")

    def _obtener_paciente_seleccionado(self):
        if self.tabla is None:
            return None

        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Selecciona un paciente primero.")
            return None

        return self.tabla.item(selected[0], "values")

    def editar_paciente_seleccionado(self):
        datos = self._obtener_paciente_seleccionado()
        if not datos:
            return

        paciente = obtener_paciente_por_id(datos[0])
        if not paciente:
            messagebox.showerror("Error", "No se encontró el paciente seleccionado.")
            return

        paciente_id, nombre_actual, edad_actual, telefono_actual, foto_actual = paciente

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar Paciente")
        ventana.geometry("380x470")
        ventana.resizable(False, False)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="Editar paciente",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(22, 18))

        foto_var = ctk.StringVar(value=foto_actual or "")
        preview = ctk.CTkLabel(ventana, text="")
        preview.pack(pady=(0, 10))
        self._actualizar_preview_foto(preview, foto_var.get())

        ctk.CTkButton(
            ventana,
            text="Seleccionar foto",
            command=lambda: self._seleccionar_foto_paciente(foto_var, preview),
        ).pack(pady=(0, 14))

        ctk.CTkButton(
            ventana,
            text="Quitar foto",
            fg_color="#DDEFE5",
            text_color="#1D2A33",
            hover_color="#CCE5D7",
            command=lambda: self._quitar_foto_paciente(foto_var, preview),
        ).pack(pady=(0, 14))

        ctk.CTkLabel(ventana, text="Nombre").pack(anchor="w", padx=30)
        nombre = ctk.CTkEntry(ventana, width=300)
        nombre.pack(padx=30, pady=(4, 10))
        nombre.insert(0, str(nombre_actual))

        ctk.CTkLabel(ventana, text="Edad").pack(anchor="w", padx=30)
        edad = ctk.CTkEntry(ventana, width=300)
        edad.pack(padx=30, pady=(4, 10))
        if edad_actual not in (None, ""):
            edad.insert(0, str(edad_actual))

        ctk.CTkLabel(ventana, text="Teléfono").pack(anchor="w", padx=30)
        telefono = ctk.CTkEntry(ventana, width=300)
        telefono.pack(padx=30, pady=(4, 18))
        if telefono_actual not in (None, ""):
            telefono.insert(0, str(telefono_actual))

        def guardar():
            nombre_val = nombre.get().strip()
            edad_val = edad.get().strip()
            telefono_val = telefono.get().strip()

            if not nombre_val:
                messagebox.showwarning("Datos incompletos", "El nombre es obligatorio.")
                return

            if edad_val and not edad_val.isdigit():
                messagebox.showwarning("Dato inválido", "La edad debe ser numérica.")
                return

            actualizar_paciente(
                paciente_id,
                nombre_val,
                int(edad_val) if edad_val else None,
                telefono_val,
                foto_var.get().strip() or None,
            )
            messagebox.showinfo("Éxito", "Paciente actualizado correctamente.")
            ventana.destroy()
            self.pacientes_data = obtener_pacientes()
            self._filtrar_pacientes()

        ctk.CTkButton(ventana, text="Guardar cambios", command=guardar).pack(pady=6)

    def eliminar_paciente_seleccionado(self):
        datos = self._obtener_paciente_seleccionado()
        if not datos:
            return

        paciente_id, nombre, _edad, _telefono = datos
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar a {nombre} y todos sus expedientes?",
        )
        if not confirmar:
            return

        eliminar_expedientes_por_paciente(paciente_id)
        eliminar_paciente(paciente_id)
        messagebox.showinfo("Éxito", "Paciente eliminado correctamente.")
        self.pacientes_data = obtener_pacientes()
        self._filtrar_pacientes()

    def nuevo_paciente(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Nuevo Paciente")
        ventana.geometry("380x470")
        ventana.resizable(False, False)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="Registrar paciente",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(22, 18))

        foto_var = ctk.StringVar(value="")
        preview = ctk.CTkLabel(ventana, text="Sin foto", width=110, height=110, fg_color="#F3F7F4", corner_radius=55)
        preview.pack(pady=(0, 10))

        ctk.CTkButton(
            ventana,
            text="Seleccionar foto",
            command=lambda: self._seleccionar_foto_paciente(foto_var, preview),
        ).pack(pady=(0, 14))

        ctk.CTkButton(
            ventana,
            text="Quitar foto",
            fg_color="#DDEFE5",
            text_color="#1D2A33",
            hover_color="#CCE5D7",
            command=lambda: self._quitar_foto_paciente(foto_var, preview),
        ).pack(pady=(0, 14))

        ctk.CTkLabel(ventana, text="Nombre").pack(anchor="w", padx=30)
        nombre = ctk.CTkEntry(ventana, width=300)
        nombre.pack(padx=30, pady=(4, 10))

        ctk.CTkLabel(ventana, text="Edad").pack(anchor="w", padx=30)
        edad = ctk.CTkEntry(ventana, width=300)
        edad.pack(padx=30, pady=(4, 10))

        ctk.CTkLabel(ventana, text="Teléfono").pack(anchor="w", padx=30)
        telefono = ctk.CTkEntry(ventana, width=300)
        telefono.pack(padx=30, pady=(4, 18))

        def guardar():
            nombre_val = nombre.get().strip()
            edad_val = edad.get().strip()
            telefono_val = telefono.get().strip()

            if not nombre_val:
                messagebox.showwarning("Datos incompletos", "El nombre es obligatorio.")
                return

            if edad_val and not edad_val.isdigit():
                messagebox.showwarning("Dato inválido", "La edad debe ser numérica.")
                return

            insertar_paciente(
                nombre_val,
                int(edad_val) if edad_val else None,
                telefono_val,
                foto_var.get().strip() or None,
            )
            messagebox.showinfo("Éxito", "Paciente agregado correctamente.")
            ventana.destroy()
            self.pacientes_data = obtener_pacientes()
            self.cargar_pacientes(datos=self.pacientes_data)

        ctk.CTkButton(ventana, text="Guardar", command=guardar).pack(pady=6)

    def abrir_expediente(self, event):
        if self.tabla is None:
            return

        selected = self.tabla.selection()
        if not selected:
            return

        datos = self.tabla.item(selected[0], "values")
        self._mostrar_expediente(datos[0])

    def abrir_expediente_seleccionado(self):
        datos = self._obtener_paciente_seleccionado()
        if not datos:
            return
        self._mostrar_expediente(datos[0])

    def agendar_cita_paciente_seleccionado(self):
        datos = self._obtener_paciente_seleccionado()
        if not datos:
            return
        self._abrir_modal_cita(datos[0])

    def _mostrar_expediente(self, paciente_id):
        paciente = obtener_paciente_por_id(paciente_id)
        if not paciente:
            messagebox.showerror("Error", "No se encontró el paciente seleccionado.")
            self.mostrar_pacientes()
            return

        paciente_id, nombre, edad, telefono, foto = paciente
        expedientes = obtener_expedientes(paciente_id)

        for widget in self.content.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.content, height=80, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 0))

        ctk.CTkButton(
            header,
            text="← Volver",
            width=100,
            command=self.mostrar_pacientes,
        ).pack(side="left", pady=20)

        ctk.CTkLabel(
            header,
            text=f"Expediente - {nombre}",
            font=("Arial", 22, "bold"),
        ).pack(side="left", padx=20, pady=20)

        main = ctk.CTkFrame(self.content)
        main.pack(fill="both", expand=True, padx=20, pady=10)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(
            main,
            width=270,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#E3ECE5",
        )
        left.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        left.grid_propagate(False)

        profile_header = ctk.CTkFrame(left, fg_color="#F3F7F4", corner_radius=14)
        profile_header.pack(fill="x", padx=14, pady=(14, 10))

        ctk.CTkLabel(
            profile_header,
            text="Perfil del paciente",
            font=("Segoe UI", 16, "bold"),
            text_color="#1D2A33",
        ).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(
            profile_header,
            text="Resumen general del expediente",
            font=("Segoe UI", 11),
            text_color="#5E6A73",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        avatar = ctk.CTkFrame(left, width=110, height=110, corner_radius=55, fg_color="#EAF5EF")
        avatar.pack(pady=(6, 10))
        avatar.pack_propagate(False)
        self._render_avatar(avatar, foto)

        ctk.CTkLabel(
            left,
            text=nombre,
            font=("Segoe UI", 19, "bold"),
            text_color="#1D2A33",
        ).pack()

        ctk.CTkLabel(
            left,
            text="Paciente activo",
            font=("Segoe UI", 11, "bold"),
            text_color="#2D936C",
            fg_color="#EAF5EF",
            corner_radius=20,
            padx=12,
            pady=5,
        ).pack(pady=(8, 14))

        photo_actions = ctk.CTkFrame(left, fg_color="transparent")
        photo_actions.pack(pady=(0, 12))

        ctk.CTkButton(
            photo_actions,
            text="Cambiar foto",
            width=100,
            height=30,
            command=lambda: self.cambiar_foto_expediente(paciente_id),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            photo_actions,
            text="Quitar",
            width=70,
            height=30,
            fg_color="#DDEFE5",
            text_color="#1D2A33",
            hover_color="#CCE5D7",
            command=lambda: self.quitar_foto_expediente(paciente_id, nombre, edad, telefono),
        ).pack(side="left")

        info_card = ctk.CTkFrame(left, fg_color="transparent")
        info_card.pack(fill="x", padx=16, pady=(0, 12))

        self._info_row(info_card, "ID", str(paciente_id))
        self._info_row(info_card, "Edad", str(edad) if edad not in (None, "") else "No registrada")
        self._info_row(info_card, "Teléfono", str(telefono) if telefono not in (None, "") else "No registrado")
        self._info_row(info_card, "Expedientes", str(len(expedientes)))

        ctk.CTkFrame(left, fg_color="#EEF3EE", height=1).pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            left,
            text="Tip",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=16, pady=(6, 4))

        ctk.CTkLabel(
            left,
            text="Mantén actualizados los datos básicos y registra cada consulta para tener un historial clínico más claro.",
            font=("Segoe UI", 11),
            text_color="#5E6A73",
            justify="left",
            wraplength=220,
        ).pack(anchor="w", padx=16)

        tabs = ctk.CTkTabview(main)
        tabs.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        tab1 = tabs.add("Ficha clínica")
        tab2 = tabs.add("Historial")
        tab3 = tabs.add("Notas")
        tab4 = tabs.add("Antecedentes")

        ficha_header = ctk.CTkFrame(tab1, fg_color="#F3F7F4", corner_radius=12)
        ficha_header.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            ficha_header,
            text="Ficha clínica",
            font=("Segoe UI", 18, "bold"),
            text_color="#1D2A33",
        ).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(
            ficha_header,
            text="Actualiza los datos generales del paciente.",
            font=("Segoe UI", 12),
            text_color="#5E6A73",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        ficha_card = ctk.CTkFrame(
            tab1,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#E3ECE5",
        )
        ficha_card.pack(fill="x", padx=10, pady=(0, 10))
        ficha_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            ficha_card,
            text="Nombre",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).grid(row=0, column=0, pady=8, padx=14, sticky="w")
        nombre_entry = ctk.CTkEntry(ficha_card, width=240, height=34)
        nombre_entry.grid(row=0, column=1, pady=8, padx=(0, 14), sticky="ew")
        nombre_entry.insert(0, nombre)

        ctk.CTkLabel(
            ficha_card,
            text="Edad",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).grid(row=1, column=0, pady=8, padx=14, sticky="w")
        edad_entry = ctk.CTkEntry(ficha_card, width=240, height=34)
        edad_entry.grid(row=1, column=1, pady=8, padx=(0, 14), sticky="ew")
        if edad is not None:
            edad_entry.insert(0, str(edad))

        ctk.CTkLabel(
            ficha_card,
            text="Teléfono",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).grid(row=2, column=0, pady=8, padx=14, sticky="w")
        tel_entry = ctk.CTkEntry(ficha_card, width=240, height=34)
        tel_entry.grid(row=2, column=1, pady=8, padx=(0, 14), sticky="ew")
        if telefono is not None:
            tel_entry.insert(0, str(telefono))

        ctk.CTkButton(
            ficha_card,
            text="Guardar datos",
            height=36,
            command=lambda: guardar_datos(),
        ).grid(row=3, column=0, columnspan=2, pady=14, padx=14, sticky="e")

        resumen_historial = ctk.CTkFrame(tab2, fg_color="#F3F7F4", corner_radius=12)
        resumen_historial.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            resumen_historial,
            text="Historial clínico",
            font=("Segoe UI", 18, "bold"),
            text_color="#1D2A33",
        ).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(
            resumen_historial,
            text=f"Registros encontrados: {len(expedientes)}",
            font=("Segoe UI", 12),
            text_color="#5E6A73",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(tab2, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if not expedientes:
            empty_card = ctk.CTkFrame(scroll, fg_color="#FFFFFF", corner_radius=14)
            empty_card.pack(fill="x", pady=8)
            ctk.CTkLabel(
                empty_card,
                text="Aún no hay registros clínicos para este paciente.",
                font=("Segoe UI", 13),
                text_color="#6C7881",
            ).pack(padx=16, pady=18)
        else:
            for exp in expedientes:
                card = ctk.CTkFrame(
                    scroll,
                    fg_color="#FFFFFF",
                    corner_radius=14,
                    border_width=1,
                    border_color="#E3ECE5",
                )
                card.pack(fill="x", pady=7)

                top_row = ctk.CTkFrame(card, fg_color="transparent")
                top_row.pack(fill="x", padx=12, pady=(12, 8))

                ctk.CTkLabel(
                    top_row,
                    text=f"Fecha: {exp[15]}",
                    font=("Segoe UI", 13, "bold"),
                    text_color="#1D2A33",
                ).pack(side="left")

                action_row = ctk.CTkFrame(top_row, fg_color="transparent")
                action_row.pack(side="right")

                ctk.CTkLabel(
                    action_row,
                    text="Consulta",
                    font=("Segoe UI", 11, "bold"),
                    text_color="#2D936C",
                    fg_color="#EAF5EF",
                    corner_radius=20,
                    padx=10,
                    pady=4,
                ).pack(side="left", padx=(0, 8))

                ctk.CTkButton(
                    action_row,
                    text="Editar",
                    width=70,
                    height=28,
                    fg_color="#DDEFE5",
                    text_color="#1D2A33",
                    hover_color="#CCE5D7",
                    command=lambda e=exp: self.editar_expediente(paciente_id, e),
                ).pack(side="left", padx=(0, 6))

                ctk.CTkButton(
                    action_row,
                    text="Eliminar",
                    width=70,
                    height=28,
                    fg_color="#B03A48",
                    hover_color="#8D2E39",
                    command=lambda expediente_id=exp[0]: self.eliminar_expediente_historial(paciente_id, expediente_id),
                ).pack(side="left")

                ctk.CTkFrame(card, fg_color="#EEF3EE", height=1).pack(fill="x", padx=12)

                detalle = (
                    f"Motivo: {exp[1] or '-'}\n"
                    f"Diagnóstico: {exp[2] or '-'}\n"
                    f"Tratamiento: {exp[3] or '-'}\n"
                    f"Notas: {exp[4] or '-'}"
                )
                ctk.CTkLabel(
                    card,
                    text=detalle,
                    justify="left",
                    anchor="w",
                    font=("Segoe UI", 12),
                    text_color="#4D5963",
                ).pack(fill="x", padx=12, pady=(10, 12))

                extras = []
                if exp[5]:
                    extras.append(f"Tipo de sangre: {exp[5]}")
                if exp[6]:
                    extras.append(f"Género: {exp[6]}")
                if exp[7]:
                    extras.append(f"Alergias: {exp[7]}")
                if exp[8]:
                    extras.append(f"Enfermedades previas: {exp[8]}")
                if exp[9]:
                    extras.append(f"Antecedentes cardíacos: {exp[9]}")
                if exp[10]:
                    extras.append(f"Lesiones previas: {exp[10]}")
                if exp[11]:
                    extras.append(f"Cirugías previas: {exp[11]}")
                if exp[12]:
                    extras.append(f"Medicamentos actuales: {exp[12]}")
                if exp[13]:
                    extras.append(f"Contraindicaciones: {exp[13]}")
                if exp[14]:
                    extras.append(f"Objetivo fisioterapia: {exp[14]}")

                if extras:
                    ctk.CTkFrame(card, fg_color="#EEF3EE", height=1).pack(fill="x", padx=12)
                    ctk.CTkLabel(
                        card,
                        text="\n".join(extras),
                        justify="left",
                        anchor="w",
                        font=("Segoe UI", 11),
                        text_color="#5E6A73",
                    ).pack(fill="x", padx=12, pady=(10, 12))

        notas_header = ctk.CTkFrame(tab3, fg_color="#F3F7F4", corner_radius=12)
        notas_header.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            notas_header,
            text="Nuevo registro clínico",
            font=("Segoe UI", 18, "bold"),
            text_color="#1D2A33",
        ).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(
            notas_header,
            text="Captura la consulta actual, diagnóstico y plan de tratamiento.",
            font=("Segoe UI", 12),
            text_color="#5E6A73",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        notas_scroll = ctk.CTkScrollableFrame(tab3, fg_color="transparent")
        notas_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        notas_card = ctk.CTkFrame(
            notas_scroll,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#E3ECE5",
        )
        notas_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            notas_card,
            text="Motivo",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(14, 4))
        motivo = ctk.CTkEntry(notas_card, placeholder_text="Describe el motivo de consulta", height=34)
        motivo.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            notas_card,
            text="Diagnóstico",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        diagnostico = ctk.CTkEntry(notas_card, placeholder_text="Diagnóstico clínico", height=34)
        diagnostico.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            notas_card,
            text="Tratamiento",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        tratamiento = ctk.CTkEntry(notas_card, placeholder_text="Tratamiento indicado", height=34)
        tratamiento.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            notas_card,
            text="Notas",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        notas = ctk.CTkEntry(notas_card, placeholder_text="Observaciones adicionales", height=34)
        notas.pack(fill="x", padx=14, pady=(0, 14))

        antecedentes_header = ctk.CTkFrame(tab4, fg_color="#F3F7F4", corner_radius=12)
        antecedentes_header.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            antecedentes_header,
            text="Antecedentes clínicos",
            font=("Segoe UI", 18, "bold"),
            text_color="#1D2A33",
        ).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(
            antecedentes_header,
            text="Datos importantes para seguridad, valoración y terapia física.",
            font=("Segoe UI", 12),
            text_color="#5E6A73",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        antecedentes_scroll = ctk.CTkScrollableFrame(tab4, fg_color="transparent")
        antecedentes_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        antecedentes_card = ctk.CTkFrame(
            antecedentes_scroll,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#E3ECE5",
        )
        antecedentes_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            antecedentes_card,
            text="Tipo de sangre",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(14, 4))
        tipo_sangre = ctk.CTkEntry(antecedentes_card, placeholder_text="Ej. O+, A-, B+", height=34)
        tipo_sangre.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Género",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        genero = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Ej. Femenino, Masculino, Otro",
            height=34,
        )
        genero.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Alergias",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        alergias = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Medicamentos, látex, etc.",
            height=34,
        )
        alergias.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Enfermedades previas",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        enfermedades_previas = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Diabetes, hipertensión, artritis, etc.",
            height=34,
        )
        enfermedades_previas.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Antecedentes cardíacos",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        antecedentes_cardiacos = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Arritmias, infarto, marcapasos, etc.",
            height=34,
        )
        antecedentes_cardiacos.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Lesiones previas",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        lesiones_previas = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Esguinces, fracturas, contracturas, etc.",
            height=34,
        )
        lesiones_previas.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Cirugías previas",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        cirugias_previas = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Rodilla, columna, hombro, etc.",
            height=34,
        )
        cirugias_previas.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Medicamentos actuales",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        medicamentos_actuales = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Antiinflamatorios, anticoagulantes, etc.",
            height=34,
        )
        medicamentos_actuales.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Contraindicaciones",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        contraindicaciones = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Ejercicio restringido, dolor agudo, fiebre, etc.",
            height=34,
        )
        contraindicaciones.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            antecedentes_card,
            text="Objetivo fisioterapia",
            font=("Segoe UI", 12, "bold"),
            text_color="#36424B",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        objetivo_fisioterapia = ctk.CTkEntry(
            antecedentes_card,
            placeholder_text="Reducir dolor, mejorar movilidad, rehabilitación, etc.",
            height=34,
        )
        objetivo_fisioterapia.pack(fill="x", padx=14, pady=(0, 14))

        def guardar_nota():
            if not motivo.get().strip():
                messagebox.showwarning("Datos incompletos", "El motivo es obligatorio.")
                return

            insertar_expediente(
                paciente_id,
                motivo.get().strip(),
                diagnostico.get().strip(),
                tratamiento.get().strip(),
                notas.get().strip(),
                tipo_sangre.get().strip(),
                genero.get().strip(),
                alergias.get().strip(),
                enfermedades_previas.get().strip(),
                antecedentes_cardiacos.get().strip(),
                lesiones_previas.get().strip(),
                cirugias_previas.get().strip(),
                medicamentos_actuales.get().strip(),
                contraindicaciones.get().strip(),
                objetivo_fisioterapia.get().strip(),
            )
            messagebox.showinfo("Éxito", "Expediente guardado correctamente.")
            self._mostrar_expediente(paciente_id)

        def guardar_datos():
            nombre_val = nombre_entry.get().strip()
            edad_val = edad_entry.get().strip()
            telefono_val = tel_entry.get().strip()

            if not nombre_val:
                messagebox.showwarning("Datos incompletos", "El nombre es obligatorio.")
                return

            if edad_val and not edad_val.isdigit():
                messagebox.showwarning("Dato inválido", "La edad debe ser numérica.")
                return

            actualizar_paciente(
                paciente_id,
                nombre_val,
                int(edad_val) if edad_val else None,
                telefono_val,
                foto,
            )
            messagebox.showinfo("Éxito", "Datos del paciente actualizados correctamente.")
            self._mostrar_expediente(paciente_id)

        ctk.CTkButton(
            notas_card,
            text="Guardar",
            height=36,
            command=guardar_nota,
        ).pack(anchor="e", padx=14, pady=(0, 14))

    def _info_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="#F9FBF9", corner_radius=10)
        row.pack(fill="x", pady=4)

        ctk.CTkLabel(
            row,
            text=label,
            font=("Segoe UI", 11, "bold"),
            text_color="#5E6A73",
        ).pack(anchor="w", padx=12, pady=(8, 0))

        ctk.CTkLabel(
            row,
            text=value,
            font=("Segoe UI", 13),
            text_color="#1D2A33",
        ).pack(anchor="w", padx=12, pady=(2, 8))

    def _abrir_modal_cita(self, paciente_id):
        paciente = obtener_paciente_por_id(paciente_id)
        if not paciente:
            messagebox.showerror("Error", "No se encontró el paciente seleccionado.")
            return

        _, nombre, _edad, _telefono, _foto = paciente
        citas = obtener_citas_por_paciente(paciente_id)

        ventana = ctk.CTkToplevel(self)
        ventana.title("Agendar cita")
        ventana.geometry("430x560")
        ventana.resizable(False, False)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text=f"Citas de {nombre}",
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w", padx=20, pady=(20, 12))

        historial = ctk.CTkScrollableFrame(ventana, width=390, height=180, fg_color="#F7FAF8")
        historial.pack(fill="x", padx=20, pady=(0, 14))

        if not citas:
            ctk.CTkLabel(
                historial,
                text="No hay citas registradas todavía.",
                text_color="#6C7881",
            ).pack(anchor="w", padx=8, pady=8)
        else:
            for cita in citas:
                card = ctk.CTkFrame(historial, fg_color="#FFFFFF", corner_radius=10)
                card.pack(fill="x", pady=5)
                ctk.CTkLabel(
                    card,
                    text=f"{cita[1]}  {cita[2]}",
                    font=("Segoe UI", 12, "bold"),
                    text_color="#1D2A33",
                ).pack(anchor="w", padx=10, pady=(10, 2))
                ctk.CTkLabel(
                    card,
                    text=f"Estado: {cita[4]}\nNotas: {cita[3] or '-'}",
                    justify="left",
                    text_color="#5E6A73",
                ).pack(anchor="w", padx=10, pady=(0, 10))

        form = ctk.CTkFrame(ventana, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color="#E3ECE5")
        form.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(form, text="Fecha", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(14, 4))
        fecha = ctk.CTkEntry(form, placeholder_text="AAAA-MM-DD", height=34)
        fecha.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(form, text="Hora", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(0, 4))
        hora = ctk.CTkEntry(form, placeholder_text="HH:MM", height=34)
        hora.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(form, text="Notas", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(0, 4))
        notas = ctk.CTkEntry(form, placeholder_text="Seguimiento, terapia, valoración, etc.", height=34)
        notas.pack(fill="x", padx=14, pady=(0, 14))

        def guardar_cita():
            fecha_val = fecha.get().strip()
            hora_val = hora.get().strip()
            notas_val = notas.get().strip()

            if not fecha_val or not hora_val:
                messagebox.showwarning("Datos incompletos", "La fecha y la hora son obligatorias.")
                return

            insertar_cita(paciente_id, fecha_val, hora_val, notas_val)
            messagebox.showinfo("Éxito", "Cita agendada correctamente.")
            ventana.destroy()

        ctk.CTkButton(
            form,
            text="Guardar cita",
            height=36,
            command=guardar_cita,
        ).pack(anchor="e", padx=14, pady=(0, 14))

    def _seleccionar_foto_paciente(self, foto_var, preview_label):
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto del paciente",
            filetypes=[
                ("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not ruta:
            return

        ruta_local = self._guardar_foto_local(ruta)
        if not ruta_local:
            messagebox.showerror("Error", "No se pudo guardar la foto seleccionada.")
            return

        foto_var.set(ruta_local)
        self._actualizar_preview_foto(preview_label, ruta_local)

    def _actualizar_preview_foto(self, preview_label, ruta_foto):
        if ruta_foto:
            try:
                image = ctk.CTkImage(light_image=Image.open(ruta_foto), dark_image=Image.open(ruta_foto), size=(110, 110))
                preview_label.configure(image=image, text="", fg_color="transparent")
                preview_label.image = image
                return
            except Exception:
                pass

        preview_label.configure(image=None, text="Sin foto", fg_color="#F3F7F4", corner_radius=55)
        preview_label.image = None

    def _quitar_foto_paciente(self, foto_var, preview_label):
        foto_var.set("")
        self._actualizar_preview_foto(preview_label, "")

    def _quitar_foto_paciente(self, foto_var, preview_label):
        foto_var.set("")
        self._actualizar_preview_foto(preview_label, "")

    def _render_avatar(self, avatar_frame, ruta_foto):
        for widget in avatar_frame.winfo_children():
            widget.destroy()

        if ruta_foto:
            try:
                image = ctk.CTkImage(light_image=Image.open(ruta_foto), dark_image=Image.open(ruta_foto), size=(110, 110))
                label = ctk.CTkLabel(avatar_frame, text="", image=image)
                label.image = image
                label.place(relx=0.5, rely=0.5, anchor="center")
                return
            except Exception:
                pass

        ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=("Segoe UI Emoji", 34),
            text_color="#2D936C",
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _guardar_foto_local(self, ruta_origen):
        try:
            origen = Path(ruta_origen)
            destino_dir = Path(__file__).resolve().parent.parent / "assets" / "pacientes"
            destino_dir.mkdir(parents=True, exist_ok=True)

            if origen.exists():
                try:
                    if origen.resolve().parent == destino_dir.resolve():
                        return str(origen.resolve())
                except OSError:
                    pass

            extension = origen.suffix.lower() or ".png"
            destino = destino_dir / f"{uuid4().hex}{extension}"
            shutil.copy2(origen, destino)
            return str(destino)
        except Exception:
            return None

    def cambiar_foto_expediente(self, paciente_id):
        paciente = obtener_paciente_por_id(paciente_id)
        if not paciente:
            messagebox.showerror("Error", "No se encontró el paciente seleccionado.")
            return

        _, nombre, edad, telefono, _foto = paciente
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto del paciente",
            filetypes=[
                ("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not ruta:
            return

        ruta_local = self._guardar_foto_local(ruta)
        if not ruta_local:
            messagebox.showerror("Error", "No se pudo guardar la foto seleccionada.")
            return

        actualizar_paciente(paciente_id, nombre, edad, telefono, ruta_local)
        messagebox.showinfo("Éxito", "Foto actualizada correctamente.")
        self._mostrar_expediente(paciente_id)

    def quitar_foto_expediente(self, paciente_id, nombre, edad, telefono):
        actualizar_paciente(paciente_id, nombre, edad, telefono, None)
        messagebox.showinfo("Éxito", "Foto eliminada correctamente.")
        self._mostrar_expediente(paciente_id)

    def editar_expediente(self, paciente_id, expediente):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar expediente")
        ventana.geometry("520x720")
        ventana.resizable(False, False)
        ventana.grab_set()

        scroll = ctk.CTkScrollableFrame(ventana, width=480, height=660)
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(
            scroll,
            text="Editar expediente",
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w", pady=(6, 14))

        campos = [
            ("Motivo", expediente[1], "motivo"),
            ("Diagnóstico", expediente[2], "diagnostico"),
            ("Tratamiento", expediente[3], "tratamiento"),
            ("Notas", expediente[4], "notas"),
            ("Tipo de sangre", expediente[5], "tipo_sangre"),
            ("Género", expediente[6], "genero"),
            ("Alergias", expediente[7], "alergias"),
            ("Enfermedades previas", expediente[8], "enfermedades_previas"),
            ("Antecedentes cardíacos", expediente[9], "antecedentes_cardiacos"),
            ("Lesiones previas", expediente[10], "lesiones_previas"),
            ("Cirugías previas", expediente[11], "cirugias_previas"),
            ("Medicamentos actuales", expediente[12], "medicamentos_actuales"),
            ("Contraindicaciones", expediente[13], "contraindicaciones"),
            ("Objetivo fisioterapia", expediente[14], "objetivo_fisioterapia"),
        ]

        entries = {}
        for label, value, key in campos:
            ctk.CTkLabel(scroll, text=label).pack(anchor="w", pady=(0, 4))
            entry = ctk.CTkEntry(scroll, height=34, width=440)
            entry.pack(fill="x", pady=(0, 10))
            if value:
                entry.insert(0, str(value))
            entries[key] = entry

        def guardar_cambios():
            if not entries["motivo"].get().strip():
                messagebox.showwarning("Datos incompletos", "El motivo es obligatorio.")
                return

            actualizar_expediente(
                expediente[0],
                entries["motivo"].get().strip(),
                entries["diagnostico"].get().strip(),
                entries["tratamiento"].get().strip(),
                entries["notas"].get().strip(),
                entries["tipo_sangre"].get().strip(),
                entries["genero"].get().strip(),
                entries["alergias"].get().strip(),
                entries["enfermedades_previas"].get().strip(),
                entries["antecedentes_cardiacos"].get().strip(),
                entries["lesiones_previas"].get().strip(),
                entries["cirugias_previas"].get().strip(),
                entries["medicamentos_actuales"].get().strip(),
                entries["contraindicaciones"].get().strip(),
                entries["objetivo_fisioterapia"].get().strip(),
            )
            messagebox.showinfo("Éxito", "Expediente actualizado correctamente.")
            ventana.destroy()
            self._mostrar_expediente(paciente_id)

        ctk.CTkButton(
            scroll,
            text="Guardar cambios",
            height=36,
            command=guardar_cambios,
        ).pack(anchor="e", pady=(6, 10))

    def eliminar_expediente_historial(self, paciente_id, expediente_id):
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Eliminar este expediente del historial?",
        )
        if not confirmar:
            return

        eliminar_expediente(expediente_id)
        messagebox.showinfo("Éxito", "Expediente eliminado correctamente.")
        self._mostrar_expediente(paciente_id)
