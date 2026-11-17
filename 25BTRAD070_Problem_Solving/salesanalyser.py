students = {}


def add_student():
    name = input("Enter student name: ")

    if name not in students:
        students[name] = []
        print("Student added successfully!")
    else:
        print("Student already exists.")


def mark_attendance():
    name = input("Enter student name: ")

    if name in students:
        status = input("Enter attendance (P/A): ").upper()

        if status == "P" or status == "A":
            students[name].append(status)
            print("Attendance marked successfully")