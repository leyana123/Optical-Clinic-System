from tkinter import Tk, Frame, Label, Button
from PIL import Image, ImageTk
from optical import (
    PatientForm,
    AppointmentListForExam,
    EyeExamsWindow,
    Window3,
    AllPatientsWindow,
)


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("OPTICare - Dra. Leanne Mendoza")
        self.root.geometry("1000x650")
        self.root.config(bg="#dcbfca")

        self.left_panel = Frame(root, bg="#a4c6e7", width=220)
        self.left_panel.pack(side="left", fill="y")

        Label(
            self.left_panel,
            text="OPTICare",
            font=("Times New Roman", 24, "bold"),
            bg="#a4c6e7",
            fg="black",
        ).pack(pady=20, padx=10)

        # buttons
        buttons = [
            ("APPOINTMENTS", self.show_appointments),
            ("EYE EXAMS", self.show_eye_exams),
            ("PRODUCTS AND BILLS", self.show_products_and_bills),
            ("ALL PATIENTS", self.show_all_patients),
            ("EXIT", self.root.quit),
        ]
        for text, cmd in buttons:
            Button(
                self.left_panel,
                text=text,
                command=cmd,
                bg="#e7c6e4",
                fg="black",
                font=("Times New Roman", 10),
                width=20,
                height=2,
            ).pack(pady=5, padx=10)

        self.center_panel = Frame(root, bg="#dcbfca")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.show_welcome()

    def clear_center(self):
        for widget in self.center_panel.winfo_children():
            widget.destroy()

    def show_welcome(self):
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

    def show_appointments(self):
        self.clear_center()
        pf = PatientForm(
            self.center_panel,
            back_callback=self.show_welcome,
            refresh_callback=self.show_eye_exams,
        )
        pf.pack(fill="both", expand=True)

    def show_eye_exams(self):
        self.clear_center()
        ael = AppointmentListForExam(
            self.center_panel,
            back_callback=self.show_welcome,
            open_exam_callback=self.open_exam_for_patient,
        )
        ael.pack(fill="both", expand=True)

    def open_exam_for_patient(self, appt_row):
        self.clear_center()
        exam_frame = EyeExamsWindow(
            self.center_panel,
            back_callback=self.show_eye_exams,
            appointment_row=appt_row,
            proceed_to_products_callback=self.show_products_for_eyeexam,
        )
        exam_frame.pack(fill="both", expand=True)

    def show_products_for_eyeexam(self, patient_name=None):
        self.clear_center()
        w3 = Window3(
            self.center_panel,
            back_callback=self.show_welcome,
            refresh_allpatients_callback=self.show_all_patients,
        )
        w3.pack(fill="both", expand=True)
        if patient_name:
            w3.search_var.set(patient_name)
            w3.search_patient()

    def show_products_and_bills(self):
        self.clear_center()
        w3 = Window3(
            self.center_panel,
            back_callback=self.show_welcome,
            refresh_allpatients_callback=self.show_all_patients,
        )
        w3.pack(fill="both", expand=True)

    def show_all_patients(self):
        self.clear_center()
        ap = AllPatientsWindow(
            self.center_panel,
            back_callback=self.show_welcome,
            app_reference=self,
        )
        ap.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()
