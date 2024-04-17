import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import requests

class Word5Finder(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(300, 400))
        self.main_container = toga.Box(style=Pack(direction=COLUMN, padding=5))

        self.label_notation = toga.Label("Поиск по файлу russian_words.txt", style=Pack(padding=5))
        self.main_container.add(self.label_notation)

        self.label_instructions = toga.Label("Введите параметры поиска:", style=Pack(padding=(5, 5)))
        self.main_container.add(self.label_instructions)

        self.entry_length = toga.TextInput(placeholder="Длина слова", style=Pack(padding=(5, 5)))
        self.main_container.add(self.entry_length)

        self.entry_present_letters = toga.TextInput(placeholder="Присутствующие буквы", style=Pack(padding=(5, 5)))
        self.main_container.add(self.entry_present_letters)

        self.entry_absent_letters = toga.TextInput(placeholder="Отсутствующие буквы", style=Pack(padding=(5, 5)))
        self.main_container.add(self.entry_absent_letters)

        self.entry_known_letters = toga.TextInput(placeholder="Известные буквы и позиция через пробел, для разделения запятая (а 2, е 4)", style=Pack(padding=(5, 5)))
        self.main_container.add(self.entry_known_letters)

        self.button_search = toga.Button("Поиск", on_press=self.find_word, style=Pack(padding=(5, 5)))
        self.main_container.add(self.button_search)

        self.list_result = toga.DetailedList(style=Pack(padding=(5, 5), flex=1))
        self.main_container.add(self.list_result)

        self.main_window.content = self.main_container
        self.main_window.show()

        self.words = self.load_words()

    def load_words(self):
        url = 'https://raw.githubusercontent.com/it4sru/find5word/main/russian_words.txt'
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.splitlines()
        else:
            return []

    def find_word(self, widget):
        if not any([self.entry_length.value, self.entry_present_letters.value, self.entry_absent_letters.value, self.entry_known_letters.value]):
            return

        found_words = []

        length = self.entry_length.value and int(self.entry_length.value)
        present_letters = self.entry_present_letters.value.lower()
        absent_letters = self.entry_absent_letters.value.lower()
        known_letters = [tuple(item.split()) for item in self.entry_known_letters.value.lower().split(',')] if self.entry_known_letters.value else []

        for line in self.words:
            words = line.split()
            for word in words:
                if (not length or len(word) == length) and (not present_letters or all(letter in word.lower() for letter in present_letters)) and (not absent_letters or all(letter not in word.lower() for letter in absent_letters)):
                    if not known_letters or all(word[int(pos)-1] == letter for letter, pos in known_letters):
                        found_words.append(word)

        self.list_result.data = found_words

def main():
    return Word5Finder()

# main logic
if __name__ == '__main__':
    main().main_loop()
