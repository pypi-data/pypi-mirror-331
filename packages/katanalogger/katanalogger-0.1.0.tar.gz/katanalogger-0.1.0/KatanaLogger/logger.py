
import time
import random
import inspect
import os, sys
import platform
import traceback
from datetime import datetime
from rich.progress import Progress
from colorama import Fore, Style, init

init(autoreset=True)

class Decorators:
    @staticmethod
    def ms(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            Decorators._log_execution_time(func, execution_time)
            return result

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            Decorators._log_execution_time(func, execution_time)
            return result
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


    @staticmethod
    def _log_execution_time(func, execution_time):
        if int(execution_time) in (8, 9, 10, 11, 12, 13):
            print(Fore.RED + f"Функция '{func.__name__}' выполнена за {execution_time:.2f} мс 👎")
        elif int(execution_time) in (7, 6, 5):
            print(Fore.YELLOW + f"Функция '{func.__name__}' выполнена за {execution_time:.2f} мс 👍")
        elif int(execution_time) in (5, 4, 3, 2, 1, 0):
            print(Fore.GREEN + f"Функция '{func.__name__}' выполнена за {execution_time:.2f} мс 👍")
        else:
            print(Fore.MAGENTA + f"Функция '{func.__name__}' выполнена за {execution_time:.2f} мс 👎")

class Logger:
    __slots__ = ('colors', 'random_color', 'bold', 'emoji', 'time_log', 'msg_default_logger')
    def __init__(self, colors: list = [], random_color: bool = False, bold: bool = True, 
    emoji: dict = None,
    time_log: bool = True, msg_default_logger: bool = True):
        
        self.colors = colors
        self.random_color = random_color
        self.bold = bold
        self.time_log = time_log
        self.msg_default_logger = msg_default_logger
        if emoji is None or emoji is False:
            self.emoji = {}
        elif emoji is True:
            self.emoji = {1: "😎", 2: "🚫", 3: "🔴"}
        else:
            self.emoji = emoji
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
    async def get_emoji(self, emoji_status: int) -> str:
        if self.emoji:
            if emoji_status in self.emoji:
                emoji_list = self.emoji[emoji_status].split("\n")
                return random.choice(emoji_list).replace(" ", "")
        return ""
    
    #@Decorators.ms
    async def perfect_log(self, log: str, status: str):
        if self.time_log:
            status_styles = {
                "success": (f"{Fore.GREEN}", "[INFO"),
                "failed": (f"{Fore.RED}", "[ERROR"),
                "warning": (f"{Fore.YELLOW}", "[WARNING"),
            }
        else:
            status_styles = {
                "success": (f"{Fore.GREEN}", "[INFO]"),
                "failed": (f"{Fore.RED}", "[ERROR]"),
                "warning": (f"{Fore.YELLOW}", "[WARNING]"),
            }

        style, label = status_styles.get(status, (f"{Style.BRIGHT}{Fore.WHITE}", "[UNKNOWN]"))
        if self.emoji:
            emoji = await self.get_emoji(1 if status == "success" else 2 if status == "failed" else 3) if bool(self.emoji) else ""
        else:
            emoji = ""
        if self.time_log:
            style, label = status_styles[status]
            time_str = datetime.now().strftime("%H:%M:%S")
            log_message = f"{style}{label}|{time_str}]{emoji} {log}"
        else:
            log_message = f"{style}{label} {log}"
        if self.bold:
            log_message = "\033[1m" + log_message + "\033[0m"
        print(log_message)

    async def die(self, log_msg: str):
        await self.perfect_log(log_msg, "failed")

    async def debug(self, log_msg: str):
        await self.perfect_log(log_msg, "warning")

    async def log(self, log_msg: str):
        await self.perfect_log(log_msg, "success")
    async def log_traceback(self, exception: Exception):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
        traceback_message = "".join(traceback_details)
        await self.perfect_log(f"Exception occurred:\n{traceback_message}", "failed")
        

    @staticmethod
    def wait_progress(time_to_step: float = 0.2, advance: float = 0.5, color: str = "red", text: str = "", total: int = 1000, finish_msg: str = ""):
        with Progress() as progress:
            task1 = progress.add_task(f"[{color}]{text}", total=total)
            while not progress.finished:
                progress.update(task1, advance=advance)
                time.sleep(time_to_step)
        print("\033[1m" + Fore.GREEN + finish_msg + "\033[0m")
        return ""
