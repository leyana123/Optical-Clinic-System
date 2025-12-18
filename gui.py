from tkinter import *
from tkinter import ttk


# ------------------ Patient Form (Appointments) ------------------
class PatientForm(Frame):
    def __init__(self, parent, back_callback, refresh_callback=None):
        super().__init__(parent, bg="#dcbfca")
        self.back_callback = back_callback
        self.refresh_callback = refresh_callback

        # Variables
        self.first_name = StringVar()
        self.surname = StringVar()
        self.age = StringVar()
        self.gender = StringVar()
        self.address = StringVar()
        self.dob = StringVar()
        self.mobile = StringVar()
        self.appointment_today = StringVar(value="Yes")
        self.appointment_date = StringVar()
        self.appointment_time = StringVar()

        # time slots in AM/PM 9:00 AM - 4:30 PM
        self.all_slots = (
            [f"{h}:{m:02d} AM" for h in range(9, 12) for m in (0, 30)]
            + ["12:00 PM"]
            + [f"{h - 12}:{m:02d} PM" for h in range(13, 17) for m in (0, 30)]
        )
        self.time_slots = self.all_slots.copy()

        self.build_form()
        self.update_appointment_date()

    def build_form(self):
        row = 0
        Label(self, text="First Name:", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        Entry(self, textvariable=self.first_name, width=30).grid(
            row=row, column=1, pady=5
        )
        row += 1
        Label(self, text="Surname:", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        Entry(self, textvariable=self.surname, width=30).grid(row=row, column=1, pady=5)
        row += 1
        Label(self, text="Gender:", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Combobox(
            self, textvariable=self.gender, values=("Male", "Female", "Other"), width=27
        ).grid(row=row, column=1, pady=5)
        row += 1
        Label(self, text="Address:", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        Entry(self, textvariable=self.address, width=30).grid(row=row, column=1, pady=5)
        row += 1
        Label(self, text="Date of Birth (YYYY-MM-DD):", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        self.dob_entry = Entry(self, textvariable=self.dob, width=30)
        self.dob_entry.grid(row=row, column=1, pady=5)
        self.dob_entry.bind("<FocusOut>", lambda e: calculate_age(self))
        self.dob_entry.bind("<KeyRelease>", lambda e: calculate_age(self))
        row += 1
        Label(self, text="Age:", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        Entry(self, textvariable=self.age, width=30, state="readonly").grid(
            row=row, column=1, pady=5
        )
        row += 1
        Label(self, text="Mobile Number:", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        Entry(self, textvariable=self.mobile, width=30).grid(row=row, column=1, pady=5)
        row += 1

        # Appointment section
        Label(
            self, text="--- Appointment ---", bg="#dcbfca", font=("Arial", 10, "bold")
        ).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        Label(self, text="Appointment Today?", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        combobox = ttk.Combobox(
            self, textvariable=self.appointment_today, values=("Yes", "No"), width=27
        )
        combobox.grid(row=row, column=1, pady=5)
        combobox.bind("<<ComboboxSelected>>", lambda e: self.update_appointment_date())
        row += 1
        Label(self, text="Appointment Date (YYYY-MM-DD):", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        Entry(self, textvariable=self.appointment_date, width=30).grid(
            row=row, column=1, pady=5
        )
        row += 1
        Label(self, text="Appointment Time:", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        self.time_combo = ttk.Combobox(
            self, textvariable=self.appointment_time, values=self.time_slots, width=27
        )
        self.time_combo.grid(row=row, column=1, pady=5)
        self.time_combo.bind("<<ComboboxSelected>>", lambda e: check_time_slot(self))
        row += 1

        Button(
            self,
            text="Add Patient",
            bg="#a4c6e7",
            width=15,
            command=lambda: add_patient(self),
        ).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        Button(self, text="Back", bg="#a4c6e7", width=15, command=self.back).grid(
            row=row, column=0, columnspan=2, pady=10
        )

    def clear_form(self):
        self.first_name.set("")
        self.surname.set("")
        self.gender.set("")
        self.address.set("")
        self.dob.set("")
        self.age.set("")
        self.mobile.set("")
        self.appointment_today.set("Yes")
        self.update_appointment_date()
        self.appointment_time.set(self.time_slots[0] if self.time_slots else "")

    def back(self):  # para ma punta sa main window
        self.destroy()
        self.back_callback()


# ------------------ Appointment List that leads to EyeExam ------------------
class AppointmentListForExam(Frame):
    def build_ui(self):
        Label(
            self,
            text="Appointments (Select a patient to start Eye Exam)",
            bg="#dcbfca",
            font=("Times New Roman", 12, "bold"),
        ).pack(anchor="w", pady=(5, 10))
        frame = Frame(self, bg="#dcbfca")
        frame.pack(fill="both", expand=True)
        # treeview with scrollbar
        cols = (
            "patient_name",
            "age",
            "mobile",
            "appointment_date",
            "appointment_time",
            "doctor",
            "exam_status",
        )
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=110 if c != "patient_name" else 200)
        ysb = ttk.Scrollbar(
            frame, orient="vertical", command=self.tree.yview
        )  # scroll na table para sa appointments
        self.tree.configure(yscroll=ysb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        btn_frame = Frame(self, bg="#dcbfca")
        btn_frame.pack(fill="x", pady=8)
        Button(
            btn_frame, text="Start Eye Exam", command=self.start_exam, bg="#a4c6e7"
        ).pack(side="left", padx=5)
        Button(btn_frame, text="Back", command=self.back_callback, bg="#a4c6e7").pack(
            side="right", padx=5
        )


class EyeExamsWindow(Frame):
    def build_window(self):
        main_container = Frame(self, bg="#dcbfca")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.left_panel = Frame(main_container, bg="#dcbfca")
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        right_panel = Frame(main_container, bg="#dcbfca")
        right_panel.pack(side="left", fill="both", expand=True)

        # select Eye Side
        Label(
            self.left_panel,
            text="Eye Side:",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
        ).pack(anchor="w", pady=(5, 0))
        ttk.Combobox(
            self.left_panel,
            textvariable=self.eye_side,
            values=["Right", "Left", "Both"],
            width=25,
        ).pack(pady=5)

        # Visual Acuity & Refraction Test
        Label(
            self.left_panel,
            text="--- Visual Acuity & Refraction ---",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
        ).pack(anchor="w", pady=(10, 0))

        top_container = Frame(self.left_panel, bg="#dcbfca")
        top_container.pack(side="top", fill="x")

        # OD Layer
        self.od_layer_frame = Frame(top_container, bg="#dcbfca")
        self.od_layer_frame.pack(side="top", fill="x", padx=5, pady=2)
        Label(self.od_layer_frame, text="OD Layer:", bg="#dcbfca").grid(row=0, column=0)
        ttk.Combobox(
            self.od_layer_frame,
            textvariable=self.od_layer,
            values=[str(x) for x in self.layers],
            width=5,
        ).grid(row=0, column=1, padx=5)
        Label(self.od_layer_frame, text="Score:", bg="#dcbfca").grid(
            row=0, column=2, padx=(10, 0)
        )
        Label(self.od_layer_frame, textvariable=self.od_score_var, bg="#dcbfca").grid(
            row=0, column=3
        )

        # OS Layer
        self.os_layer_frame = Frame(top_container, bg="#dcbfca")
        self.os_layer_frame.pack(side="top", fill="x", padx=5, pady=2)
        Label(self.os_layer_frame, text="OS Layer:", bg="#dcbfca").grid(row=0, column=0)
        ttk.Combobox(
            self.os_layer_frame,
            textvariable=self.os_layer,
            values=[str(x) for x in self.layers],
            width=5,
        ).grid(row=0, column=1, padx=5)
        Label(self.os_layer_frame, text="Score:", bg="#dcbfca").grid(
            row=0, column=2, padx=(10, 0)
        )
        Label(self.os_layer_frame, textvariable=self.os_score_var, bg="#dcbfca").grid(
            row=0, column=3
        )

        # OD Refraction
        self.od_ref_frame = Frame(top_container, bg="#dcbfca")
        self.od_ref_frame.pack(side="top", fill="x", padx=5, pady=2)
        Label(self.od_ref_frame, text="OD SPH:", bg="#dcbfca").grid(row=0, column=0)
        ttk.Combobox(
            self.od_ref_frame,
            values=[f"{x / 4:.2f}" for x in range(-48, 49)],
            textvariable=self.od_sph,
            width=5,
        ).grid(row=0, column=1)
        Label(self.od_ref_frame, text="CYL:", bg="#dcbfca").grid(
            row=0, column=2, padx=(5, 0)
        )
        self.od_cyl_dropdown = ttk.Combobox(
            self.od_ref_frame,
            values=[f"{x / 4:.2f}" for x in range(-24, 25)],
            textvariable=self.od_cyl,
            width=5,
            state="disabled",
        )
        self.od_cyl_dropdown.grid(row=0, column=3, padx=2)
        Label(self.od_ref_frame, text="Axis:", bg="#dcbfca").grid(
            row=0, column=4, padx=(5, 0)
        )
        self.od_axis_dropdown = ttk.Combobox(
            self.od_ref_frame,
            values=[str(x) for x in range(0, 181)],
            textvariable=self.od_axis,
            width=5,
            state="disabled",
        )
        self.od_axis_dropdown.grid(row=0, column=5, padx=2)
        Label(self.od_ref_frame, text="ADD:", bg="#dcbfca").grid(
            row=0, column=6, padx=(5, 0)
        )
        ttk.Combobox(
            self.od_ref_frame,
            values=[f"{x / 4:.2f}" for x in range(2, 15)],
            textvariable=self.od_add,
            width=5,
        ).grid(row=0, column=7)

        # OS Refraction
        self.os_ref_frame = Frame(top_container, bg="#dcbfca")
        self.os_ref_frame.pack(side="top", fill="x", padx=5, pady=2)
        Label(self.os_ref_frame, text="OS SPH:", bg="#dcbfca").grid(row=0, column=0)
        ttk.Combobox(
            self.os_ref_frame,
            values=[f"{x / 4:.2f}" for x in range(-48, 49)],
            textvariable=self.os_sph,
            width=5,
        ).grid(row=0, column=1)
        Label(self.os_ref_frame, text="CYL:", bg="#dcbfca").grid(
            row=0, column=2, padx=(5, 0)
        )
        self.os_cyl_dropdown = ttk.Combobox(
            self.os_ref_frame,
            values=[f"{x / 4:.2f}" for x in range(-24, 25)],
            textvariable=self.os_cyl,
            width=5,
            state="disabled",
        )
        self.os_cyl_dropdown.grid(row=0, column=3, padx=2)
        Label(self.os_ref_frame, text="Axis:", bg="#dcbfca").grid(
            row=0, column=4, padx=(5, 0)
        )
        self.os_axis_dropdown = ttk.Combobox(
            self.os_ref_frame,
            values=[str(x) for x in range(0, 181)],
            textvariable=self.os_axis,
            width=5,
            state="disabled",
        )
        self.os_axis_dropdown.grid(row=0, column=5, padx=2)
        Label(self.os_ref_frame, text="ADD:", bg="#dcbfca").grid(
            row=0, column=6, padx=(5, 0)
        )
        ttk.Combobox(
            self.os_ref_frame,
            values=[f"{x / 4:.2f}" for x in range(2, 15)],
            textvariable=self.os_add,
            width=5,
        ).grid(row=0, column=7)

        # Symptom Selector
        Label(
            self.left_panel,
            text="--- Symptoms & Diagnosis ---",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
        ).pack(anchor="w", pady=(10, 0))
        symptom_options = [""] + [
            v["symptom"]
            for v in eye_conditions.values()
            if v["symptom"] != "No specific symptom selected, detected by SPH/Layer"
        ]
        ttk.Combobox(
            self.left_panel,
            textvariable=self.selected_symptom,
            values=symptom_options,
            width=25,
        ).pack(pady=5)

        # (diagnosis, treatments)
        Label(right_panel, text="Patient:", bg="#dcbfca", anchor="w").pack(anchor="w")
        self.patient_label = Label(
            right_panel,
            text="",
            bg="#dcbfca",
            font=("Times New Roman", 12, "bold"),
            anchor="w",
        )
        self.patient_label.pack(anchor="w", pady=(0, 10))

        # Diagnosis
        Label(
            right_panel,
            text="Diagnosis:",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(5, 0))
        self.diagnostic_textbox = Text(right_panel, height=8, width=50)
        self.diagnostic_textbox.pack(fill="x", pady=(0, 5))

        # Treatments
        Label(
            right_panel,
            text="Treatments / Prescription:",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(5, 0))
        self.treatment_textbox = Text(right_panel, height=10, width=50)
        self.treatment_textbox.pack(fill="x", pady=(0, 5))

        # Eye Progression
        Label(
            right_panel,
            text="Eye Progression (Next Action):",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(5, 0))
        self.eye_progression_text = Text(right_panel, height=5, width=50)
        self.eye_progression_text.pack(fill="x", pady=(0, 5))

        # Action Buttons
        button_frame = Frame(right_panel, bg="#dcbfca")
        button_frame.pack(fill="x", pady=10)
        Button(
            button_frame, text="Auto-Diagnose", command=self.auto_diagnose, bg="#a4c6e7"
        ).pack(side="left", padx=5)
        Button(
            button_frame, text="Save Exam", command=self.save_exam, bg="#a4c6e7"
        ).pack(side="right", padx=5)
        Button(
            button_frame, text="Back", command=self.back_callback, bg="#a4c6e7"
        ).pack(side="right", padx=5)


class Window3(Frame):
    def build_ui(self):
        top_frame = Frame(self, bg="#dcbfca")
        top_frame.pack(side="top", fill="x", padx=10, pady=10)

        label_search_frame = Frame(top_frame, bg="#dcbfca")
        label_search_frame.pack(anchor="w", fill="x")
        Label(
            label_search_frame,
            text="Patients (Completed Eye Exam)",
            bg="#dcbfca",
            font=("Arial", 12, "bold"),
        ).pack(side="left")

        Label(label_search_frame, text=" Search:", bg="#dcbfca").pack(side="left")
        self.search_var = StringVar()
        Entry(label_search_frame, textvariable=self.search_var, width=20).pack(
            side="left", padx=5
        )
        Button(
            label_search_frame,
            text="Search",
            command=self.search_patient,
            bg="#a4c6e7",
            fg="black",
        ).pack(side="left")

        tree_frame = Frame(top_frame, bg="#dcbfca")
        tree_frame.pack(fill="x")
        self.patient_tree = ttk.Treeview(
            tree_frame,
            columns=("patient_name", "saved_at"),
            show="headings",
            height=3,
        )
        ysb = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.patient_tree.yview
        )
        self.patient_tree.configure(yscroll=ysb.set)
        self.patient_tree.heading("patient_name", text="Patient Name")
        self.patient_tree.heading("saved_at", text="Saved At")
        self.patient_tree.column("patient_name", width=200)
        self.patient_tree.column("saved_at", width=140)
        self.patient_tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.patient_tree.bind("<<TreeviewSelect>>", self.on_patient_select)

        # Middle Frame for product selection
        middle_frame = Frame(self, bg="#dcbfca")
        middle_frame.pack(fill="x", padx=10, pady=10)

        left_mid_frame = Frame(middle_frame, bg="#dcbfca")
        left_mid_frame.pack(side="left", fill="y", padx=(0, 10))

        right_mid_frame = Frame(middle_frame, bg="#dcbfca")
        right_mid_frame.pack(side="left", fill="both", expand=True)

        # --- Left Mid Frame: Diagnosis & Frames ---
        Label(
            left_mid_frame,
            text="Diagnosis Products: ",
            bg="#dcbfca",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        diag_items = [
            f"{n} - \u20b1{p}" for n, p in self.products_by_category["diagnosis"]
        ]
        ttk.Combobox(
            left_mid_frame,
            textvariable=self.diag_var,
            values=["Select Diagnosis Product"] + diag_items,
            width=35,
        ).pack(anchor="w", pady=5)
        self.diag_var.set("Select Diagnosis Product")
        self.diag_var.trace("w", self.select_diagnosis_item)

        Label(
            left_mid_frame,
            text="Frame colors (Graded lens included based on prescription): ",
            bg="#dcbfca",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(10, 5))

        frame_options = [
            f"{n} - \u20b1{p}" for n, p in self.products_by_category["frame"]
        ]
        ttk.Combobox(
            left_mid_frame,
            textvariable=self.frame_color_var,
            values=["Select Frame Color"] + frame_options,
            width=35,
        ).pack(anchor="w", pady=5)
        self.frame_color_var.set("Select Frame Color")
        # Price is counted here when a selection is made
        self.frame_color_var.trace("w", self.select_frame_color)

        Label(
            left_mid_frame,
            text="Contact Lenses Colors (Graded based on prescription) :",
            bg="#dcbfca",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(10, 5))

        contact_options = [
            f"{n} - \u20b1{p}" for n, p in self.products_by_category["contact"]
        ]
        self.contact_combo = ttk.Combobox(
            left_mid_frame,
            textvariable=self.contact_color_var,
            values=["Select Contact Color"] + contact_options,
            width=35,
        )
        self.contact_combo.pack(anchor="w", pady=5)
        self.contact_color_var.set("Select Contact Color")
        # Price is counted here when a selection is made
        self.contact_color_var.trace("w", self.select_contact_color)

        # --- Right Mid Frame: Add-ons ---
        Label(
            right_mid_frame,
            text="Add-ons for Lens: ",
            bg="#dcbfca",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        self.addon_frame = Frame(right_mid_frame, bg="#dcbfca")
        self.addon_frame.pack(fill="x", expand=True)
        self.addon_frame.grid_columnconfigure(0, weight=1)
        self.addon_frame.grid_columnconfigure(1, weight=1)

        ADD_ON_ITEMS = self.products_by_category["addon"]
        for i, (name, price) in enumerate(ADD_ON_ITEMS):
            var = IntVar()
            self.addon_vars[name] = var
            cb = Checkbutton(
                self.addon_frame,
                text=f"{name} - \u20b1{price}",
                variable=var,
                command=lambda n=name, p=price, v=var: self.toggle_item_addon(n, p, v),
                bg="#dcbfca",
                anchor="w",
                width=35,
                justify="left",
                wraplength=420,
            )
            row = i // 2
            col = i % 2
            cb.grid(row=row, column=col, sticky="we", padx=5, pady=2)

        # Rightmost Panel for Receipt
        right_frame = Frame(self, bg="#dcbfca")
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        Label(
            right_frame, text="Bill / Receipt", bg="#dcbfca", font=("Arial", 12, "bold")
        ).pack(pady=(0, 5))

        receipt_frame = Frame(right_frame, bg="#dcbfca")
        receipt_frame.pack(fill="both", expand=True)

        Button(
            receipt_frame,
            text="Back",
            command=self.back_callback,
            bg="#a4c6e7",
            fg="black",
            font=("Times New Roman", 10),
            width=12,
            height=1,
        ).pack(side="left", padx=5, pady=(0, 5))

        save_btn = Button(
            receipt_frame,
            text="Save Bill",
            command=self.save_bill,
            bg="#a4c6e7",
            fg="black",
            font=("Times New Roman", 10),
            width=12,
            height=1,
        )
        save_btn.pack(side="left", padx=10, pady=(0, 5))

        self.receipt_text = Text(
            receipt_frame, width=55, height=32, bg="white", fg="black"
        )
        self.receipt_text.pack(fill="both", expand=False)


class AllPatientsWindow(Frame):
    def __init__(self, parent, back_callback=None, app_reference=None):
        super().__init__(parent, bg="#dcbfca")
        self.back_callback = back_callback
        self.app_reference = app_reference
        self.build_ui()
        self.load_all_patients()

    def build_ui(self):
        Label(
            self,
            text="All Patients (Final Records)",
            bg="#dcbfca",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", pady=5)

        search_frame = Frame(self, bg="#dcbfca")
        search_frame.pack(fill="x", pady=5)

        Label(search_frame, text="Select Name:", bg="#dcbfca").pack(
            side="left", padx=(5, 2)
        )
        self.search_var = StringVar()
        Entry(search_frame, textvariable=self.search_var).pack(side="left", padx=2)
        Button(search_frame, text="Search", bg="#a4c6e7", command=self.search).pack(
            side="left", padx=2
        )
        Button(
            search_frame, text="View Receipt", bg="#a4c6e7", command=self.view_update
        ).pack(side="left", padx=2)
        Button(
            search_frame, text="View Patient", bg="#a4c6e7", command=self.view_patient
        ).pack(side="left", padx=2)
        Button(
            search_frame, text="Back", bg="#a4c6e7", command=self.back_callback
        ).pack(side="right", padx=2)
        Button(
            search_frame, text="Delete", bg="#a4c6e7", command=self.delete_record
        ).pack(side="right", padx=2)

        tree_frame = Frame(self, bg="#dcbfca")
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        cols = ("patient_name", "total_bill", "exam_status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=240 if c == "patient_name" else 120)
        ysb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y")

        details_frame = Frame(self, bg="#dcbfca")
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)
        Label(
            details_frame,
            text="Details:",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
        ).pack(anchor="w")

        self.details_text = Text(details_frame, height=20, width=80)
        self.details_text.pack(fill="both", expand=True)
