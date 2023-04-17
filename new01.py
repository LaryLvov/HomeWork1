import string
import patoolib
import zipfile
import shutil
import os
import sys
import transliterate
import re

# функция транслитерации


def normalize(name):
    table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z',
        'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', ' ': '_', '(': '_', ')': '_',
        '[': '_', ']': '_', '{': '_', '}': '_', ';': '_', ':': '_', '/': '_', '|': '_', '\\': '_',
        ',': '_', '.': '_', '<': '_', '>': '_', '?': '_', '!': '_', '@': '_', '#': '_', '$': '_',
        '%': '_', '^': '_', '&': '_', '*': '_', '-': '_', '+': '_', '=': '_', '~': '_'
    }
    name = name.lower()
    trans_name = ''
    for char in name:
        trans_name += table.get(char, char)
    return trans_name

# функция обработки папки


def handle_folder(folder):
    images = ['JPEG', 'PNG', 'JPG', 'SVG']
    videos = ['AVI', 'MP4', 'MOV', 'MKV']
    documents = ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']
    music = ['MP3', 'OGG', 'WAV', 'AMR']
    archives = ['ZIP', 'GZ', 'TAR']

    known_extensions = set()
    unknown_extensions = set()
    for root, dirs, files in os.walk(folder):
        for file in files:
            extension = os.path.splitext(file)[-1].upper()[1:]
            known_extensions.add(extension) if extension in images+videos + \
                documents+music+archives else unknown_extensions.add(extension)

            if extension in images:
                dest_folder = os.path.join(folder, "images")
            elif extension in videos:
                dest_folder = os.path.join(folder, "videos")
            elif extension in documents:
                dest_folder = os.path.join(folder, "documents")
            elif extension in music:
                dest_folder = os.path.join(folder, "music")
            elif extension in archives:
                dest_folder = os.path.join(folder, "archives")
            else:
                dest_folder = os.path.join(folder, "other")
                continue
            if not os.path.exists(dest_folder):
                os.mkdir(dest_folder)

            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_folder, normalize(
                os.path.splitext(file)[0]) + os.path.splitext(file)[1])
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(src_file, dest_file)

            if extension in archives:
                try:
                    os.makedirs(os.path.join(
                        dest_folder, os.path.splitext(file)[0]), exist_ok=True)
                    patoolib.extract_archive(dest_file, outdir=os.path.join(
                        dest_folder, os.path.splitext(file)[0]))
                except Exception:
                    print(f"Unable to extract archive {src_file}")

    # удаляем пустые папки
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rmdir(dir_path)
                print(f"Directory {dir_path} removed")
            except OSError:
                print(f"Directory {dir_path} not removed (not empty)")


path_to_clean = "/path/to/clean"
handle_folder(path_to_clean)


def sort_files(path):
    images = []
    videos = []
    documents = []
    music = []
    archives = []
    unknown = []
    extensions = set()

    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)

        if os.path.isdir(file_path):
            subimages, subvideos, subdocuments, submusic, subarchives, subunknown, subextensions = sort_files(
                file_path)
            images += subimages
            videos += subvideos
            documents += subdocuments
            music += submusic
            archives += subarchives
            unknown += subunknown
            extensions.update(subextensions)
            continue

        extension = file_name.split('.')[-1].upper()
        if extension in ('JPEG', 'JPG', 'PNG', 'GIF'):
            handle_images(file_path)
            images.append(file_path)
        elif extension in ('AVI', 'MP4', 'MOV', 'MKV'):
            handle_videos(file_path)
            videos.append(file_path)
        elif extension in ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'):
            handle_documents(file_path)
            documents.append(file_path)
        elif extension in ('MP3', 'OGG', 'WAV', 'AMR'):
            handle_music(file_path)
            music.append(file_path)
        elif extension in ('ZIP', 'GZ', 'TAR'):
            handle_archives(file_path)
            archives.append(file_path)
        else:
            unknown.append(extension)
        extensions.add(extension)

    return images, videos, documents, music, archives, unknown, extensions


# def handle_images(filename):
#     """
#     Обработчик для изображений. Переносит файл в папку images.
#     """
#     move_file(filename, 'images')


# def handle_videos(filename):
#     """
#     Обработчик для видео файлов. Переносит файл в папку video.
#     """
#     move_file(filename, 'video')


# def handle_documents(filename):
#     """
#     Обработчик для документов. Переносит файл в папку documents.
#     """
#     move_file(filename, 'documents')


# def handle_music(filename):
#     """
#     Обработчик для музыкальных файлов. Переносит файл в папку audio.
#     """
#     move_file(filename, 'audio')


def handle_archives(filename):
    """
    Обработчик для архивов. Распаковывает архив и переносит его содержимое в папку archives.
    """
    # Извлекаем имя архива без расширения
    archive_name = os.path.splitext(filename)[0]
    # Создаем папку с именем архива, если ее еще нет
    archive_folder = os.path.join(os.path.dirname(filename), archive_name)
    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)
    # Распаковываем архив
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(archive_folder)
    # Переносим содержимое архива в папку archives
    for dirpath, dirnames, filenames in os.walk(archive_folder):
        for file in filenames:
            move_file(os.path.join(dirpath, file), 'archives')


def move_file(filename, category):
    """
    Переносит файл в указанную категорию.
    """
    # Создаем папку категории, если ее еще нет
    target_folder = os.path.join(os.path.dirname(filename), category)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    # Получаем новое имя файла с помощью функции normalize
    new_filename = os.path.join(
        target_folder, normalize(os.path.basename(filename)))
    # Переименовываем и перемещаем файл
    os.rename(filename, new_filename)


def normalize(filename):
    """
    Функция для нормализации имени файла.
    """
    # Транслитерируем кириллицу в латиницу
    filename = transliterate.translit(filename, 'ru', reversed=True)
    # Заменяем все символы, кроме латинских букв и цифр, на '_'
    new_filename = re.sub(r'[^\w\s\d-]+', '_', filename)
    return new_filename


# Возвращает списки файлов в каждой категории, список известных расширений и список неизвестных расширений
def get_file_lists():
    images = []
    videos = []
    documents = []
    music = []
    archives = []
    extensions = []
    unknown = []

    for filename in os.listdir():
        # Игнорируем директории
        if os.path.isdir(filename):
            continue

        extension = os.path.splitext(filename)[1].lower()

        # if extension in IMAGE_EXTENSIONS


if __name__ == '__main__':
    # Получаем имя папки для сортировки из аргументов командной строки
    if len(sys.argv) != 2:
        print("Usage: python sort.py <folder>")
        sys.exit(1)

folder_path = sys.argv[1]

# Проверяем, что папка существует
if not os.path.isdir(folder_path):
    print(f"{folder_path} is not a directory")
    sys.exit(1)

# Сортируем файлы в указанной папке
images, videos, documents, music, archives, unknown, extensions = sort_files(
    folder_path)


# Выводим отчет о сортировке
print("Sorted files:")
print(f"Images: {len(images)}")
print(f"Videos: {len(videos)}")
print(f"Documents: {len(documents)}")
print(f"Music: {len(music)}")
print(f"Archives: {len(archives)}")
print(f"Unknown: {unknown}")
print(f"Extensions: {extensions}")
