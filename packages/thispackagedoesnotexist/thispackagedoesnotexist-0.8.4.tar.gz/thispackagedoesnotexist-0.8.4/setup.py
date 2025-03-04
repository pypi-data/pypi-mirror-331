from setuptools import setup, find_packages

setup(
    name="thispackagedoesnotexist",
    version="0.8.4",
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "pycryptodome",
        "pyaudio",
        "pillow",
        "mss",
        "pyautogui",
        "opencv-python",
        "python-socketio",
        "websocket-client",
        "requests",
        "pywin32",
        "pynput",
        "WMI",
        "psutil"
    ],
)

