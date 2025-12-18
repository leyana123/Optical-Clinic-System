import sqlite3
from tkinter import *
from tkinter import ttk
import datetime
from tkinter import messagebox
from optical import (
    eye_conditions,
    symptom_to_medical,
    get_db_conn,
)


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
        self.update_appointment_date()

    # appointment ng check up
    def update_appointment_date(patient_form):
        now = datetime.datetime.now()
        today = now.date()

        if patient_form.appointment_today.get() == "Yes":
            selected_date = today
            patient_form.appointment_date.set(selected_date.strftime("%Y-%m-%d"))

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
            for t in patient_form.all_slots:
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

            patient_form.time_slots = available_slots
            patient_form.time_combo.config(values=patient_form.time_slots)
            patient_form.appointment_time.set(patient_form.time_slots[0])

        else:  # Appointment Today = No
            appt_date_str = patient_form.appointment_date.get().strip()
            try:
                selected_date = datetime.datetime.strptime(
                    appt_date_str, "%Y-%m-%d"
                ).date()
                if selected_date <= today:
                    patient_form.appointment_date.set("")
                    patient_form.time_slots = patient_form.all_slots.copy()
                    patient_form.appointment_time.set("")
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
                        t for t in patient_form.all_slots if t not in taken_slots
                    ]
                    if not available_slots:
                        available_slots = ["No available slots"]
                    patient_form.time_slots = available_slots
                    patient_form.time_combo.config(values=patient_form.time_slots)
                    patient_form.appointment_time.set(patient_form.time_slots[0])
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

    def calculate_age(patient_form, event=None):
        dob_str = patient_form.dob.get().strip()
        if not dob_str:
            patient_form.age.set("")
            patient_form.dob_entry.config(bg="white")
            return
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            patient_form.age.set("Calculating...")  # habang nag ttype ng DOB
            patient_form.dob_entry.config(bg="#fca1a1")
            return

        # run kapag tamam yung format
        today = datetime.date.today()
        if dob > today:
            patient_form.age.set("Invalid")
            patient_form.dob_entry.config(bg="#fca1a1")
            return
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        patient_form.age.set(str(age))
        patient_form.dob_entry.config(bg="white")

    # for adding patient
    def add_patient(patient_form):
        fname = patient_form.first_name.get().strip()
        lname = patient_form.surname.get().strip()
        address = patient_form.address.get().strip()
        dob_str = patient_form.dob.get().strip()
        mobile = patient_form.mobile.get().strip()
        appointment_date = patient_form.appointment_date.get().strip()
        appointment_time = patient_form.appointment_time.get().strip()

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
        except ValueError:  # raise error na dapat ay same format
            messagebox.showerror(
                "Error", "Appointment date must be in YYYY-MM-DD format."
            )
            return
        if appt_date_obj < datetime.date.today():
            messagebox.showerror("Error", "Appointment date cannot be in the past.")
            return
        #  if appointment today = No, date cannot be today
        if (
            patient_form.appointment_today.get() == "No"
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
                patient_form.gender.get(),
                address,
                dob_str,
                int(patient_form.age.get() or 0),
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

        patient_form.clear_form()
        if patient_form.refresh_callback:
            patient_form.refresh_callback()


# ------------------ Appointment List frame that leads to EyeExam ------------------
class AppointmentListForExam(Frame):
    def __init__(self, parent, back_callback, open_exam_callback):
        super().__init__(parent, bg="#dcbfca")
        self.parent = parent
        self.back_callback = back_callback
        self.open_exam_callback = open_exam_callback
        self.build_ui()
        self.load_appointments()  # appointments mula sa database at ipapakita sa list

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

        # Eye side and symptom selection
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

        # for updates ng score
        self.od_layer.trace("w", self.update_scores)
        self.os_layer.trace("w", self.update_scores)
        self.eye_side.trace("w", self.update_eye_visibility)
        self.selected_symptom.trace("w", self.update_scores)

        self.update_eye_visibility()

        if appointment_row:
            self.prefill_from_appointment(appointment_row)

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

    def calculate_cyl_axis_single(self, layer_val):
        # logic calculation
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

        # --- PRESCRIPTION TABLE ---
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

        # Remove duplicate progression lines
        progression_list = list(dict.fromkeys(progression_list))

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
        created_at = self.appointment_row[
            "created_at"
        ]  # Unique ID for Appointment record

        diagnostics = self.diagnostic_textbox.get("1.0", "end").strip()
        treatments = self.treatment_textbox.get("1.0", "end").strip()
        eye_progression = self.eye_progression_text.get("1.0", "end").strip()
        suggested = []
        txt_lines = treatments.splitlines()

        # find suggested products from treatments/prescription
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT name FROM Products")
        product_names = [row["name"] for row in cur.fetchall()]

        for line in txt_lines:
            line = line.strip()
            # if any product name is contained in the line
            for product in product_names:
                if product.lower() in line.lower():
                    suggested.append(product)
                    break

        # Insert/Update EyeExams table
        saved_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur.execute(
                """
                INSERT INTO EyeExams (patient_name, appointment_id, prescription, suggested_products, od_sph, os_sph, od_cyl, od_axis, os_cyl, os_axis, od_add, os_add, diagnostics, treatments, eye_progression, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    patient_name,
                    created_at,  # appointment_id uses created_at from Appointments
                    self.treatment_textbox.get("1.0", "end").strip(),
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
                    first_name=excluded.first_name, surname=excluded.surname, gender=excluded.gender, address=excluded.address, dob=excluded.dob, age=excluded.age, mobile=excluded.mobile, 
                    eye_side=excluded.eye_side, od_layer=excluded.od_layer, os_layer=excluded.os_layer, od_score=excluded.od_score, os_score=excluded.os_score, 
                    od_sph=excluded.od_sph, os_sph=excluded.os_sph, od_cyl=excluded.od_cyl, od_axis=excluded.od_axis, os_cyl=excluded.os_cyl, os_axis=excluded.os_axis, od_add=excluded.od_add, os_add=excluded.os_add, 
                    selected_symptom=excluded.selected_symptom, diagnostics=excluded.diagnostics, treatments=excluded.treatments, eye_progression=excluded.eye_progression, last_updated=excluded.last_updated
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
                    self.selected_symptom.get(),
                    diagnostics,
                    treatments,
                    eye_progression,
                    saved_at,
                ),
            )

            # Appointments to EyeExams
            cur.execute(
                "DELETE FROM Appointments WHERE patient_name=? AND created_at=?",
                (patient_name, created_at),
            )

            conn.commit()

            messagebox.showinfo(
                "Exam Saved",
                f"Eye exam for {patient_name} saved successfully. Proceeding to billing.",
            )

            # proceed na sa billing
            if self.proceed_to_products_callback:
                self.proceed_to_products_callback(patient_name)
            else:
                self.back_callback()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save exam: {e}")
            conn.rollback()

        conn.close()


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
        """Pre-selects items based on the suggested_products column from EyeExams."""
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
            # Fix price if zero
            key = name.strip().lower()
            price_from_db = product_price_map.get(key)

            if price == 0 or price is None:
                if price_from_db is not None:
                    price = price_from_db
                self.selected_items[name] = price  # update price in selected_items

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


class AllPatientsWindow(Frame):
    def __init__(self, parent, back_callback=None, app_reference=None):
        super().__init__(parent, bg="#dcbfca")
        self.back_callback = back_callback
        self.app_reference = app_reference
        self.build_ui()
        self.load_all_patients()

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
        self.details_text.insert(ttk.END, "=" * 134 + "\n")

        # Display all fields nicely
        for key in rec.keys():
            self.details_text.insert(
                END, f"{key.replace('_', ' ').title()}: {rec[key]}\n"
            )

        self.details_text.insert(ttk.END, "=" * 134 + "\n")
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
