import ctypes

lib = 0

def get_path_to_hooks():
    return '\\'.join(str(__file__).split('\\')[:-1])+'\\hooks'

def init():
    # Загрузка библиотеки
    global lib
    lib = ctypes.CDLL('\\'.join(str(__file__).split('\\')[:-1])+'\\lib.so')  # Для Linux
    # lib = ctypes.CDLL('./lib.dll')  # Для Windows
    # lib = ctypes.CDLL('./lib.dylib')  # Для macOS

    # Определение типа функции loop_function
    # lib.loop_function.argtypes = [ctypes.c_int]
    # lib.loop_function.restype = None
    lib.DrawCustomText.argtypes = [ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p]
    lib.DrawCustomText.restype = None

    lib.set_window_resizable.argtypes = [ctypes.c_bool]
    lib.set_window_resizable.restype = None

    lib.set_iteration.argtypes = [ctypes.CFUNCTYPE(None)]
    lib.set_iteration.restype = None

    lib.set_start.argtypes = [ctypes.CFUNCTYPE(None)]
    lib.set_start.restype = None

    # Определение типа функции test
    # lib.test.argtypes = []
    # lib.test.restype = None
    lib.window_sating.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p]
    lib.window_sating.restype = None
    # Создание C-совместимой функции
    lib.load_image.argtypes = [ctypes.c_char_p, ctypes.c_wchar_p]
    lib.load_image.restype = None

    lib.image.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
    lib.image.restype = None

    lib.Main.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.Main.restype = ctypes.c_int

    # lib.toggleWindowBorder.argtypes = []
    # lib.toggleWindowBorder.restype = None

    # lib.moveWindowToMouse.argtypes = []
    # lib.moveWindowToMouse.restype = None

    # lib.drawImage.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
    # lib.drawImage.restype = None

def load_image(name, path):
    # Загрузка изображения
    image_name = ctypes.c_char_p(bytes(name, "utf-8"))
    image_path = ctypes.c_wchar_p(path)
    lib.load_image(image_name, image_path)

def image(x, y, w, h, name):
    lib.image(x, y, w, h, bytes(name, "utf-8"))

def text(fp, x, y, size, txt):
    lib.DrawCustomText(bytes(fp, "utf-8"), x, y, size, bytes(txt, "utf-8"))

def window_sating(w, h, path):
    lib.window_sating(w, h, ctypes.c_wchar_p(path))

def start_render(funk_iteration,funk_start):
    # Параметры для функции Main
    if funk_iteration == None:
        def a():
            pass
        funk_iteration=a
    hInstance = ctypes.c_void_p()
    hPrevInstance = ctypes.c_void_p()
    lpCmdLine = ctypes.c_char_p(b"")
    nCmdShow = ctypes.c_int(1)
    CMPFUNC = ctypes.CFUNCTYPE(None)
    s_cfunc=CMPFUNC(funk_start)
    t_cfunc = CMPFUNC(funk_iteration)
    lib.set_iteration(t_cfunc)
    lib.set_start(s_cfunc)
    # Вызов функции
    try:
        lib.Main(hInstance, hPrevInstance, lpCmdLine, nCmdShow)
    except OSError:
        pass

def loading(list):
    for i in list:
        load_image(i.split('\\')[-1].split('.')[0], i)

def get_hwnd():
    return lib.get_hwnd()

def set_window_resizable(resizable):
    lib.set_window_resizable(ctypes.c_bool(resizable))

def update_window_size_to_fit_images():
    lib.update_window_size_to_fit_images()

if __name__ == "__main__":
    init()
    loading(["2.png"])
    window_sating(400, 300, ".\\icon.ico")
    def funk_start():
        set_window_resizable(1)

    def iterations():
        image(375, 0, 125, 125, '2')
        lib.update_window_size_to_fit_images()

    # Установить окно как нерастяжимое


    start_render(iterations,funk_start)

    # Получить hwnd окна
    hwnd = get_hwnd()
    print(f"HWND: {hwnd}")