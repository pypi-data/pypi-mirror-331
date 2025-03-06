from importlib.metadata import entry_points

display_eps = entry_points(group='test_atml.display')
try:
    display = display_eps[0].load()
except IndexError:
    def display(text):
        print(text)


def hello_world():
    display('Hello world')



