# I would like to add a method to str, like Colorize in Rust, however you cannot do that (easily at least) in Python.
# So I guess you'll have to use it like this:
# superfancy.black(str)

# Also, make sure to import as: from superfancy import *

import superfancy.color
import superfancy.background
import superfancy.style

color = superfancy.color
background = superfancy.background
style = superfancy.style

def addEscapeCharacter(string: str, code: int) -> str:
    """
    .. |language| replace:: Python

    Adds an ASCII escape code to your string:
    ```
    ansi.addEscapeCharacter("Hello, World!", 1) # Bold "Hello, World!"
    ```

    :param string: String to be styled
    :param code: ASCII code to be added
    
    :return: String with ASCII escape code as a prefix
    """
    return "\033[%sm" % str(code) + string

def black(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Black
    ```
    ansi.black("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BLACK)

def red(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Red
    ```
    ansi.red("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.RED)

def green(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Green
    ```
    ansi.green("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.GREEN)

def yellow(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Yellow
    ```
    ansi.yellow("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.YELLOW)

def blue(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Blue
    ```
    ansi.blue("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BLUE)

def magenta(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Magenta
    ```
    ansi.magenta("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.MAGENTA)

def gray(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Gray
    ```
    ansi.gray("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.GRAY)

def brightBlack(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Black (dark gray)
    ```
    ansi.brightBlack("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.DARK_GRAY)

def brightRed(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Red
    ```
    ansi.brightRed("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BRIGHT_RED)

def brightGreen(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Green
    ```
    ansi.brightGreen("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BRIGHT_GREEN)

def brightYellow(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Yellow
    ```
    ansi.brightYellow("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BRIGHT_YELLOW)

def brightBlue(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Blue
    ```
    ansi.brightBlue("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BRIGHT_BLUE)

def brightMagenta(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Magenta
    ```
    ansi.brightMagenta("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BRIGHT_MAGENTA)

def brightCyan(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Cyan
    ```
    ansi.brightCyan("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BRIGHT_CYAN)

def brightGray(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Bright Gray
    ```
    ansi.brightGray("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.BRIGHT_GRAY)

def default(string: str) -> str:
    """
    .. |language| replace:: Python

    Foreground Default
    ```
    ansi.brightGray("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, color.DEFAULT)

def bgBlack(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Black
    ```
    ansi.bgBlack("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BLACK)

def bgRed(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Red
    ```
    ansi.bgRed("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_RED)

def bgGreen(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Green
    ```
    ansi.bgGreen("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_GREEN)

def bgYellow(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Yellow
    ```
    ansi.bgYellow("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_YELLOW)

def bgBlue(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Blue
    ```
    ansi.bgBlue("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BLUE)

def bgMagenta(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Magenta
    ```
    ansi.bgMagenta("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_MAGENTA)

def bgCyan(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Cyan
    ```
    ansi.bgCyan("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_CYAN)

def bgGray(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Gray
    ```
    ansi.bgGray("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_GRAY)

def bgBrightGray(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Gray
    ```
    ansi.bgBrightGray("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_GRAY)

def bgBrightRed(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Red
    ```
    ansi.bgBrightRed("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_RED)

def bgBrightGreen(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Green
    ```
    ansi.bgBrightGreen("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_GREEN)

def bgBrightYellow(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Yellow
    ```
    ansi.bgBrightYellow("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_YELLOW)

def bgBrightBlue(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Blue
    ```
    ansi.bgBrightBlue("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_BLUE)

def bgBrightMagenta(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Magenta
    ```
    ansi.bgBrightMagenta("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_MAGENTA)

def bgBrightCyan(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Cyan
    ```
    ansi.bgBrightCyan("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_CYAN)

def bgBrightGray(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Gray
    ```
    ansi.bgBrightGray("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_BRIGHT_GRAY)

def bgDefault(string: str) -> str:
    """
    .. |language| replace:: Python

    Background Bright Blue
    ```
    ansi.bgBrightBlue("Hello, World!") # "Hello, World!" in the requested color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested color
    """
    return addEscapeCharacter(string, background.BACKGROUND_DEFAULT)

def bold(string: str) -> str:
    """
    .. |language| replace:: Python

    Bold
    ```
    ansi.bold("Hello, World!") # "Hello, World!" in bold
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested style
    """
    return addEscapeCharacter(string, style.BOLD)

def dim(string: str) -> str:
    """
    .. |language| replace:: Python

    dim
    ```
    ansi.dim("Hello, World!") # "Hello, World!" but in a dimmer color
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested style
    """
    return addEscapeCharacter(string, style.DIM)

def italic(string: str) -> str:
    """
    .. |language| replace:: Python

    Italic
    ```
    ansi.italic("Hello, World!") # "Hello, World!" in italic
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested styled
    """
    return addEscapeCharacter(string, style.ITALIC)

def underlined(string: str) -> str:
    """
    .. |language| replace:: Python

    Underline
    ```
    ansi.underlined("Hello, World!") # "Hello, World!" but underlined
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested style
    """
    return addEscapeCharacter(string, style.UNDERLINED)

def blink(string: str) -> str:
    """
    .. |language| replace:: Python

    Blink
    ```
    ansi.blink("Hello, World!") # "Hello, World!" as blinking text
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested style
    """
    return addEscapeCharacter(string, style.BLINK)

def reverse(string: str) -> str:
    """
    .. |language| replace:: Python

    Invert
    ```
    ansi.reverse("Hello, World!") # "Hello, World!" with inverted colors
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested style
    """
    return addEscapeCharacter(string, style.REVERSE)

def concealed(string: str) -> str:
    """
    .. |language| replace:: Python

    Concealed
    ```
    ansi.concealed("Hello, World!") # "Hello, World!" but concealed
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested style
    """
    return addEscapeCharacter(string, style.CONCEALED)

def strikethrough(string: str) -> str:
    """
    .. |language| replace:: Python

    Strikethrough
    ```
    ansi.strikethrough("Hello, World!") # "Hello, World!" but with a strikethrough
    ```

    :param string: String to be styled
    
    :return: Returns the string with the requested style
    """
    return addEscapeCharacter(string, style.STRIKETHROUGH)

# "Python is not a messy language!"
# 643 lines later