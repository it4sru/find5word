import toga
import re
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import requests

class Word5Finder(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(300, 600))
        self.main_container = toga.Box(style=Pack(direction=COLUMN, padding=5))

        self.button_load = toga.Button("Загрузить слова", on_press=self.load_words, style=Pack(padding=5))
        self.main_container.add(self.button_load)

        self.label_instructions = toga.Label("Введите параметры поиска:", style=Pack(padding=5))
        self.main_container.add(self.label_instructions)

        self.entry_length = toga.TextInput(
            placeholder="Количество букв в слове", 
            style=Pack(padding=5),
            on_change=self.validate_numbers
        )
        self.main_container.add(self.entry_length)

        self.entry_present_letters = toga.TextInput(
            placeholder="Присутствующие буквы в слове", 
            style=Pack(padding=5),
            on_change=self.validate_letters
        )
        self.main_container.add(self.entry_present_letters)

        self.entry_absent_letters = toga.TextInput(
            placeholder="Отсутствующие буквы в слове", 
            style=Pack(padding=5),
            on_change=self.validate_letters
        )
        self.main_container.add(self.entry_absent_letters)

        self.entry_known_letters = toga.TextInput(
            placeholder="Известные буквы и позиция по возрастанию (а2 е4)", 
            style=Pack(padding=5),
            on_change=self.validate_lettersANDnumbers
        )
        self.main_container.add(self.entry_known_letters)

        self.button_search = toga.Button("Поиск", on_press=self.find_word, style=Pack(padding=5))
        self.main_container.add(self.button_search)

        self.label_notation = toga.Label("", style=Pack(padding=5))
        self.main_container.add(self.label_notation)

        self.list_result = toga.MultilineTextInput(readonly=True, style=Pack(padding=5, flex=1))
        self.main_container.add(self.list_result)

        self.main_window.content = self.main_container
        self.main_window.show()

    def validate_numbers(self, widget):
        input_text = widget.value
        input_text = re.sub(r'[^0-9]', '', input_text)
        widget.value = input_text.lower()
        self.find_word(widget)

    def validate_letters(self, widget):
        input_text = widget.value
        input_text = re.sub(r'[^а-яА-Я]', '', input_text)
        input_text = re.sub(r'ёЁ', 'е', input_text)
        widget.value = input_text.lower()
        self.find_word(widget)

    def validate_lettersANDnumbers(self, widget):
        input_text = widget.value
        input_text = re.sub(r'[^а-яА-Я 0-9]', '', input_text)
        input_text = re.sub(r'\s+', ' ', input_text)
        input_text = re.sub(r'ёЁ', 'е', input_text)
        widget.value = input_text.lower()
        self.find_word(widget)

    def load_words(self, widget):
        self.label_notation.text = "Загрузка слов ..."
        
        url = 'https://raw.githubusercontent.com/it4sru/find5word/main/russian_words.txt'
        response = requests.get(url)

        if response.status_code == 200:
            self.words = response.text.splitlines()
            self.list_result.value = '\n'.join(self.words)
            self.label_notation.text = f"Загружено {len(self.words)} слов (сущ. ед. числ.)"
            self.button_load.text = "Повторно загрузить слова"
        else:
            self.label_notation.text = "Ошибка загрузки слов"
            return []
            
    def find_word(self, widget):
        if not self.list_result.value:
            self.label_notation.text = "Загрузите слова"
            return
        if not any([self.entry_length.value, self.entry_present_letters.value, self.entry_absent_letters.value, self.entry_known_letters.value]):
            self.label_notation.text = "Введите параметры поиска"
            return

        self.found_words = []

        length = self.entry_length.value and int(self.entry_length.value)
        present_letters = self.entry_present_letters.value.lower()
        absent_letters = self.entry_absent_letters.value.lower()
        known_letters = [tuple(item) for item in self.entry_known_letters.value.lower().split(' ')] if self.entry_known_letters.value else []

        for word in self.words:
            if (not length or len(word) == length) and (not present_letters or all(letter in word.lower() for letter in present_letters)) and (not absent_letters or all(letter not in word.lower() for letter in absent_letters)):
                if not known_letters or all(word[int(pos)-1] == letter for letter, pos in known_letters):
                    self.found_words.append(word)

        self.list_result.value = '\n'.join(self.found_words)


def main():
    return Word5Finder()

if __name__ == '__main__':
    main().main_loop()
