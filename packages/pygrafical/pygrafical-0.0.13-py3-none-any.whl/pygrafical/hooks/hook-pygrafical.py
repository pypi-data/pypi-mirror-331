# my_library/hooks/hook-my_library.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Собираем все подмодули
hiddenimports = collect_submodules('pygrafical')

# Собираем все данные
datas = collect_data_files('pygrafical', include_py_files=True)
