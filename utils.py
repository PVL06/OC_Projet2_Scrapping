import aiohttp
import aiohttp.client_exceptions


''' Custom request function with error control '''


async def fetch(session: aiohttp.ClientSession, url: str) -> str | None:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
            else:
                print(f'Request error {response.status} for url : {url}\n')
                return None
    except aiohttp.client_exceptions.ClientConnectorError:
        print(f'Client connection error\n')
    else:
        return html
    

''' Custom progress bar '''


class Format:
    # Colors
    GREEN = '\033[0;32m'
    PURPLE = "\033[0;35m"
    END = "\033[0m"
    # Cursors
    DARK_SHADE = '\u2593'
    LIGHT_SHADE = '\u2591'
    # Line cursor
    # replace N by number of lines
    LINE_UP = '\x1B[NA'
    # Status
    RUN = f'{PURPLE}[RUN.....] {END}'
    COMPLETE = f'{GREEN}[COMPLETE] {END}'


class Bar(Format):
    def __init__(self, title: str, total_step: int, width: int = 50) -> None:
        self.title = title.capitalize()
        self.total_step = total_step
        self.width = width
        self.step = 0
        self.complete = False
        self.line = self._update_line()

    def increase(self) -> str | None:
        if not self.complete:
            self.step += 1
            if self.step == self.total_step:
                self.complete = True
            self.line = self._update_line()
        return self.line
    
    def _update_line(self) -> str:
        status = self.COMPLETE if self.complete else self.RUN
        bar_color = self.GREEN if self.complete else self.PURPLE
        normalize_bar = round(self.step * self.width / self.total_step)
        progress_bar = f"{self.DARK_SHADE * normalize_bar}{self.LIGHT_SHADE * (self.width - normalize_bar)}"
        counter = f"{str(self.step)}/{self.total_step}"
        line = f"{status} {self.title}: {bar_color}|{progress_bar}|{self.END} [{counter}]"
        return line
            

class Progress:
    def __init__(self, title: str, total_step: int, width: int = 50) -> None:
        self.bar = Bar(title, total_step, width)

    def up(self) -> None:
        if not self.bar.complete:
            print(self.bar.increase(), end='\r')
            if self.bar.complete:
                print(end='\n')
