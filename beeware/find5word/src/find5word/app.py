import toga
import re
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import requests

class Word5Finder(toga.App):
    # Константы
    WORDS_URL = 'https://raw.githubusercontent.com/it4sru/find5word/main/russian_words.txt'
    LOADING_MESSAGE = "Загрузка слов ..."
    ERROR_MESSAGE = "Ошибка загрузки слов"
    SUCCESS_MESSAGE = "Загружено {num} слов"

    def startup(self):
        # Создаем главное окно
        self.main_window = toga.MainWindow(title=self.formal_name, size=(300, 600))
        self.main_container = toga.Box(style=Pack(direction=COLUMN, padding=5))

        # Создаем кнопку для загрузки слов
        self.button_load = toga.Button("Загрузить слова", on_press=self.load_words, style=Pack(padding=5))
        self.main_container.add(self.button_load)

        # Создаем метку для инструкций
        self.label_instructions = toga.Label("Задайте параметры поиска:", style=Pack(padding=(0, 5, 15, 5)))
        self.main_container.add(self.label_instructions)

        # Создаем поле для ввода количества букв в слове
        self.label_entry_length = toga.Label("Количество букв в слове:", style=Pack(padding=(0, 5)))
        self.main_container.add(self.label_entry_length)
        self.entry_length = toga.TextInput(
            placeholder="введите цифру", 
            style=Pack(padding=(0, 5, 10, 5)),
            on_change=self.validate_numbers,
            readonly=True  # Поле не активно до загрузки слов
        )
        self.main_container.add(self.entry_length)

        # Создаем поле для ввода присутствующих букв в слове
        self.label_entry_present_letters = toga.Label("Буквы которые есть в слове:", style=Pack(padding=(0, 5)))
        self.main_container.add(self.label_entry_present_letters)
        self.entry_present_letters = toga.TextInput(
            placeholder="введите буквы подряд без пробела", 
            style=Pack(padding=(0, 5, 10, 5)),
            on_change=self.validate_letters,
            readonly=True  # Поле не активно до загрузки слов
        )
        self.main_container.add(self.entry_present_letters)

        # Создаем поле для ввода отсутствующих букв в слове
        self.label_entry_absent_letters = toga.Label("Буквы которых точно нет в слове:", style=Pack(padding=(0, 5)))
        self.main_container.add(self.label_entry_absent_letters)
        self.entry_absent_letters = toga.TextInput(
            placeholder="введите буквы подряд без пробела", 
            style=Pack(padding=(0, 5, 10, 5)),
            on_change=self.validate_letters,
            readonly=True  # Поле не активно до загрузки слов
        )
        self.main_container.add(self.entry_absent_letters)

        # Создаем поле для ввода известных букв и их позиций
        self.label_entry_known_letters = toga.Label("Буквы позиция которых известна:", style=Pack(padding=(0, 5)))
        self.main_container.add(self.label_entry_known_letters)
        self.entry_known_letters = toga.TextInput(
            placeholder="введите буквы заменяя неизвестные буквы на *", 
            style=Pack(padding=(0, 5, 10, 5)),
            on_change=self.validate_lettersANDnumbers,
            readonly=True  # Поле не активно до загрузки слов
        )
        self.main_container.add(self.entry_known_letters)

        # Создаем метку для уведомлений
        self.label_notation = toga.Label("", style=Pack(padding=5))
        self.main_container.add(self.label_notation)

        # Создаем поле для вывода результатов
        self.list_result = toga.MultilineTextInput(readonly=True, style=Pack(padding=5, flex=1))
        self.main_container.add(self.list_result)

        # Добавляем контейнер в главное окно
        self.main_window.content = self.main_container
        self.main_window.show()

    # Функция для валидации чисел
    def validate_numbers(self, widget):
        input_text = widget.value
        input_text = re.sub(r'[^0-9]', '', input_text)
        widget.value = input_text.lower()
        self.find_matching_words(widget)

    # Функция для валидации букв
    def validate_letters(self, widget):
        input_text = widget.value
        input_text = re.sub(r'[^а-яА-Я]', '', input_text)
        widget.value = input_text.lower()
        self.find_matching_words(widget)

    # Функция для валидации букв и чисел
    def validate_lettersANDnumbers(self, widget):
        input_text = widget.value
        input_text = re.sub(r'[^а-яА-Я*]', '', input_text)
        widget.value = input_text.lower()
        self.find_matching_words(widget)

    # Функция для загрузки слов
    def load_words(self, widget):
        try:
            # Отображение сообщения о загрузке
            self.display_loading_message()
            
            # Загрузка слов
            response = requests.get(self.WORDS_URL, verify=True)
            if response.status_code == 200:
                self.words = response.text.splitlines()
                self.list_results_update()
                self.display_loaded_words_count(len(self.words))
                self.button_load.text = "Повторно загрузить слова"
                self.update_ui_after_load()
                self.find_matching_words(widget)
            else:
                self.display_error_message()
                return []
        except Exception as e:
            self.display_error_message()
            print(f"Error loading words: {e}")

    def list_results_update(self):
        self.list_result.value = '\n'.join(self.words)

    def display_loading_message(self):
        self.label_notation.text = self.LOADING_MESSAGE
        
    def display_error_message(self):
        self.label_notation.text = self.ERROR_MESSAGE

    def display_loaded_words_count(self, count):
        self.label_notation.text = self.SUCCESS_MESSAGE.format(num=count)

    def update_ui_after_load(self):
        # Активация полей для ввода после загрузки слов
        self.entry_length.readonly = False
        self.entry_present_letters.readonly = False
        self.entry_absent_letters.readonly = False
        self.entry_known_letters.readonly = False

    # Функция для поиска слов
    def find_matching_words(self, widget):

        self.matching_words = []

        desired_length = int(self.entry_length.value) if self.entry_length.value else None
        required_present_letters = self.entry_present_letters.value.lower()
        forbidden_absent_letters = self.entry_absent_letters.value.lower()
        pattern = self.entry_known_letters.value.lower() if self.entry_known_letters.value else None

        for word in self.words:
            if pattern:
                pattern_condition = len(word) >= len(pattern)
                for i, char in enumerate(pattern):
                    if char != '*' and pattern_condition:
                        pattern_condition = word[i] == char
                    if not pattern_condition:
                        break
            else:
                pattern_condition = True

            length_condition = desired_length is None or len(word) == desired_length
            present_letters_condition = not required_present_letters or all(letter in word.lower() for letter in required_present_letters)
            absent_letters_condition = not forbidden_absent_letters or all(letter not in word.lower() for letter in forbidden_absent_letters)

            if length_condition and pattern_condition and present_letters_condition and absent_letters_condition:
                self.matching_words.append(word)

        self.list_result.value = '\n'.join(self.matching_words)

def main():
    return Word5Finder()

if __name__ == '__main__':
    main().main_loop()