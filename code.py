import pickle
from collections import defaultdict, UserDict
from datetime import datetime, timedelta

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# Класс, представляющий общее поле данных (имя, номер телефона, дата рождения)
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Класс для хранения имени контакта
class Name(Field):
    pass

# Класс для хранения номера телефона контакта
class Phone(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        # Проверка на корректный формат номера телефона
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError("Некоректний формат номера телефону. Використовуйте 10 цифр без пробілів та інших символів.")

# Класс для хранения даты рождения контакта
class Birthday(Field):
    def __init__(self, value):
        try:
            # Преобразование строки в объект даты
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте ДД.ММ.ГГГГ")

# Класс, представляющий запись о контакте
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Метод для добавления номера телефона к контакту
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # Метод для удаления номера телефона из контакта
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    # Метод для изменения номера телефона контакта
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    # Метод для поиска номера телефона в контакте
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    # Метод для добавления даты рождения к контакту
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    # Метод для представления контакта в виде строки
    def __str__(self):
        return f"Ім'я контакту: {self.name.value}, телефон: {'; '.join(str(p) for p in self.phones)}"

# Класс для хранения контактов в адресной книге
class AddressBook(UserDict):
    # Метод для добавления записи в адресную книгу
    def add_record(self, record):
        self.data[record.name.value] = record

    # Метод для поиска записи по имени в адресной книге
    def find(self, name):
        return self.data.get(name)

    # Метод для удаления записи из адресной книги по имени
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    # Метод для поиска ближайшей даты дня рождения
    def find_next_birthday(self, weekday):
        today = datetime.now().date()
        next_birthday = None

        for name, record in self.data.items():
            if record.birthday:
                birthday_this_year = datetime(today.year, record.birthday.value.month, record.birthday.value.day).date()
                if birthday_this_year < today:
                    birthday_this_year = datetime(today.year + 1, record.birthday.value.month,
                                                  record.birthday.value.day).date()

                while birthday_this_year.weekday() != weekday:
                    birthday_this_year += timedelta(days=1)

                if next_birthday is None or (birthday_this_year - today) < (next_birthday - today):
                    next_birthday = birthday_this_year

        return next_birthday

    # Метод для получения ближайших дней рождения в течение указанного количества дней
    def get_upcoming_birthday(self, days=7):
        today = datetime.today().date()
        upcoming_birthdays = []

        for name, record in self.data.items():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))

                    upcoming_birthdays.append({
                        "name": name,
                        "congratulation_date": birthday_this_year.strftime("%Y.%m.%d")
                    })

        return upcoming_birthdays

# Декоратор для обработки ошибок ввода
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return str(e)
        except ValueError as e:
            return str(e)
        except IndexError as e:
            return str(e)

    return wrapper

# Функция для добавления контакта в адресную книгу
@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Неправильна кількість аргументів. Використовуйте: add [имя] [телефон]")
    name = args[0]
    phones = args[1:]
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт доданий."
    for phone in phones:
        record.add_phone(phone)
    return message

# Функция для изменения номера телефона контакта
@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Неправильна кількість аргументів. Використовуйте: change [ім'я] [новий_телефон]")
    name, phone = args
    if name not in book.data:
        raise KeyError(f"Контакт '{name}' не знайдено.")
    book.data[name].phones = [Phone(phone)]
    return "Контакт успішно оновлено."

# Функция для показа контакта по имени
@input_error
def show_contacts(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Неправильна кількість аргументів. Використовуйте: show [ім'я]")
    name = args[0]
    if name not in book.data:
        raise KeyError(f"Контакт '{name}' не знайдено.")
    return str(book.data[name])

# Функция для показа всех контактов
@input_error
def show_all_contacts(book: AddressBook):
    if not book.data:
        return "Список контактів порожній."
    return "\n".join(
        [f"{name}: {', '.join(str(phone) for phone in record.phones)}" for name, record in book.data.items()])

# Функция для добавления дня рождения контакту
@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Неправильна кількість аргументів. Використовуйте: add-birthday [ім'я] [дата]")
    name, birthday = args
    if name not in book.data:
        raise KeyError(f"Контакт '{name}' не знайдено.")
    book.data[name].add_birthday(birthday)
    return f"Дату народження успішно додано для контакту '{name}'."

# Функция для показа дня рождения контакта
@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Неправильна кількість аргументів. Використовуйте: show-birthday [ім'я]")
    name = args[0]
    if name not in book.data:
        raise KeyError(f"Контакт '{name}' не знайдено.")
    birthday = book.data[name].birthday
    if birthday is None:
        return f"Для контакту '{name}' не вказано дату народження."
    else:
        return f"Дата народження контакту '{name}': {birthday}"

# Функция для показа всех дней рождения
@input_error
def all_birthdays(book):
    birthdays_list = []
    for name, record in book.data.items():
        if record.birthday:
            birthdays_list.append((name, record.birthday.value))
    if not birthdays_list:
        return "В адресній книзі немає контактів із днями народження."
    else:
        return "\n".join([f"{name}: {birthday}" for name, birthday in birthdays_list])

# Функция для разбора введенной пользователем команды
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()  # Перевод команды в нижний регистр и удаление лишних пробелов
    return cmd, args

# Главная функция программы
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        try:
            command, args = parse_input(user_input)
        except ValueError as e:
            print(e)
            continue

        if command in ["close", "exit"]:
            print("Goodbye!")
            save_data(book)  # Сохранение данных перед завершением работы программы
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "show":
            print(show_contacts(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "all-birthdays":
            print(all_birthdays(book))
        else:
            print("Недійсна команда.")

if __name__ == "__main__":
    main()
