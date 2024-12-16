import os
import tarfile
import pytest
from unittest import mock
from Unixshell import VShell


@pytest.fixture
def shell():
    with mock.patch('tarfile.open', autospec=True) as mocked_tarfile:
        mock_tarfile_instance = mock.MagicMock()
        mocked_tarfile.return_value = mock_tarfile_instance

        # Создаем объекты tarfile для файлов и директорий
        tarinfo1 = tarfile.TarInfo(name='/file1.txt')
        tarinfo1.size = 100  # добавляем размер, чтобы можно было "прочитать" файл
        dirinfo1 = tarfile.TarInfo(name='dir1/')
        dirinfo1.size = 0
        tarinfo2 = tarfile.TarInfo(name='/file2.txt')
        tarinfo2.size = 200
        dirinfo2 = tarfile.TarInfo(name='dir2/')
        dirinfo2.size = 0
        
        # Возвращаем список объектов как "члены" архива
        mock_tarfile_instance.getmembers.return_value = [tarinfo1, tarinfo2, dirinfo1, dirinfo2]

        # Мокаем extractfile для разных файлов
        mock_file1 = mock.MagicMock()
        # Замокируем read() для возврата байтов
        mock_file1.read.return_value = b"This is file1 content"
        # Замокируем decode() для возврата строки
        mock_file1.decode.return_value = "This is file1 content"

        mock_file2 = mock.MagicMock()
        mock_file2.read.return_value = b"This is file2 content"
        mock_file2.decode.return_value = "This is file2 content"

        # Настроим extractfile так, чтобы возвращать разные файлы в зависимости от имени
        def extractfile_mock(file):
            if file.name == '/file1.txt':
                return mock_file1
            elif file.name == '/file2.txt':
                return mock_file2
            else:
                raise ValueError(f"Unexpected file: {file.name}")

        mock_tarfile_instance.extractfile.side_effect = extractfile_mock

        shell_instance = VShell("testfs.tar", "testuser", "localhost")
        shell_instance.text_area = mock.Mock()
        return shell_instance


def test_ls(shell):
    shell.ls()
    shell.text_area.insert.assert_called_once_with('end', "file1.txt  file2.txt    \n")
    assert shell.currentpath == ""
    assert shell.filesystemlist[0].name == '/file1.txt'


def test_cat(shell):

    # Проверка на отсутствие файла
    shell.cat("nonexistent.txt")
    shell.text_area.insert.assert_called_with('end', "Error: File 'nonexistent.txt' not found.\n")
    shell.cat("file5.txt")
    shell.text_area.insert.assert_called_with('end', "Error: File 'file5.txt' not found.\n")

def test_cd(shell):
    shell.cd('Dir1')
    shell.text_area.insert.assert_called_with('end', "Directory 'Dir1' does not exist.\n")
    assert shell.currentpath == ''

def test_mv(shell):
    shell.mv('/file1.txt', 'file1_renamed.txt')
    shell.text_area.insert.assert_called_with('end', "Moved '/file1.txt' to 'file1_renamed.txt.\n")
    assert (file.name == '/file1_renamed.txt' for file in shell.filesystemlist)
    shell.mv('nonexistent.txt', 'newname.txt')
    shell.text_area.insert.assert_called_with('end', "Error: File 'nonexistent.txt' not found.\n")

def test_rev(shell):
    shell.rev("nonexistent.txt")
    shell.text_area.insert.assert_called_with('end', "Error: File 'nonexistent.txt' not found.\n")
    shell.rev("file5.txt")
    shell.text_area.insert.assert_called_with('end', "Error: File 'file5.txt' not found.\n")