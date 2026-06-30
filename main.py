import json
import uuid

DATE_FILE = "data.json"


def generate_student_id():
    return "ST-" + uuid.uuid4().hex[:8].upper()


def normalize_student_id(student_id):
    s_id = str(student_id).strip().upper()

    if len(s_id) == 8 and not student_id.startswith("ST-"):
        return "ST-" + s_id
    return s_id


class Student:
    def __init__(self, id, name, age, email):
        self.id = normalize_student_id(id)
        self.name = name
        self.age = age
        self.email = email
        self.course_ids = []
        self.grades = {}

    def add_course(self, course_id):
        if course_id not in self.course_ids:
            self.course_ids.append(course_id)

    def remove_course(self, course_id):
        if course_id in self.course_ids:
            self.course_ids.remove(course_id)

        if course_id in self.grades:
            del self.grades[course_id]

    def add_grade(self, course_id, grade):
        if course_id not in self.course_ids:
            raise ValueError(f"Студент не записаний на цей курс {course_id}")

        if grade < 1 or grade > 12:
            raise ValueError(f"Оцінка має бути від 1 до 12")

        if course_id not in self.grades:
            self.grades[course_id] = []

        self.grades[course_id].append(grade)

    def average_grade(self):
        all_grades = []

        for grades in self.grades.values():
            all_grades.extend(grades)

        if len(all_grades) == 0:
            return 0

        return sum(all_grades) / len(all_grades)

    def average_grade_by_course(self, course_id):
        grades = self.grades.get(course_id, [])

        if len(grades) == 0:
            return 0

        return sum(grades) / len(grades)

    def to_dict(self):
        grades_student_json = {}
        for course_id, grades in self.grades.items():
            grades_student_json[str(course_id)] = grades

        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "course_ids": self.course_ids,
            "grades": grades_student_json
        }

    @staticmethod
    def from_dict(data):
        s = Student(
            data["id"],
            data["name"],
            data["age"],
            data["email"]
        )

        s.course_ids = data.get("course_ids", [])

        grades = data.get("grades", {})

        for c_id, c_grades in grades.items():
            s.grades[c_id] = c_grades

        return s

    def __str__(self):
        return (f"ІД: {self.id}, "
                f"Імя: {self.name}, "
                f"Вік: {self.age}, "
                f"е-Пошта: {self.email}, "
                f"Курсів: {len(self.course_ids)}, "
                f"Середній бал: {self.average_grade():.2f}")


class Course:
    def __init__(self, id, title, teacher):
        self.id = normalize_student_id(id)
        self.title = title
        self.teacher = teacher
        self.student_ids = []

    def add_student(self, student_id):
        s_id = normalize_student_id(student_id)

        if s_id not in self.student_ids:
            self.student_ids.append(s_id)

    def remove_student(self, student_id):
        s_id = normalize_student_id(student_id)

        if s_id in self.student_ids:
            self.student_ids.remove(s_id)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "teacher": self.teacher,
            "student_ids": self.student_ids
        }

    @staticmethod
    def from_dict(data):
        c = Course(
            data["id"],
            data["title"],
            data["teacher"]
        )

        c.student_ids = []


        for s_id in data.get("student_ids", []):
            c.student_ids.append(normalize_student_id(s_id))

        return c

    def __str__(self):
        return (f"ІД: {self.id}, "
                f"Назва: {self.title}, "
                f"Викладач: {self.teacher}, "
                f"Студентів: {len(self.student_ids)}, ")


class EducationCenter:
    pass


class App:
    pass
