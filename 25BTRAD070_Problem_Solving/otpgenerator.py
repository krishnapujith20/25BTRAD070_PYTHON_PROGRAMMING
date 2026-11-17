def calculate_grade(marks):
    if marks >= 90:
        return "A"
    elif marks >= 80:
        return "B"
    elif marks >= 70:
        return "C"
    elif marks >= 60:
        return "D"
    elif marks >= 50:
        return "E"
    else:
        return "F"


def main():
    marks = int(input("Enter student marks: "))
    grade = calculate_grade(marks)

    print("Marks:", marks)
    print("Grade:", grade)


main()