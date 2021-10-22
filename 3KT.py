

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal
from functools import reduce
from random import randint
from requests import get

MALE = "М"
FEMALE = "Ж"


@dataclass
class Human(ABC):
    """Абстрактный класс - человек"""

    __name: str
    __age: int
    __sex: str

    def __init__(self, name: str = "Новый человек", age: int = 0, sex: str = MALE):
        self.name = name
        self.age = age
        self.sex = sex

    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, name: str):
        if len(name) > 0 and name[0] in (chr(s) for s in range(ord("А"), ord("Я") + 1)):
            self.__name = name
        else:
            raise ValueError("Имя должно быть непустым и начинаться с заглавной русской буквы")

    @property
    def age(self) -> int:
        return self.__age
    @age.setter
    def age(self, age: int):
        if isinstance(age, int) and 0 <= age <= 200:
            self.__age = age
        else:
            raise ValueError("Возраст должен быть целым неотрицательным числом")

    @property
    def sex(self) -> str:
        return self.__sex
    @sex.setter
    def sex(self, sex: Literal[MALE, FEMALE]):
        if sex.upper() in (MALE, FEMALE):
            self.__sex = sex.upper()
        else:
            raise ValueError("Пол может быть только 'М' или 'Ж'")

    @abstractmethod
    def __str__(self):
        pass
# end class Human


@dataclass
class Student(Human):
    """Класс - студент"""

    __rating: int

    def __init__(self, name: str = "Вася", age: int = 0, sex: str = MALE, rating: int = 0):
        super().__init__(name, age, sex)
        self.rating = rating

    @property
    def rating(self) -> int:
        return self.__rating
    @rating.setter
    def rating(self, rating: int):
        if 0 <= rating <= 100:
            self.__rating = rating
        else:
            raise ValueError("Рейтинг может быть только целым числом от 0 до 100")

    def __str__(self) -> str:
        return f"Сотрудник: {self.name}, возраст {self.age}, пол {self.sex}, КПД {self.rating}%"

    def __add__(self, other):
        """Сложение студента с другим объектом"""
        if isinstance(other, Student):  # студент + студент = группа
            return Group(self, other)
        elif isinstance(other, Group):  # студент + группа = группа чуть побольше
            return Group(*other.students + [self])
        else:
            raise TypeError(f"Нельзя складывать объекты типов {self.__class__} и {type(other)}")
    __radd__ = __add__

    @staticmethod
    def isStudents(*objects) -> bool:
        return all(isinstance(s, Student) for s in objects)

    @staticmethod
    def studentsToGroup(*students):
        if Student.isStudents(*students):
            return Group(students)
        else:
            raise TypeError("В группу должны входить только студенты")
# end class Student


class Group:
    """Класс - группа (контейнер студентов)"""

    def __init__(self, *students, name="Новая группа"):
        self.students = students
        self.name = name

    @property
    def students(self):
        return self.__students
    @students.setter
    def students(self, students):
        if Student.isStudents(*students):
            # этот код ужасен, не пишите так
            if reduce(lambda accum, stud: all((accum, sum(int(stud is st) for st in students) == 1)), (True,) + students):
               self.__students = list(students)
            else:
                raise ValueError("Один сотрудник не может входить в отделение более одного раза")
        else:
            raise TypeError("В группу должны входить только студенты")

    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, name):
        if len(name) > 0:
            self.__name = name
        else:
            raise ValueError("Имя группы не может быть пустым")

    def __str__(self):
        text = f"Отделение '{self.name}' состоит из {len(self)} человек:\n\t"
        rit = iter(range(1, len(self) + 1))
        text += "\n\t".join((f"{next(rit)}. {s}" for s in self.students)) if len(self) > 0 else "Пусто"
        return text

    def __len__(self):
        return len(self.students)

    def __add__(self, other):
        """Сложение группы с другим объектом"""
        if isinstance(other, Group):  # группа + группа = группа побольше
            return Group(*self.students, *other.students)
        elif isinstance(other, Student):  # группа + студент = группа чуть побольше
            return other + self
        else:
            raise TypeError(f"Нельзя складывать объекты типов {self.__class__} и {type(other)}")
    __radd__ = __add__
# end class Group


def studentGenerator() -> Student:
    """Функция - генератор студентов"""

    male_names = ("Максим",)
    female_names = ("Анна",)
    try:
        male_names = get(r"https://raw.githubusercontent.com/linuxforse/"
                         r"random_russian_and_ukraine_name_surname/master/imena_m_ru.txt").text.split()
        female_names = get(r"https://raw.githubusercontent.com/linuxforse/"
                           r"random_russian_and_ukraine_name_surname/master/imena_f_ru.txt").text.split()
        if len(male_names) + len(female_names) < 2:
            raise Exception("Списки имен пусты")
    except Exception as e:
        print(f"Произошла ошибка при попытке скачать файл с именами, а именно:\n{e}")

    while True:
        sex = MALE if randint(0, 1) == 0 else FEMALE
        names = male_names if sex == MALE else female_names
        name = names[randint(0, len(names) - 1)]
        age = randint(17, 30)
        rating = randint(33, 100)
        yield Student(name, age, sex, rating)
# end function studentGenerator()


if __name__ == "__main__":
    stud1 = Student("Василий", 18, MALE, 50)
    stud2 = Student("Жанна", 21, FEMALE, 70)
    stud3 = Student("Михаил", 25, MALE, 45)
    stud4 = Student("Василина", 18, FEMALE, 35)
    stud5 = Student("Пафнутий", 23, MALE, 100)

    group1 = Group(stud2, stud1, name="Техническая поддержка")
    group2 = Group(stud4, stud3, name="Продажи")
    print(group1)
    print(group2)

    students = []
    studgen = studentGenerator()
    for i in range(20):
        students.append(next(studgen))

    group3 = Group(*students[:3], name="Разработчики")
    group4 = Group(*students[3:8], name="Тестировщики")
    group6 = Group(*students[8:12], name="Веб разработка")
    group5 = Group(stud5, stud4,stud3,stud2, name="Аналитики")

    print(group3)
    print(group4)
    print(group5)
    print(group6)
