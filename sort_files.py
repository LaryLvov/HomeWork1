import zipfile
import shutil
import os
import sys

# винесомо окремо ці значення, та перейменуємо іх як константи
EXTENSIONS = dict(
    images=['JPEG', 'PNG', 'JPG', 'SVG'],
    videos=['AVI', 'MP4', 'MOV', 'MKV'],
    documents=['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
    music=['MP3', 'OGG', 'WAV', 'AMR'],
    archives=['ZIP', 'GZ', 'TAR'],
)


# залишемо лише цю (не будемо використати сторонні пакети)
def normalize(name):
    table = {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'i',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'h',
        'ц': 'c',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sch',
        'ъ': '',
        'ы': 'y',
        'ь': '',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
        ' ': '_',
        '(': '_',
        ')': '_',
        '[': '_',
        ']': '_',
        '{': '_',
        '}': '_',
        ';': '_',
        ':': '_',
        '/': '_',
        '|': '_',
        '\\': '_',
        ',': '_',
        '.': '_',
        '<': '_',
        '>': '_',
        '?': '_',
        '!': '_',
        '@': '_',
        '#': '_',
        '$': '_',
        '%': '_',
        '^': '_',
        '&': '_',
        '*': '_',
        '-': '_',
        '+': '_',
        '=': '_',
        '~': '_',
    }
    name = name.lower()
    trans_name = ''
    for char in name:
        trans_name += table.get(char, char)
    return trans_name


def sort_files(folder):
    # будемо використовувати словник у якості сховища результату
    # це дозволить швидше обробляти дані
    result = {}
    for root, _, files in os.walk(folder):
        for file in files:
            src_file = os.path.join(root, file)
            # отримаємо одразу ім'я та розширення файлу
            # так я позначаю, що не використовую отримане значення
            _, ext = os.path.splitext(file)
            extension = ext[1:].upper()
            folder = 'other'
            # якщо не знайдемо співпадіння по ext то ім'я категорії буде other
            # інакше буде визначено як ім'я ключа до якого належить extension
            for _name, extensions in EXTENSIONS.items():
                if extension in extensions:
                    folder = _name

            try:
                result[folder].append(src_file)
            except KeyError:
                result[folder] = [src_file]

    return result


# зараз також нам ще потрібно вирішити проблему однакових імен
def move_files(folder, sorted_result):
    for _name, files in sorted_result.items():
        print("--------------------------------")
        if _name == 'archives':
            # не обрабляємо archives
            # або можемо тут викликати функцію обробки архивів
            continue
        # створемо шлях
        dest_folder = os.path.join(folder, _name)
        # ця операція створить лише якщо не має (флаг exist_ok=True)
        os.makedirs(dest_folder, exist_ok=True)
        for file in files:
            name, ext = os.path.splitext(file)
            new_name = normalize(name)
            dest_file = os.path.join(dest_folder, new_name + ext)
            # переміщення файлу до пункту призначення
            shutil.move(file, dest_file)


def remove_empty_folder(folder):
    # удаляем пустые папки
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rmdir(dir_path)
                print(f"Directory {dir_path} removed")
            except OSError:
                print(f"Directory {dir_path} not removed (not empty)")


def handle_archives(folder, dest_folder_name, archives):
    dest_folder = os.path.join(folder, dest_folder_name)
    os.makedirs(dest_folder, exist_ok=True)
    # обробимо усі архіви
    for archive in archives:
        archive_name = os.path.splitext(archive)[0]
        archive_folder = os.path.join(folder, archive_name)
        os.makedirs(archive_folder, exist_ok=True)

        with zipfile.ZipFile(archive, 'r') as zip_ref:
            zip_ref.extractall(archive_folder)

        # поки не проводимо нормалізацію імен розпакованих файлів
        # також ми не сортуємо отриманні файли
        # не фіксуємо які файли і куди перемістили
        for root, _, filenames in os.walk(archive_name):
            for file in filenames:
                shutil.move(os.path.join(root, file), dest_folder)


def info_result(result):
    # Выводим отчет о сортировке
    # також тут вже є інформація про архіви
    print("Sorted files:")
    for _name, files in result.items():
        print(f"{_name.capitalize()}: {len(files)}")


if __name__ == '__main__':
    # Получаем имя папки для сортировки из аргументов командной строки
    if len(sys.argv) != 2:
        print("Usage:  <folder>")
        sys.exit(1)

    folder_path = sys.argv[1]

    # Проверяем, что папка существует
    if not os.path.isdir(folder_path):
        print(f"{folder_path} is not a directory")
        sys.exit(1)

    # Сортируем файлы в указанной папке
    # теперб у нас есть возможность применить сортировку к распакованным архивам
    # если вдруг потребуется
    result = sort_files(folder_path)

    move_files(folder=folder_path, sorted_result=result)

    if result.get('archives'):
        handle_archives(
            folder=folder_path,
            dest_folder_name='archives',
            archives=result['archives'],
        )
    remove_empty_folder(folder_path)
    info_result(result)
