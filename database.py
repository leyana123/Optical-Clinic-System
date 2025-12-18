# database.py

import sqlite3

DB_FILE = "optical_clinic_system.db"


def get_db_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


EYE_EXAM_FEE = ("Medical Checkup Fee", 1000)


def init_db_schema():
    conn = get_db_conn()
    cur = conn.cursor()

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
    # AllPatients table
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

    for name, price in DIAGNOSIS_ITEMS:
        cur.execute(
            "INSERT OR IGNORE INTO Products (name, category, price) VALUES (?, ?, ?)",
            (name, "diagnosis", price),
        )
    for name, price in FRAME_ITEMS:
        cur.execute(
            "INSERT OR IGNORE INTO Products (name, category, price) VALUES (?, ?, ?)",
            (name, "frame", price),
        )
    for name, price in ADD_ON_ITEMS:
        cur.execute(
            "INSERT OR IGNORE INTO Products (name, category, price) VALUES (?, ?, ?)",
            (name, "addon", price),
        )
    for name, price in CONTACT_LENSES_COLOR:
        cur.execute(
            "INSERT OR IGNORE INTO Products (name, category, price) VALUES (?, ?, ?)",
            (name, "contact", price),
        )
    # Medical checkup fee as a product
    cur.execute(
        "INSERT OR IGNORE INTO Products (name, category, price) VALUES (?, ?, ?)",
        (EYE_EXAM_FEE[0], "fee", EYE_EXAM_FEE[1]),
    )

    conn.commit()
    conn.close()


seed_products()


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
            ELSE 'Completed'
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


if __name__ == "__main__":
    init_db_schema()
    seed_products()
