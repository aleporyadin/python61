import json
import uuid

DATE_FILE = "data.json"


def generate_student_id():
    return "ST-" + uuid.uuid4().hex[:8].upper()


def normalize_student_id(student_id):
    s_id = str(student_id).strip().upper()

    if len(s_id) == 8 and not s_id.startswith("ST-"):
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

        s.course_ids = []
        for c_id in data.get("course_ids", []):
            s.course_ids.append(int(c_id))

        grades = data.get("grades", {})

        for c_id, c_grades in grades.items():
            s.grades[int(c_id)] = c_grades

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
        self.id = id
        self.title = title
        self.teacher = teacher
        self.student_ids = []

    def add_student(self, student_id):
        if student_id not in self.student_ids:
            self.student_ids.append(student_id)

    def remove_student(self, student_id):
        if student_id in self.student_ids:
            self.student_ids.remove(student_id)

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
            int(data["id"]),
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
    def __init__(self):
        self.students = []
        self.courses = []
        self.next_course_id = 1

    def create_unique_student_id(self):
        while True:
            student_id = generate_student_id()

            if self.find_student_by_id(student_id) is None:
                return student_id

    def find_student_by_id(self, student_id) -> Student | None:
        s_id = normalize_student_id(student_id)
        for s in self.students:
            if s.id == s_id:
                return s

        return None

    def find_course_by_id(self, course_id) -> Course | None:
        for c in self.courses:
            if c.id == course_id:
                return c

        return None

    def find_students_by_name(self, name_part):
        res = []
        name_part = name_part.lower()
        for s in self.students:
            if name_part in s.name.lower():
                res.append(s)

        return res

    def add_student(self, name, age, email):
        s_id = self.create_unique_student_id()
        s = Student(s_id, name, age, email)
        self.students.append(s)
        return s

    def edit_student(self, student_id, name, age, email):
        s = self.find_student_by_id(student_id)
        if s is None:
            return False
        s.name = name
        s.age = age
        s.email = email
        return True

    def add_course(self, title, teacher):
        c = Course(self.next_course_id, title, teacher)
        self.courses.append(c)
        self.next_course_id += 1
        return c

    def delete_student(self, student_id):
        s = self.find_student_by_id(student_id)
        if s is None:
            return False

        self.students.remove(s)

        for c in self.courses:
            c.remove_student(s.id)

        return True

    def enroll_student_to_course(self, student_id, course_id):
        s = self.find_student_by_id(student_id)
        c = self.find_course_by_id(course_id)

        if s is None:
            raise ValueError("Студента з таким ІД не знайдено")

        if c is None:
            raise ValueError("Курс з таким ІД не знайдено")

        s.add_course(c.id)
        c.add_student(s.id)

    def add_grade_to_student(self, student_id, course_id, grade):
        s = self.find_student_by_id(student_id)
        c = self.find_course_by_id(course_id)

        if s is None:
            raise ValueError("Студента з таким ІД не знайдено")

        if c is None:
            raise ValueError("Курс з таким ІД не знайдено")

        s.add_grade(c.id, grade)

    def get_sorted_students_by_name(self):
        return sorted(self.students, key=lambda s: s.name.lower())

    def get_sorted_students_by_avg_grade(self):
        return sorted(self.students, key=lambda s: s.average_grade())

    def get_best_student(self):
        if len(self.students) == 0:
            return None
        return max(self.students, key=lambda s: s.average_grade())

    def get_student_without_courses(self):
        res = []

        for s in self.students:
            if len(s.course_ids) == 0:
                res.append(s)
        return res

    def get_avg_grade_of_center(self):
        grades = []
        for s in self.students:
            for s_grade in s.grades.values():
                grades.extend(s_grade)

        if len(grades) == 0:
            return 0

        return sum(grades) / len(grades)

    def to_dict(self):
        students_data = []
        courses_data = []

        for s in self.students:
            students_data.append(s.to_dict())

        for c in self.courses:
            courses_data.append(c.to_dict())

        return {
            "next_course_id": self.next_course_id,
            "students": students_data,
            "courses": courses_data
        }

    def save_to_json(self, filename):
        data = self.to_dict()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_json(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.students = []
        self.courses = []

        for s_d in data.get("students", []):
            self.students.append(Student.from_dict(s_d))

        for c_d in data.get("courses", []):
            self.courses.append(Course.from_dict(c_d))

        self.next_course_id = data.get("next_course_id", self.get_next_course_id())

        if self.next_course_id < self.get_next_course_id():
            self.next_course_id = self.get_next_course_id()

    def get_next_course_id(self):
        if len(self.courses) == 0:
            return 1
        max_id = max(course.id for course in self.courses)
        return max_id + 1


class App:
    def __init__(self):
        self.center = EducationCenter()
        self.is_running = True

        self.actions = {
            1: self.add_student_menu,
            2: self.show_student_menu,
            3: self.search_student_menu,
            4: self.delete_student_menu,
            5: self.add_course_menu,
            6: self.show_course_menu,
            7: self.enroll_student_menu,
            8: self.add_grade_menu,
            9: self.show_student_details_menu,
            10: self.sort_student_menu,
            11: self.statistics_menu,
            12: self.save_menu,
            13: self.load_menu,
            14: self.edit_student_menu,
            0: self.exit_program
        }

    def run(self):
        while self.is_running:
            self.show_main_menu()
            choice = self.input_int("Ваш вибір: ", 0, 14)
            act = self.actions.get(choice)
            act()

            if self.is_running:
                self.pause()

    def show_main_menu(self):
        print("\n===== Навчальний центр =====")
        print("1. Додати студента")
        print("2. Показати студентів")
        print("3. Пошук студента")
        print("4. Видалити студента")
        print("5. Додати курс")
        print("6. Показати курси")
        print("7. Записати студента на курс")
        print("8. Додати оцінку")
        print("9. Показати студента")
        print("10. Сортування студентів")
        print("11. Статистика")
        print("12. Зберегти дані")
        print("13. Завантажити дані")
        print("14. Редагувати студента")
        print("0. Вийти")

    def input_int(self, message, min_value=None, max_value=None):
        while True:
            try:
                value = int(input(message))
            except ValueError:
                print("Введіть ціле число")
                continue

            if min_value is not None and value < min_value:
                print(f"Число має бути не менше {min_value}")
                continue

            if max_value is not None and value > max_value:
                print(f"Число має бути не більше {max_value}")
                continue

            return value

    def pause(self):
        input("\nНатисніть Enter, щоб продовжити...")

    def input_text(self, message):
        while True:
            value = input(message).strip()

            if value != "":
                return value

            print("Поле не може бути порожнім")

    def input_filename(self, message):
        filename = input(message).strip()

        if filename == "":
            return DATE_FILE

        return filename

    def print_students(self, students):
        if len(students) == 0:
            print("Студентів не знайдено")
            return

        for s in students:
            print(s)

    def print_courses(self, courses):
        if len(courses) == 0:
            print("Курсів не знайдено")
            return

        for c in courses:
            print(c)

    def print_student_details(self, student):
        print(student)

        if len(student.course_ids) == 0:
            print("Курси: немає")
            return

        print("Курси:")
        for course_id in student.course_ids:
            course = self.center.find_course_by_id(course_id)
            course_title = "курс не знайдено"

            if course is not None:
                course_title = course.title

            grades = student.grades.get(course_id, [])
            grades_text = "немає оцінок"

            if len(grades) > 0:
                grades_text = ", ".join(str(g) for g in grades)

            avg_grade = student.average_grade_by_course(course_id)
            print(f"- {course_id}. {course_title}: {grades_text}, середній бал {avg_grade:.2f}")

    def print_course_details(self, course):
        print(course)

        if len(course.student_ids) == 0:
            print("Студенти: немає")
            return

        print("Студенти:")
        for student_id in course.student_ids:
            student = self.center.find_student_by_id(student_id)

            if student is None:
                print(f"- {student_id}: студент не знайдений")
            else:
                print(f"- {student.id}: {student.name}")

    def add_student_menu(self):
        print("\n--- Додавання студента ---")
        name = self.input_text("Ім'я: ")
        age = self.input_int("Вік: ", 1, 120)
        email = self.input_text("е-Пошта: ")

        student = self.center.add_student(name, age, email)
        print(f"Студента додано. ID: {student.id}")

    def edit_student_menu(self):
        print("\n--- Редагування студента ---")
        student_id = self.input_text("ID студента: ")
        name = self.input_text("Ім'я: ")
        age = self.input_int("Вік: ", 1, 120)
        email = self.input_text("е-Пошта: ")
        student = self.center.edit_student(student_id, name, age, email)
        if student:
            print("Студента змінено")
        else:
            print("Студента з таким ID не знайдено")

    def show_student_menu(self):
        print("\n--- Список студентів ---")
        self.print_students(self.center.students)

    def search_student_menu(self):
        print("\n--- Пошук студента ---")
        name_part = self.input_text("Введіть ім'я або його частину: ")
        students = self.center.find_students_by_name(name_part)
        self.print_students(students)

    def delete_student_menu(self):
        print("\n--- Видалення студента ---")
        student_id = self.input_text("ID студента: ")

        if self.center.delete_student(student_id):
            print("Студента видалено")
        else:
            print("Студента з таким ID не знайдено")

    def add_course_menu(self):
        print("\n--- Додавання курсу ---")
        title = self.input_text("Назва курсу: ")
        teacher = self.input_text("Викладач: ")

        course = self.center.add_course(title, teacher)
        print(f"Курс додано. ID: {course.id}")

    def show_course_menu(self):
        print("\n--- Список курсів ---")

        if len(self.center.courses) == 0:
            print("Курсів не знайдено")
            return

        for course in self.center.courses:
            self.print_course_details(course)

    def enroll_student_menu(self):
        print("\n--- Запис студента на курс ---")

        if len(self.center.students) == 0:
            print("Спочатку додайте студента")
            return

        if len(self.center.courses) == 0:
            print("Спочатку додайте курс")
            return

        student_id = self.input_text("ID студента: ")
        course_id = self.input_int("ID курсу: ", 1)

        try:
            self.center.enroll_student_to_course(student_id, course_id)
            print("Студента записано на курс")
        except ValueError as e:
            print(e)

    def add_grade_menu(self):
        print("\n--- Додавання оцінки ---")

        if len(self.center.students) == 0:
            print("Спочатку додайте студента")
            return

        if len(self.center.courses) == 0:
            print("Спочатку додайте курс")
            return

        student_id = self.input_text("ID студента: ")
        course_id = self.input_int("ID курсу: ", 1)
        grade = self.input_int("Оцінка: ", 1, 12)

        try:
            self.center.add_grade_to_student(student_id, course_id, grade)
            print("Оцінку додано")
        except ValueError as e:
            print(e)

    def show_student_details_menu(self):
        print("\n--- Дані студента ---")
        student_id = self.input_text("ID студента: ")
        student = self.center.find_student_by_id(student_id)

        if student is None:
            print("Студента з таким ID не знайдено")
            return

        self.print_student_details(student)

    def sort_student_menu(self):
        print("\n--- Сортування студентів ---")

        if len(self.center.students) == 0:
            print("Студентів не знайдено")
            return

        print("1. За ім'ям")
        print("2. За середнім балом")
        choice = self.input_int("Ваш вибір: ", 1, 2)

        if choice == 1:
            students = self.center.get_sorted_students_by_name()
        else:
            students = sorted(
                self.center.students,
                key=lambda s: s.average_grade(),
                reverse=True
            )

        self.print_students(students)

    def statistics_menu(self):
        print("\n--- Статистика ---")
        print(f"Кількість студентів: {len(self.center.students)}")
        print(f"Кількість курсів: {len(self.center.courses)}")
        print(f"Середній бал центру: {self.center.get_avg_grade_of_center():.2f}")

        best_student = self.center.get_best_student()

        if best_student is None:
            print("Найкращий студент: немає")
        else:
            print(f"Найкращий студент: {best_student.name} ({best_student.average_grade():.2f})")

        students_without_courses = self.center.get_student_without_courses()
        print(f"Студентів без курсів: {len(students_without_courses)}")

        if len(students_without_courses) > 0:
            self.print_students(students_without_courses)

    def save_menu(self):
        print("\n--- Збереження даних ---")
        filename = self.input_filename(f"Файл для збереження [{DATE_FILE}]: ")

        try:
            self.center.save_to_json(filename)
            print(f"Дані збережено у файл {filename}")
        except OSError as e:
            print(f"Не вдалося зберегти дані: {e}")

    def load_menu(self):
        print("\n--- Завантаження даних ---")
        filename = self.input_filename(f"Файл для завантаження [{DATE_FILE}]: ")

        try:
            self.center.load_from_json(filename)
            print(f"Дані завантажено з файлу {filename}")
        except FileNotFoundError:
            print("Файл не знайдено")
        except json.JSONDecodeError:
            print("Файл має неправильний JSON формат")
        except OSError as e:
            print(f"Не вдалося завантажити дані: {e}")

    def exit_program(self):
        print("Роботу завершено")
        self.is_running = False


if __name__ == "__main__":
    app = App()
    app.run()
