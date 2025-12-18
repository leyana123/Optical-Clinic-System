from tkinter import *
from tkinter import ttk, messagebox
import datetime
from PIL import Image, ImageTk
import sqlite3

# problemss
eye_conditions = {
    "Astigmatism": {
        "symptom": "Blurry or distorted vision",
        "treatment": "Glasses, contact lenses",
        "affects_eye_grade": True,
        "suggestion": "Becoming blurry",
    },
    "Behçet's Disease": {
        "symptom": "Redness, pain, eye inflammation",
        "treatment": "Steroid drops: Dexamethasone",
        "affects_eye_grade": False,
    },
    "Color Blindness": {
        "symptom": "Difficulty distinguishing colors",
        "treatment": "Special lenses (EnChroma)",
        "affects_eye_grade": False,
    },
    "Dry Eye": {
        "symptom": "Scratchy, watery, or irritated eyes",
        "treatment": "Eye Drops: Artificial tears",
        "affects_eye_grade": False,
    },
    "Myopia (Nearsightedness)": {
        "symptom": "No specific symptom selected, detected by SPH/Layer",
        "treatment": "Glasses, contact lenses",
        "affects_eye_grade": True,
        "suggestion": "Becoming blurry",
    },
    "Hyperopia (Farsightedness)": {
        "symptom": "No specific symptom selected, detected by SPH/Layer",
        "treatment": "Glasses, contact lenses",
        "affects_eye_grade": True,
        "suggestion": "Becoming blurry",
    },
    "Pink Eye (Conjunctivitis)": {
        "symptom": "Red, itchy, watery eyes",
        "treatment": "Antibiotic drops: Antihistamines",
        "affects_eye_grade": False,
    },
    "Presbyopia": {
        "symptom": "Age-related difficulty reading",
        "treatment": "Reading glasses",
        "affects_eye_grade": True,
        "suggestion": "Becoming blurry",
    },
    "Uveitis": {
        "symptom": "Red, painful eyes, inflammation",
        "treatment": "Eye Drops: Lotepred",
        "affects_eye_grade": False,
    },
}
symptom_to_medical = {v["symptom"]: k for k, v in eye_conditions.items()}

# database setup
DB_FILE = "optical_clinic_system.db"  # database name


def get_db_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


EYE_EXAM_FEE = ("Medical Checkup Fee", 1000)


def init_db_schema():
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON")

    # PatientFullInfo table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS PatientFullInfo (
            patient_name TEXT PRIMARY KEY,
            first_name TEXT,
            surname TEXT,
            gender TEXT,
            address TEXT,
            dob TEXT,
            age INTEGER,
            mobile TEXT,
            eye_side TEXT,
            od_layer TEXT,
            os_layer TEXT,
            od_score TEXT,
            os_score TEXT,
            od_sph TEXT,
            os_sph TEXT,
            od_cyl TEXT,
            od_axis TEXT,
            os_cyl TEXT,
            os_axis TEXT,
            od_add TEXT,
            os_add TEXT,
            selected_symptom TEXT,
            diagnostics TEXT,
            treatments TEXT,
            eye_progression TEXT,
            last_updated TEXT
        )
        """
    )

    # Appointments table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Appointments (
            appointment_id INTEGER PRIMARY KEY,
            patient_name TEXT,
            first_name TEXT,
            surname TEXT,
            gender TEXT,
            address TEXT,
            dob TEXT,
            age INTEGER,
            mobile TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            doctor TEXT,
            created_at TEXT,
            FOREIGN KEY (patient_name) REFERENCES PatientFullInfo(patient_name) 
                ON UPDATE CASCADE ON DELETE SET NULL
        )
        """
    )

    # EyeExams table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS EyeExams (
            exam_id INTEGER PRIMARY KEY,
            patient_name TEXT,
            appointment_id INTEGER,
            prescription TEXT,
            suggested_products TEXT,
            od_sph TEXT,
            os_sph TEXT,
            od_cyl TEXT,
            od_axis TEXT,
            os_cyl TEXT,
            os_axis TEXT,
            od_add TEXT,
            os_add TEXT,
            diagnostics TEXT,
            treatments TEXT,
            eye_progression TEXT,
            saved_at TEXT,
            FOREIGN KEY (patient_name) REFERENCES PatientFullInfo(patient_name)
                ON UPDATE CASCADE ON DELETE SET NULL,
            FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id)
                ON UPDATE CASCADE ON DELETE SET NULL
        )
        """
    )

    # AllPatients table (Billing/Sales)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS AllPatients (
            bill_id INTEGER PRIMARY KEY,
            patient_name TEXT,
            appointment_id INTEGER,
            prescription TEXT,
            purchased_products TEXT,
            total_bill REAL,
            date_time TEXT,
            doctor TEXT,
            FOREIGN KEY (patient_name) REFERENCES PatientFullInfo(patient_name)
                ON UPDATE CASCADE ON DELETE SET NULL,
            FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id)
                ON UPDATE CASCADE ON DELETE SET NULL
        )
        """
    )

    # Products table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            category TEXT,
            price REAL
        )
        """
    )

    conn.commit()
    conn.close()


def seed_products():
    DIAGNOSIS_ITEMS = [
        ("Eye Drops: Artificial tears for Dry Eye", 750),
        ("Special lenses (EnChroma) and filters for Color Blindness", 900),
        ("Antibiotic drops: antihistamines for Pink Eye (Bacterial)", 700),
        ("Steroid Drops: Dexamethasone for Behçet's Disease", 650),
        ("Reading glasses for Presbyopia", 1200),
        ("Eye Drops: Lotepred for Uveitis", 650),
        ("Standard Multi-Purpose Solution", 500),
    ]
    FRAME_ITEMS = [
        ("Black Frame", 5999),
        ("Pink Frame", 5999),
        ("Navy Blue Frame", 5999),
        ("Silver Frame", 5999),
        ("Crystal/Clear Frame", 5999),
        ("Emerald Green Frame", 5999),
        ("Rose Gold Frame", 5999),
        ("Burgundy/Wine Frame", 5999),
        ("Red Frame", 5999),
        ("Matte Grey Frame", 5999),
        ("Regular White Frame and Lenses (without grades)", 2999),
    ]
    CONTACT_LENSES_COLOR = [
        ("Crystal Brown Contact Lens", 4299),
        ("Amber Brown Contact Lens", 4299),
        ("Star Brown Contact Lens", 4299),
        ("Moonlight Brown Contact Lens", 4299),
        ("Crystal Gray Contact Lens", 4299),
        ("Blue Contact Lens", 4299),
        ("Black Normal Contact Lenses", 1299),
        ("Chocolate Black Normal Contact Lenses", 1299),
    ]
    ADD_ON_ITEMS = [
        ("Anti-Reflective Coating (ARC)", 5000),
        ("Blue Light Filter (Anti-Radiation)", 1000),
        ("Transition Lenses (Photochromic)", 1980),
        ("Anti-Scratch Coating", 500),
        ("UV Protection", 500),
        ("High-Index Lenses (Strong Power)", 1500),
        ("Myopia Mgmt. Lenses", 1250),
        ("Polarized Coating", 2580),
        ("Progressive Lenses", 3000),
    ]

    conn = get_db_conn()
    cur = conn.cursor()

    product_data = []
    for name, price in DIAGNOSIS_ITEMS:
        product_data.append((name, "diagnosis", price))
    for name, price in FRAME_ITEMS:
        product_data.append((name, "frame", price))
    for name, price in ADD_ON_ITEMS:
        product_data.append((name, "addon", price))
    for name, price in CONTACT_LENSES_COLOR:
        product_data.append((name, "contact", price))

    # lagay lahat ng products
    cur.executemany(
        "INSERT OR IGNORE INTO Products (name, category, price) VALUES (?, ?, ?)",
        product_data,
    )

    # chech up fee
    cur.execute(
        "INSERT OR IGNORE INTO Products (name, category, price) VALUES (?, ?, ?)",
        (EYE_EXAM_FEE[0], "fee", EYE_EXAM_FEE[1]),
    )

    conn.commit()
    conn.close()


# for pending na status
def get_appointments_with_exam_status():
    conn = get_db_conn()
    cur = conn.cursor()

    query = """
    SELECT
        A.appointment_id,
        A.patient_name,
        A.appointment_date,
        A.appointment_time,
        CASE
            WHEN E.exam_id IS NULL THEN 'Pending'
        END AS exam_status
    FROM Appointments A
    LEFT JOIN EyeExams E
        ON A.appointment_id = E.appointment_id
    ORDER BY A.appointment_date, A.appointment_time;
    """

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    appointments = []
    for row in rows:
        appointments.append(
            {
                "appointment_id": row["appointment_id"],
                "patient_name": row["patient_name"],
                "appointment_date": row["appointment_date"],
                "appointment_time": row["appointment_time"],
                "exam_status": row["exam_status"],
            }
        )

    return appointments


seed_products()


# ------------------ Patient Form (Appointments) ------------------
class PatientForm(Frame):
    def __init__(self, parent, back_callback, refresh_callback=None):
        super().__init__(parent, bg="#dcbfca")
        self.parent = parent
        self.back_callback = back_callback
        self.refresh_callback = refresh_callback

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

    # ui para sa patient form
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
        self.dob_entry.bind(
            "<FocusOut>", self.calculate_age
        )  # compute ang edad pagkatapos magtype
        self.dob_entry.bind(
            "<KeyRelease>", self.calculate_age
        )  # real-time calculation habang nagta-type
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

        Label(
            self,
            text="--- Appointment ---",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
        ).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        Label(self, text="Appointment Today?", bg="#dcbfca").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Combobox(
            self, textvariable=self.appointment_today, values=("Yes", "No"), width=27
        ).grid(row=row, column=1, pady=5)
        self.appointment_today.trace("w", lambda *args: self.update_appointment_date())
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
        self.time_combo.bind(
            "<<ComboboxSelected>>", self.check_time_slot
        )  # bind real-time check
        row += 1

        Button(
            self, text="Add Patient", command=self.add_patient, bg="#a4c6e7", width=15
        ).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        Button(self, text="Back", command=self.back, bg="#a4c6e7", width=15).grid(
            row=row, column=0, columnspan=2, pady=10
        )

    # appointment ng check up
    def update_appointment_date(self):
        now = datetime.datetime.now()
        today = now.date()

        if self.appointment_today.get() == "Yes":
            selected_date = today
            self.appointment_date.set(selected_date.strftime("%Y-%m-%d"))

            try:
                conn = get_db_conn()
                cur = conn.cursor()
                cur.execute(
                    "SELECT appointment_time FROM Appointments WHERE appointment_date=?",
                    (selected_date.strftime("%Y-%m-%d"),),
                )
                taken_slots = [r[0] for r in cur.fetchall()]
                conn.close()
            except Exception:
                taken_slots = []

            current_minutes = now.hour * 60 + now.minute
            available_slots = []
            for t in self.all_slots:
                h, m_ampm = t.split(":")
                m, ampm = m_ampm.split()
                h, m = int(h), int(m)
                if ampm == "PM" and h != 12:
                    h += 12
                slot_minutes = h * 60 + m
                if slot_minutes > current_minutes and t not in taken_slots:
                    available_slots.append(t)

            if not available_slots:  # if lagpas na sa clinic hours
                available_slots = ["Clinic is closed"]

            self.time_slots = available_slots
            self.time_combo.config(values=self.time_slots)
            self.appointment_time.set(self.time_slots[0])

        else:  # Appointment Today = No
            appt_date_str = self.appointment_date.get().strip()
            try:
                selected_date = datetime.datetime.strptime(
                    appt_date_str, "%Y-%m-%d"
                ).date()
                if selected_date <= today:
                    self.appointment_date.set("")
                    self.time_slots = self.all_slots.copy()
                    self.time_combo.config(values=self.time_slots)
                    self.appointment_time.set("")
                    return
            except ValueError:
                selected_date = None

            if selected_date:
                try:
                    conn = get_db_conn()
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT appointment_time FROM Appointments WHERE appointment_date=?",
                        (selected_date.strftime("%Y-%m-%d"),),
                    )
                    taken_slots = [r[0] for r in cur.fetchall()]
                    conn.close()
                    available_slots = [
                        t for t in self.all_slots if t not in taken_slots
                    ]
                    if not available_slots:
                        available_slots = ["No available slots"]
                    self.time_slots = available_slots
                    self.time_combo.config(values=self.time_slots)
                    self.appointment_time.set(self.time_slots[0])
                except Exception:
                    pass

    def check_time_slot(self, event=None):
        appointment_time = self.appointment_time.get()  # date and time na gusto
        appointment_date_str = self.appointment_date.get().strip()

        # if hindi pipili nh date and time
        if appointment_time in ["", "No available slots", "Clinic is closed"]:
            return
        if not appointment_date_str:
            return
        # format ng date
        try:
            selected_date = datetime.datetime.strptime(
                appointment_date_str, "%Y-%m-%d"
            ).date()
        except ValueError:
            return
        # checking kung may naka book na sa date and oras
        try:
            conn = get_db_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM Appointments WHERE appointment_date=? AND appointment_time=?",
                (selected_date.strftime("%Y-%m-%d"), appointment_time),
            )
            if cur.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Time Slot Taken",
                    "Someone is already booked at this time. Please select another slot.",
                )
                self.appointment_time.set("")
            conn.close()
        except Exception:
            pass

    def calculate_age(self, event=None):
        dob_str = self.dob.get().strip()
        if not dob_str:
            self.age.set("")
            self.dob_entry.config(bg="white")
            return
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            self.age.set("Calculating...")  # habang nag ttype ng DOB
            self.dob_entry.config(bg="#fca1a1")
            return  # prevents from running

        # run kapag tamam yung format
        today = datetime.date.today()
        if dob > today:
            self.age.set("Invalid")  # future dates
            self.dob_entry.config(bg="#fca1a1")
            return
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        self.age.set(str(age))
        self.dob_entry.config(bg="white")

    # clear lang ng form
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

    # for adding patient
    def add_patient(self):
        fname = self.first_name.get().strip()
        lname = self.surname.get().strip()
        address = self.address.get().strip()
        dob_str = self.dob.get().strip()
        mobile = self.mobile.get().strip()
        appointment_date = self.appointment_date.get().strip()
        appointment_time = self.appointment_time.get().strip()

        # Validation
        if not fname.replace(
            " ", ""
        ).isalpha():  # dapat letters lang here if not di matutuloy process
            messagebox.showerror(
                "Error", "First Name must contain letters only and cannot be empty."
            )
            return
        if not lname.replace(
            " ", ""
        ).isalpha():  # dapat letters lang here if not di matutuloy process
            messagebox.showerror(
                "Error", "Surname must contain letters only and cannot be empty."
            )
            return
        if not address:  # bawal ang empty na address
            messagebox.showerror("Error", "Address cannot be empty.")
            return
        try:
            dob = datetime.datetime.strptime(
                dob_str, "%Y-%m-%d"
            ).date()  # bawal futute date and wrong format
            if dob > datetime.date.today():
                messagebox.showerror("Error", "DOB cannot be a future date.")
                return
        except ValueError:
            messagebox.showerror("Error", "DOB must be in YYYY-MM-DD format.")
            return
        if not (
            mobile.isdigit() and len(mobile) == 11
        ):  # 11 digits lang like here sa pelepens na mobile num
            messagebox.showerror("Error", "Mobile number must be exactly 11 digits.")
            return
        try:
            appt_date_obj = datetime.datetime.strptime(  # bawal past date
                appointment_date, "%Y-%m-%d"
            ).date()
            if appt_date_obj < datetime.date.today():
                messagebox.showerror("Error", "Appointment date cannot be in the past.")
                return
        except ValueError:
            messagebox.showerror(  # raise error na dapat ay same format
                "Error", "Appointment date must be in YYYY-MM-DD format."
            )
            return
        if appt_date_obj < datetime.date.today():
            messagebox.showerror("Error", "Appointment date cannot be in the past.")
            return

        #  if appointment today = No, date cannot be today
        if (
            self.appointment_today.get() == "No"
            and appt_date_obj == datetime.date.today()
        ):
            messagebox.showerror("Error", "Appointment date must be a future date.")
            return
        if (
            appointment_time == "Clinic is closed"
        ):  # if lagpas 4 na since hanggang 4:30 lang clinic
            messagebox.showerror(
                "Cannot Add Patient", "Cannot Add Patient. Clinic is closed"
            )
            return
        if appointment_time in ["No available slots", ""]:
            messagebox.showerror("Error", "No available time slots for this date.")
            return

        # Double booking check and lagay sa db
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM Appointments WHERE appointment_date=? AND appointment_time=?",
            (appointment_date, appointment_time),
        )
        if (
            cur.fetchone()[0] > 0
        ):  # check if naka may ibang naka booked na sa time na yon
            conn.close()
            messagebox.showerror(
                "Error", "Selected time is already booked. Please select another slot."
            )
            return
        # for successful na fill out
        patient_name = f"{fname} {lname}"
        cur.execute(
            """
            INSERT INTO Appointments (first_name, surname, patient_name, gender, address, dob, age, mobile, appointment_date, appointment_time, doctor, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                fname,
                lname,
                patient_name,
                self.gender.get(),
                address,
                dob_str,
                int(self.age.get() or 0),
                mobile,
                appointment_date,
                appointment_time,
                "Leanne Mendoza",  # default since ako lang doctor
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Patient Added",
            f"Patient {patient_name} added for {appointment_date} at {appointment_time}",
        )
        self.clear_form()
        if self.refresh_callback:
            self.refresh_callback()

    def back(self):  # para ma punta sa main window
        self.destroy()
        self.back_callback()


# ------------------ Appointment List frame that leads to EyeExam ------------------
class AppointmentListForExam(Frame):
    def __init__(self, parent, back_callback, open_exam_callback):
        super().__init__(parent, bg="#dcbfca")
        self.parent = parent
        self.back_callback = back_callback
        self.open_exam_callback = open_exam_callback
        self.build_ui()
        self.load_appointments()  # appointments mula sa database at ipapakita sa list

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

    # lagay dito yung mga patients tapos kung mga pending kapag wala pa silang eye exam, pero mostly pending here kasi mag start pa lang exam
    def load_appointments(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        conn = get_db_conn()
        cur = conn.cursor()
        # naka sequence yung appointment based sa date and time nila. not kung sino yung nag aappoint
        query = """
        SELECT
            A.*,
            CASE
                WHEN E.patient_name IS NULL THEN 'Pending'
            END AS exam_status
        FROM Appointments A
        LEFT JOIN EyeExams E ON A.patient_name = E.patient_name
        ORDER BY appointment_date,
            CASE
                WHEN appointment_time LIKE '%AM' THEN
                    printf('%02d:%02d',
                        CAST(substr(appointment_time, 1, instr(appointment_time, ':')-1) AS INTEGER),
                        CAST(substr(appointment_time, instr(appointment_time, ':')+1, 2) AS INTEGER))
                ELSE
                    printf('%02d:%02d',
                        CAST(substr(appointment_time, 1, instr(appointment_time, ':')-1) AS INTEGER)+12,
                        CAST(substr(appointment_time, instr(appointment_time, ':')+1, 2) AS INTEGER))
            END
        """
        cur.execute(query)
        # get sa db ng patients the display sa table in sequence
        for row in cur.fetchall():
            self.tree.insert(
                "",
                "end",
                values=(
                    row["patient_name"],
                    row["age"],
                    row["mobile"],
                    row["appointment_date"],
                    row["appointment_time"],
                    row["doctor"],
                    row["exam_status"],
                ),
            )

        conn.close()

    # select muna ng patient bago i start eye exam
    def start_exam(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Patient", "Please select a patient first.")
            return
        patient_name = self.tree.item(sel[0], "values")[0]
        conn = get_db_conn()
        cur = conn.cursor()
        # Fetch complete appointment record
        cur.execute("SELECT * FROM Appointments WHERE patient_name=?", (patient_name,))
        appt = cur.fetchone()
        conn.close()
        if not appt:
            messagebox.showerror("Error", "Selected patient not found.")
            return
        self.open_exam_callback(appt)


# ------------------ Eye Exam Window ------------------
class EyeExamsWindow(Frame):
    def __init__(
        self,
        parent,
        back_callback,
        appointment_row=None,
        proceed_to_products_callback=None,
    ):
        super().__init__(parent, bg="#dcbfca")
        self.back_callback = back_callback
        self.appointment_row = appointment_row
        self.proceed_to_products_callback = proceed_to_products_callback

        # eye side and symptom selection
        self.eye_side = StringVar(value="Both")
        self.selected_symptom = StringVar(value="")
        self.layers = list(range(1, 12))
        self.layer_scores = {
            1: "20/200",
            2: "20/100",
            3: "20/70",
            4: "20/50",
            5: "20/40",
            6: "20/30",
            7: "20/25",
            8: "20/20",
            9: "20/15",
            10: "20/13",
            11: "20/10",
        }
        self.od_layer = StringVar(value="")
        self.os_layer = StringVar(value="")
        self.od_score_var = StringVar(value="")
        self.os_score_var = StringVar(value="")
        self.od_sph = StringVar()
        self.os_sph = StringVar()
        self.od_cyl = StringVar()
        self.os_cyl = StringVar()
        self.od_axis = StringVar()
        self.os_axis = StringVar()
        self.od_add = StringVar()
        self.os_add = StringVar()

        # Build UI
        self.build_window()

        # score after makapili ng layer
        self.od_layer.trace("w", self.update_scores)
        self.os_layer.trace("w", self.update_scores)
        self.eye_side.trace("w", self.update_eye_visibility)
        self.selected_symptom.trace("w", self.update_scores)

        self.update_eye_visibility()

        if appointment_row:
            self.prefill_from_appointment(appointment_row)

    def build_window(self):
        main_container = Frame(self, bg="#dcbfca")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.left_panel = Frame(main_container, bg="#dcbfca")
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        right_panel = Frame(main_container, bg="#dcbfca")
        right_panel.pack(side="left", fill="both", expand=True)

        # Eye Side Selector
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

        # Visual Acuity & Refraction Section
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
            text="Eye Progression:",
            bg="#dcbfca",
            font=("Times New Roman", 10, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(5, 0))
        self.eye_progression_text = Text(right_panel, height=5, width=50)
        self.eye_progression_text.pack(fill="x", pady=(0, 5))

        # Buttons
        button_frame = Frame(right_panel, bg="#dcbfca")
        button_frame.pack(fill="x", pady=10)
        Button(
            button_frame, text="Diagnose", command=self.auto_diagnose, bg="#a4c6e7"
        ).pack(side="left", padx=5)
        Button(
            button_frame, text="Save Exam", command=self.save_exam, bg="#a4c6e7"
        ).pack(side="right", padx=5)
        Button(
            button_frame, text="Back", command=self.back_callback, bg="#a4c6e7"
        ).pack(side="right", padx=5)

    def prefill_from_appointment(self, appt_row):
        self.patient_label.config(
            text=f"{appt_row['patient_name']} (Age: {appt_row['age']}, Mobile: {appt_row['mobile']})"
        )

    def update_eye_visibility(self, *args):
        eye_side = self.eye_side.get()
        vis_od = eye_side in ["Right", "Both"]
        vis_os = eye_side in ["Left", "Both"]

        if vis_od:
            self.od_layer_frame.pack(side="top", fill="x", padx=5, pady=2)
            self.od_ref_frame.pack(side="top", fill="x", padx=5, pady=2)
        else:
            self.od_layer_frame.pack_forget()
            self.od_ref_frame.pack_forget()

        if vis_os:
            self.os_layer_frame.pack(side="top", fill="x", padx=5, pady=2)
            self.os_ref_frame.pack(side="top", fill="x", padx=5, pady=2)
        else:
            self.os_layer_frame.pack_forget()
            self.os_ref_frame.pack_forget()

    # for astig only
    def calculate_cyl_axis_single(self, layer_val):
        if layer_val in [1, 2]:
            return "-1.50", 90
        elif layer_val in [3, 4]:
            return "-1.00", 180
        elif layer_val in [5, 6]:
            return "-0.50", 45
        else:
            return "0.00", 0

    def suggest_sph_from_layer(self, layer):
        mapping = {
            1: -4.0,
            2: -3.0,
            3: -2.5,
            4: -2.0,
            5: -1.5,
            6: -1.0,
            7: -0.5,
            8: 0.0,
            9: 0.5,
            10: 1.0,
            11: 1.5,
        }
        return f"{mapping.get(layer, 0.0):.2f}"

    def update_add_suggestion(self):
        for var, layer in [
            (self.od_add, self.od_layer.get()),
            (self.os_add, self.os_layer.get()),
        ]:
            if not layer:
                continue
            try:
                layer = int(layer)
            except ValueError:
                continue

            if layer <= 3:
                var.set("1.50")
            elif layer <= 5:
                var.set("1.00")
            else:
                var.set("0.00")

    def update_scores(self, *args):
        def safe_float(val):
            try:
                return float(val)
            except:
                return 0.0

        try:
            od_layer_val = (
                int(self.od_layer.get()) if self.od_layer.get().isdigit() else None
            )
        except ValueError:
            od_layer_val = None
        try:
            os_layer_val = (
                int(self.os_layer.get()) if self.os_layer.get().isdigit() else None
            )
        except ValueError:
            os_layer_val = None

        if od_layer_val:
            self.od_score_var.set(self.layer_scores[od_layer_val])
            self.od_sph.set(self.suggest_sph_from_layer(od_layer_val))
        else:
            self.od_score_var.set("")
            self.od_sph.set("")

        if os_layer_val:
            self.os_score_var.set(self.layer_scores[os_layer_val])
            self.os_sph.set(self.suggest_sph_from_layer(os_layer_val))
        else:
            self.os_score_var.set("")
            self.os_sph.set("")

        self.update_add_suggestion()

        # astigmatism handling
        if self.selected_symptom.get() == "Blurry or distorted vision":
            if od_layer_val:
                od_cyl, od_axis = self.calculate_cyl_axis_single(od_layer_val)
                self.od_cyl.set(od_cyl)
                self.od_axis.set(str(od_axis))
                self.od_cyl_dropdown.config(state="normal")
                self.od_axis_dropdown.config(state="normal")
            if os_layer_val:
                os_cyl, os_axis = self.calculate_cyl_axis_single(os_layer_val)
                self.os_cyl.set(os_cyl)
                self.os_axis.set(str(os_axis))
                self.os_cyl_dropdown.config(state="normal")
                self.os_axis_dropdown.config(state="normal")
        else:
            self.od_cyl.set("")
            self.od_axis.set("")
            self.os_cyl.set("")
            self.os_axis.set("")
            self.od_cyl_dropdown.config(state="disabled")
            self.od_axis_dropdown.config(state="disabled")
            self.os_cyl_dropdown.config(state="disabled")
            self.os_axis_dropdown.config(state="disabled")

    def auto_diagnose(self):
        self.diagnostic_textbox.delete("1.0", "end")
        self.treatment_textbox.delete("1.0", "end")
        self.eye_progression_text.delete("1.0", "end")

        selected_eye_side = self.eye_side.get()
        selected_symptom = self.selected_symptom.get()

        od_layer_val = (
            int(self.od_layer.get()) if self.od_layer.get().isdigit() else None
        )
        os_layer_val = (
            int(self.os_layer.get()) if self.os_layer.get().isdigit() else None
        )

        od_sph_val = float(self.od_sph.get() or 0.0)
        os_sph_val = float(self.os_sph.get() or 0.0)
        od_cyl_val = float(self.od_cyl.get() or 0.0)
        os_cyl_val = float(self.os_cyl.get() or 0.0)

        diag_list = []
        treatments_list = []
        progression_list = []
        od_issue = False
        os_issue = False
        astigmatism_selected = (
            selected_symptom == eye_conditions["Astigmatism"]["symptom"]
        )

        # OD
        if selected_eye_side in ["Right", "Both"]:
            if od_cyl_val != 0.0 or astigmatism_selected:
                diag_list.append("OD: Astigmatism")
                progression_list.append("OD: Becoming blurry")
                od_issue = True
            elif od_sph_val < 0:
                diag_list.append("OD: Myopia (Nearsightedness)")
                progression_list.append("OD: Becoming blurry")
                od_issue = True
            elif od_sph_val > 0:
                diag_list.append("OD: Hyperopia (Farsightedness)")
                progression_list.append("OD: Becoming blurry")
                od_issue = True

            if not od_issue and od_layer_val == 8:
                progression_list.append("OD: No significant progression noted.")

            if od_issue:
                # Add treatments if any refractive issue detected
                treatments_list.append("OD: Glasses / Contact lenses")

        # OS
        if selected_eye_side in ["Left", "Both"]:
            if os_cyl_val != 0.0 or astigmatism_selected:
                diag_list.append("OS: Astigmatism")
                progression_list.append("OS: Becoming blurry")
                os_issue = True
            elif os_sph_val < 0:
                diag_list.append("OS: Myopia (Nearsightedness)")
                progression_list.append("OS: Becoming blurry")
                os_issue = True
            elif os_sph_val > 0:
                diag_list.append("OS: Hyperopia (Farsightedness)")
                progression_list.append("OS: Becoming blurry")
                os_issue = True

            if not os_issue and os_layer_val == 8:
                progression_list.append("OS: No significant progression noted.")

            if os_issue:
                # Add treatments if any refractive issue detected
                treatments_list.append("OS: Glasses / Contact lenses")

        # NON-REFRACTIVE SYMPTOMS
        if selected_symptom and not astigmatism_selected:
            condition = symptom_to_medical[selected_symptom]
            treat = eye_conditions[condition]["treatment"]
            if selected_eye_side == "Right":
                diag_list.append(f"OD: {condition}")
                treatments_list.append(f"OD: {treat}")
            elif selected_eye_side == "Left":
                diag_list.append(f"OS: {condition}")
                treatments_list.append(f"OS: {treat}")
            else:
                diag_list.append(f"OD & OS: {condition}")
                treatments_list.append(f"OD & OS: {treat}")

            if eye_conditions[condition].get("affects_eye_grade", False):
                progression_list.append(eye_conditions[condition]["suggestion"])
            else:
                if selected_eye_side == "Right":
                    progression_list.append("OD: Non-refractive issue detected.")
                elif selected_eye_side == "Left":
                    progression_list.append("OS: Non-refractive issue detected.")
                else:
                    progression_list.append("OD: Non-refractive issue detected.")
                    progression_list.append("OS: Non-refractive issue detected.")

        # PRESCRIPTION TABLE
        prescription_needed = od_issue or os_issue
        if prescription_needed:
            treatments_list = [
                t
                for t in treatments_list
                if t
                not in ["OD: Glasses / Contact lenses", "OS: Glasses / Contact lenses"]
            ]

            treatments_list.append("--- Eye Grade ---")
            treatments_list.append("Eye\tSPH\tCYL\tAXIS\tADD")
            if od_issue and selected_eye_side in ["Right", "Both"]:
                treatments_list.append(
                    f"OD\t{self.od_sph.get()}\t{self.od_cyl.get() or ''}\t{self.od_axis.get() or ''}\t{self.od_add.get()}"
                )
            if os_issue and selected_eye_side in ["Left", "Both"]:
                treatments_list.append(
                    f"OS\t{self.os_sph.get()}\t{self.os_cyl.get() or ''}\t{self.os_axis.get() or ''}\t{self.os_add.get()}"
                )
            if (
                od_issue
                and os_issue
                and "OD & OS: Glasses / Contact lenses" not in treatments_list
            ):
                treatments_list.insert(0, "OD & OS: Glasses / Contact lenses")
            elif (
                od_issue
                and not os_issue
                and "OD: Glasses / Contact lenses" not in treatments_list
            ):
                treatments_list.insert(0, "OD: Glasses / Contact lenses")
            elif (
                os_issue
                and not od_issue
                and "OS: Glasses / Contact lenses" not in treatments_list
            ):
                treatments_list.insert(0, "OS: Glasses / Contact lenses")

        progression_list = list(dict.fromkeys(progression_list))

        # --- UPDATE UI ---
        self.diagnostic_textbox.delete("1.0", "end")
        self.diagnostic_textbox.insert("end", "\n".join(diag_list))
        self.treatment_textbox.delete("1.0", "end")
        self.treatment_textbox.insert("end", "\n".join(treatments_list))
        self.eye_progression_text.delete("1.0", "end")
        self.eye_progression_text.insert("end", "\n".join(progression_list))

    def save_exam(self):
        if not self.appointment_row:
            messagebox.showerror("Error", "No patient selected for exam.")
            return

        patient_name = self.appointment_row["patient_name"]
        first_name = self.appointment_row["first_name"]
        surname = self.appointment_row["surname"]
        gender = self.appointment_row["gender"]
        address = self.appointment_row["address"]
        dob = self.appointment_row["dob"]
        age = self.appointment_row["age"]
        mobile = self.appointment_row["mobile"]
        created_at = self.appointment_row["created_at"]

        diagnostics = self.diagnostic_textbox.get("1.0", "end").strip()
        treatments = self.treatment_textbox.get("1.0", "end").strip()
        eye_progression = self.eye_progression_text.get("1.0", "end").strip()
        selected_symptom = self.selected_symptom.get().strip()

        # must have input in form
        if not (diagnostics or treatments or eye_progression or selected_symptom):
            messagebox.showerror("Error", "Please fill out the form.")
            return

        suggested = []
        txt_lines = treatments.splitlines()

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT name FROM Products")
        product_names = [row["name"] for row in cur.fetchall()]

        for line in txt_lines:
            line = line.strip()
            for product in product_names:
                if product.lower() in line.lower():
                    suggested.append(product)
                    break

        saved_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur.execute(
                """
                INSERT INTO EyeExams (patient_name, appointment_id, prescription, suggested_products,
                    od_sph, os_sph, od_cyl, od_axis, os_cyl, os_axis, od_add, os_add,
                    diagnostics, treatments, eye_progression, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_name,
                    created_at,
                    treatments,
                    ", ".join(suggested),
                    self.od_sph.get(),
                    self.os_sph.get(),
                    self.od_cyl.get(),
                    self.od_axis.get(),
                    self.os_cyl.get(),
                    self.os_axis.get(),
                    self.od_add.get(),
                    self.os_add.get(),
                    diagnostics,
                    treatments,
                    eye_progression,
                    saved_at,
                ),
            )

            cur.execute(
                """
                INSERT INTO PatientFullInfo (
                    patient_name, first_name, surname, gender, address, dob, age, mobile,
                    eye_side, od_layer, os_layer, od_score, os_score,
                    od_sph, os_sph, od_cyl, od_axis, os_cyl, os_axis, od_add, os_add,
                    selected_symptom, diagnostics, treatments, eye_progression, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(patient_name) DO UPDATE SET 
                    first_name=excluded.first_name, surname=excluded.surname, gender=excluded.gender, address=excluded.address,
                    dob=excluded.dob, age=excluded.age, mobile=excluded.mobile,
                    eye_side=excluded.eye_side, od_layer=excluded.od_layer, os_layer=excluded.os_layer,
                    od_score=excluded.od_score, os_score=excluded.os_score,
                    od_sph=excluded.od_sph, os_sph=excluded.os_sph, od_cyl=excluded.od_cyl, od_axis=excluded.od_axis,
                    os_cyl=excluded.os_cyl, os_axis=excluded.os_axis, od_add=excluded.od_add, os_add=excluded.os_add,
                    selected_symptom=excluded.selected_symptom, diagnostics=excluded.diagnostics,
                    treatments=excluded.treatments, eye_progression=excluded.eye_progression, last_updated=excluded.last_updated
                """,
                (
                    patient_name,
                    first_name,
                    surname,
                    gender,
                    address,
                    dob,
                    age,
                    mobile,
                    self.eye_side.get(),
                    self.od_layer.get(),
                    self.os_layer.get(),
                    self.od_score_var.get(),
                    self.os_score_var.get(),
                    self.od_sph.get(),
                    self.os_sph.get(),
                    self.od_cyl.get(),
                    self.od_axis.get(),
                    self.os_cyl.get(),
                    self.os_axis.get(),
                    self.od_add.get(),
                    self.os_add.get(),
                    selected_symptom,
                    diagnostics,
                    treatments,
                    eye_progression,
                    saved_at,
                ),
            )

            # Remove appointment record since exam is saved
            cur.execute(
                "DELETE FROM Appointments WHERE patient_name=? AND created_at=?",
                (patient_name, created_at),
            )

            conn.commit()

            messagebox.showinfo(
                "Exam Saved",
                f"Eye exam for {patient_name} saved successfully. Proceeding to billing.",
            )

            if self.proceed_to_products_callback:
                self.proceed_to_products_callback(patient_name)
            else:
                self.back_callback()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save exam: {e}")
            conn.rollback()

        finally:
            conn.close()


# ------------------ Products and Bills Window ------------------
class Window3(Frame):
    def __init__(self, parent, back_callback, refresh_allpatients_callback):
        super().__init__(parent, bg="#dcbfca")
        self.back_callback = back_callback
        self.refresh_allpatients_callback = refresh_allpatients_callback
        self.selected_patient = None
        self.selected_items = {}
        self.addon_vars = {}
        self.load_products_from_db()
        self.frame_color_var = StringVar()
        self.contact_color_var = StringVar()
        self.diag_var = StringVar()
        self.build_ui()
        self.load_patients_tree()

    def load_products_from_db(self):
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT name, category, price FROM Products ORDER BY category, name"
        )
        rows = cur.fetchall()
        conn.close()
        self.products_by_category = {
            "diagnosis": [],
            "frame": [],
            "addon": [],
            "fee": [],
            "contact": [],
        }
        for name, cat, price in rows:
            if cat not in self.products_by_category:
                self.products_by_category[cat] = []
            self.products_by_category[cat].append((name, price))

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

        # product selection
        middle_frame = Frame(self, bg="#dcbfca")
        middle_frame.pack(fill="x", padx=10, pady=10)

        left_mid_frame = Frame(middle_frame, bg="#dcbfca")
        left_mid_frame.pack(side="left", fill="y", padx=(0, 10))

        right_mid_frame = Frame(middle_frame, bg="#dcbfca")
        right_mid_frame.pack(side="left", fill="both", expand=True)

        # Diagnosis & Frames
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

        # add ons
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

        # for Receipt
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

    def load_patients_tree(self):
        for r in self.patient_tree.get_children():
            self.patient_tree.delete(r)

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT patient_name, saved_at FROM EyeExams ORDER BY saved_at")
        rows = cur.fetchall()
        conn.close()

        if not rows:
            self.patient_tree.insert("", "end", values=("", "No Patient found..."))
        else:
            for row in rows:
                self.patient_tree.insert(
                    "", "end", values=(row["patient_name"], row["saved_at"])
                )

    def search_patient(self):
        name = self.search_var.get().strip().lower()
        for r in self.patient_tree.get_children():
            self.patient_tree.delete(r)

        conn = get_db_conn()
        cur = conn.cursor()
        if name == "":
            cur.execute("SELECT patient_name, saved_at FROM EyeExams ORDER BY saved_at")
        else:
            cur.execute(
                "SELECT patient_name, saved_at FROM EyeExams WHERE LOWER(patient_name) LIKE ? ORDER BY saved_at",
                (f"%{name}%",),
            )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            self.patient_tree.insert("", "end", values=("", "No Patient found..."))
        else:
            for row in rows:
                self.patient_tree.insert(
                    "", "end", values=(row["patient_name"], row["saved_at"])
                )

    def on_patient_select(self, event):
        sel = self.patient_tree.selection()
        if not sel:
            self.selected_patient = None
            self.clear_ui()
            return

        patient_name = self.patient_tree.item(sel[0], "values")[0]
        saved_at = self.patient_tree.item(sel[0], "values")[1]

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM EyeExams WHERE patient_name=? AND saved_at=?",
            (patient_name, saved_at),
        )
        self.selected_patient = cur.fetchone()
        conn.close()

        self.clear_ui(keep_patient=True)
        self.load_suggested_products()
        self.update_receipt()

    def load_suggested_products(self):
        if not self.selected_patient:
            return

        suggested_products_str = self.selected_patient["suggested_products"]
        if not suggested_products_str:
            return

        suggested_list = [p.strip() for p in suggested_products_str.split(",")]

        # get product names without price string for dropdown matching
        def get_product_name_without_price(product_list):
            return [name for name, price in product_list]

        # Diagnosis Products
        diag_names = get_product_name_without_price(
            self.products_by_category["diagnosis"]
        )
        for product_name in suggested_list:
            if product_name in diag_names:
                for name, price in self.products_by_category["diagnosis"]:
                    if name == product_name:
                        self.diag_var.set(f"{name} - \u20b1{price}")
                        self.selected_items[name] = price
                        break

        # Frames (assume only one suggested frame or contact lens)
        frame_names = get_product_name_without_price(self.products_by_category["frame"])
        for product_name in suggested_list:
            if product_name in frame_names:
                for name, price in self.products_by_category["frame"]:
                    if name == product_name:
                        self.frame_color_var.set(f"{name} - \u20b1{price}")
                        self.selected_items[name] = price
                        break

        # Contact Lenses
        contact_names = get_product_name_without_price(
            self.products_by_category["contact"]
        )
        for product_name in suggested_list:
            if product_name in contact_names:
                for name, price in self.products_by_category["contact"]:
                    if name == product_name:
                        self.contact_color_var.set(f"{name} - \u20b1{price}")
                        self.selected_items[name] = price
                        break

        # Add-ons
        addon_names = get_product_name_without_price(self.products_by_category["addon"])
        for product_name in suggested_list:
            if product_name in addon_names:
                if product_name in self.addon_vars:
                    self.addon_vars[product_name].set(1)
                    # Find price and add to selected_items
                    for name, price in self.products_by_category["addon"]:
                        if name == product_name:
                            self.selected_items[name] = price
                            break

        # Medical checkup fee
        fee_name, fee_price = EYE_EXAM_FEE
        self.selected_items[fee_name] = fee_price

    def select_diagnosis_item(self, *args):
        chosen = self.diag_var.get()
        # Clear previous diagnosis selections
        for name, _ in self.products_by_category["diagnosis"]:
            self.selected_items.pop(name, None)

        if chosen.startswith("Select"):
            self.update_receipt()
            return

        if " - \u20b1" in chosen:
            name, price_str = chosen.split(" - \u20b1")
            price = int(float(price_str.replace(",", "")))
            self.selected_items[name] = price
            self.update_receipt()

    def select_frame_color(self, *args):
        chosen = self.frame_color_var.get()
        # Clear previous frame selections
        for name, _ in self.products_by_category["frame"]:
            self.selected_items.pop(name, None)

        if chosen.startswith("Select"):
            self.update_receipt()
            return

        if " - \u20b1" in chosen:
            name, price_str = chosen.split(" - \u20b1")
            price = int(float(price_str.replace(",", "")))
            self.selected_items[name] = price
            self.update_receipt()

    def select_contact_color(self, *args):
        chosen = self.contact_color_var.get()
        # Clear previous contact selections
        for name, _ in self.products_by_category["contact"]:
            self.selected_items.pop(name, None)

        if chosen.startswith("Select"):
            self.update_receipt()
            return

        if " - \u20b1" in chosen:
            name, price_str = chosen.split(" - \u20b1")
            price = int(float(price_str.replace(",", "")))
            self.selected_items[name] = price
            self.update_receipt()

    def toggle_item_addon(self, name, price, var):
        if var.get() == 1:
            self.selected_items[name] = price
        else:
            self.selected_items.pop(name, None)
        self.update_receipt()

    def update_receipt(self):
        self.receipt_text.delete(1.0, END)
        if not self.selected_patient:
            return

        # Patient name and appointment time
        patient_name = self.selected_patient["patient_name"]
        appointment_time = self.selected_patient["saved_at"]
        diagnostics = self.selected_patient["diagnostics"]
        treatments = self.selected_patient["treatments"]

        self.receipt_text.insert(END, f"Patient: {patient_name}\n")
        self.receipt_text.insert(END, f"Appointment Date/Time: {appointment_time}\n")
        self.receipt_text.insert(END, "-" * 45 + "\n")

        if diagnostics:
            self.receipt_text.insert(END, f"Diagnosis:\n{diagnostics}\n\n")
        if treatments:
            self.receipt_text.insert(END, f"Treatments / Products:\n{treatments}\n\n")

        total = 0

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT name, price FROM Products")
        product_price_map = {
            row["name"].strip().lower(): row["price"] for row in cur.fetchall()
        }
        conn.close()

        fee_name, fee_price = EYE_EXAM_FEE
        self.selected_items[fee_name] = fee_price

        sorted_items = sorted(self.selected_items.items(), key=lambda item: item[0])

        for name, price in sorted_items:
            key = name.strip().lower()
            price_from_db = product_price_map.get(key)

            if price == 0 or price is None:
                if price_from_db is not None:
                    price = price_from_db
                self.selected_items[name] = price  # update price in selected_items

            # Use the most recent price if available
            price_to_display = price if price is not None else price_from_db

            if price_to_display is not None:
                self.receipt_text.insert(
                    END, f"{name:<30} \u20b1{price_to_display:,.2f}\n"
                )
                total += price_to_display
            else:
                self.receipt_text.insert(
                    END, f"{name:<30} \u20b10.00 (Price not found)\n"
                )

        self.receipt_text.insert(END, "-" * 45 + "\n")
        self.receipt_text.insert(END, f"TOTAL: \u20b1{total:,.2f}\n")
        self.receipt_text.insert(END, "-" * 45 + "\n")

    def save_bill(self):
        if not self.selected_patient:
            messagebox.showerror("Error", "Please select a patient first.")
            return

        total_bill = 0
        purchased_products = []
        patient_name = self.selected_patient["patient_name"]
        appointment_id = self.selected_patient["appointment_id"]

        for name, price in self.selected_items.items():
            if price is None or price == 0:
                conn_p = get_db_conn()
                cur_p = conn_p.cursor()
                cur_p.execute("SELECT price FROM Products WHERE name=?", (name,))
                db_price = cur_p.fetchone()
                conn_p.close()
                price = db_price["price"] if db_price else 0

            total_bill += price
            purchased_products.append(name)

        if total_bill == 0:
            messagebox.showerror("Error", "Total bill is zero. Please select products.")
            return

        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_conn()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO AllPatients (patient_name, appointment_id, prescription, purchased_products, total_bill, date_time, doctor)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_name,
                    appointment_id,
                    self.selected_patient["prescription"],
                    ", ".join(purchased_products),
                    total_bill,
                    date_time,
                    "Leanne Mendoza",
                ),
            )

            cur.execute(
                "DELETE FROM EyeExams WHERE patient_name=? AND saved_at=?",
                (patient_name, self.selected_patient["saved_at"]),
            )

            conn.commit()

            messagebox.showinfo(
                "Bill Saved", f"Bill for {patient_name} saved successfully."
            )
            self.clear_ui()
            self.load_patients_tree()
            if self.refresh_allpatients_callback:
                self.refresh_allpatients_callback()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save bill: {e}")
            conn.rollback()

        conn.close()

    def clear_ui(self, keep_patient=False):
        if not keep_patient:
            self.selected_patient = None
        self.selected_items = {}
        self.frame_color_var.set("Select Frame Color")
        self.contact_color_var.set("Select Contact Color")
        self.diag_var.set("Select Diagnosis Product")
        for var in self.addon_vars.values():
            var.set(0)
        self.receipt_text.delete(1.0, END)
        if not keep_patient:
            self.patient_tree.selection_remove(self.patient_tree.selection())


# ------------------ AllPatients Window ------------------
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

    def load_all_patients(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT patient_name, total_bill FROM AllPatients ORDER BY date_time DESC"
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            self.tree.insert("", "end", values=("", "No Patient found...", ""))
        else:
            for row in rows:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["patient_name"],
                        f"\u20b1{row['total_bill']:,.2f}",
                        "Completed",
                    ),
                )

        conn.close()

    def search(self):
        self.load_all_patients()
        search_text = self.search_var.get().strip().lower()
        if not search_text:
            return

        for item in self.tree.get_children():
            name = self.tree.item(item, "values")[0].lower()
            if search_text not in name:
                self.tree.delete(item)

    def view_update(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                "Selection Error", "Please select a patient first to view the receipt."
            )
            return

        patient_name = self.tree.item(sel[0], "values")[0]

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM AllPatients WHERE patient_name=?", (patient_name,))
        rec = cur.fetchone()

        if not rec:
            messagebox.showerror("Error", "Patient record not found.")
            conn.close()
            return

        # Fetch all product prices
        product_prices = {}
        cur.execute("SELECT name, price FROM Products")
        for row in cur.fetchall():
            product_prices[row["name"].strip()] = row["price"]

        product_list_raw = rec["purchased_products"].split(",")
        product_list = [p.strip() for p in product_list_raw]

        MEDICAL_CHECKUP_NAME = "Medical Checkup Fee"
        if MEDICAL_CHECKUP_NAME.strip() in product_list:
            product_list.remove(MEDICAL_CHECKUP_NAME.strip())
        product_list.insert(0, MEDICAL_CHECKUP_NAME.strip())

        self.details_text.delete("1.0", END)
        self.details_text.insert(END, "=" * 134 + "\n")
        self.details_text.insert(END, f"Patient: {patient_name}\n")
        self.details_text.insert(
            END,
            f"Appointment Date/Time: {rec['date_time'] if 'date_time' in rec.keys() else 'N/A'}\n",
        )
        self.details_text.insert(END, "-" * 134 + "\n")

        if product_list:
            self.details_text.insert(END, "Purchased Products / Treatments:\n")
            total_calc = 0
            for name in product_list:
                price = product_prices.get(name, 0)
                self.details_text.insert(END, f"{name:<60} \u20b1{price:,.2f}\n")
                total_calc += price

            self.details_text.insert(END, "\n")
            self.details_text.insert(END, f"TOTAL: \u20b1{total_calc:,.2f}\n")

        self.details_text.insert(END, "-" * 134 + "\n")
        self.details_text.insert(
            END,
            f"Doctor: {rec['doctor'] if 'doctor' in rec.keys() else 'Leanne Mendoza'}\n",
        )
        conn.close()

    def view_patient(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                "Selection Error",
                "Please select a patient first to view the patient info.",
            )
            return

        patient_name = self.tree.item(sel[0], "values")[0]

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM PatientFullInfo WHERE patient_name=?", (patient_name,)
        )
        rec = cur.fetchone()

        if not rec:
            messagebox.showerror("Error", "Patient full info not found.")
            conn.close()
            return

        self.details_text.delete("1.0", END)
        self.details_text.insert(END, "=" * 134 + "\n")
        self.details_text.insert(END, f"Full Patient Information for: {patient_name}\n")
        self.details_text.insert(END, "=" * 134 + "\n")

        for key in rec.keys():
            self.details_text.insert(
                END, f"{key.replace('_', ' ').title()}: {rec[key]}\n"
            )

        self.details_text.insert(END, "=" * 134 + "\n")
        conn.close()

    def delete_record(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a record to delete.")
            return
        patient_name = self.tree.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirm", "Delete this patient record?"):
            return
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM AllPatients WHERE patient_name=?", (patient_name,))
        cur.execute("DELETE FROM PatientFullInfo WHERE patient_name=?", (patient_name,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Record deleted.")
        self.load_all_patients()


# ------------------ Main Application ------------------
class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("OPTICare - Dra. Leanne Mendoza")
        self.root.geometry("1000x650")
        self.root.config(bg="#dcbfca")

        # Left side
        self.left_panel = Frame(root, bg="#a4c6e7")
        self.left_panel.pack(side="left", fill="y")

        #  logo
        try:
            # Placeholder for image loading, assuming file is available
            img = Image.open("logo.png").resize((200, 150))
            self.logo = ImageTk.PhotoImage(img)
            Label(self.left_panel, image=self.logo, bg="#a4c6e7").pack(pady=10)
        except Exception:
            Label(
                self.left_panel,
                text="OPTICare",
                font=("Times New Roman", 24, "bold"),
                bg="#a4c6e7",
                fg="black",
            ).pack(pady=20, padx=10)

        # Buttons
        buttons = [
            "APPOINTMENTS",
            "EYE EXAMS",
            "PRODUCTS AND BILLS",
            "ALL PATIENTS",
            "EXIT",
        ]
        for btn_text in buttons:
            Button(
                self.left_panel,
                text=btn_text,
                command=lambda t=btn_text: self.on_button_click(t),
                bg="#e7c6e4",
                fg="black",
                font=("Times New Roman", 10),
                width=20,
                height=2,
            ).pack(pady=5, padx=10)

        self.center_panel = Frame(root, bg="#dcbfca")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.show_default_image()

    def clear_center(self):
        for widget in self.center_panel.winfo_children():
            widget.destroy()

    def show_default_image(self):
        self.clear_center()
        wrapper = Frame(self.center_panel, bg="#dcbfca")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        Label(
            wrapper,
            text="Welcome to OPTICare\t \t \t           Dra. Leanne Mendoza",
            font=("Times New Roman", 22, "bold"),
            bg="#dcbfca",
        ).pack(pady=10)
        try:
            image_path = r"C:\Users\Acer\OneDrive\Desktop\logo_pic.jpg"
            img = Image.open(image_path)
            img = img.resize((950, 550), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.default_img = photo
            Label(wrapper, image=photo, bg="#dcbfca").pack(pady=10)
        except:
            Label(
                wrapper,
                text="(Image not found)",
                font=("Times New Roman", 14),
                bg="#dcbfca",
                fg="gray",
            ).pack(pady=10)

    def on_button_click(self, button_text):
        self.clear_center()
        if button_text == "APPOINTMENTS":
            pf = PatientForm(
                self.center_panel,
                back_callback=self.show_default_image,
                refresh_callback=lambda: self.on_button_click("EYE EXAMS"),
            )
            pf.pack(fill="both", expand=True)
        elif button_text == "EYE EXAMS":
            ael = AppointmentListForExam(
                self.center_panel,
                back_callback=self.show_default_image,
                open_exam_callback=self.open_exam_for_patient,
            )
            ael.pack(fill="both", expand=True)
        elif button_text == "PRODUCTS AND BILLS":
            w3 = Window3(
                self.center_panel,
                back_callback=self.show_default_image,
                refresh_allpatients_callback=lambda: self.on_button_click(
                    "ALL PATIENTS"
                ),
            )
            w3.pack(fill="both", expand=True)
        elif button_text == "ALL PATIENTS":
            ap = AllPatientsWindow(
                self.center_panel,
                back_callback=self.show_default_image,
                app_reference=self,
            )
            ap.pack(fill="both", expand=True)
        elif button_text == "EXIT":
            self.root.quit()
        else:
            Label(
                self.center_panel,
                text=f"{button_text} page is under construction",
                font=("Times New Roman", 14),
                bg="#dcbfca",
            ).pack(expand=True)

    def open_exam_for_patient(self, appt_row):
        self.clear_center()
        exam_frame = EyeExamsWindow(
            self.center_panel,
            back_callback=lambda: self.on_button_click("EYE EXAMS"),
            appointment_row=appt_row,
            proceed_to_products_callback=self.open_products_for_eyeexam,
        )
        exam_frame.pack(fill="both", expand=True)

    def open_products_for_eyeexam(self, *args):
        self.clear_center()
        w3 = Window3(
            self.center_panel,
            back_callback=self.show_default_image,
            refresh_allpatients_callback=lambda: self.on_button_click("ALL PATIENTS"),
        )
        w3.pack(fill="both", expand=True)
        # select the newly saved patient if patient is passed
        if args and args[0]:
            patient_name = args[0]
            # display the list
            w3.search_var.set(patient_name)
            w3.search_patient()


if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()
