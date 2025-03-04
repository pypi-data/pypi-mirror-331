# BPrinter | Принтер

[![PyPI version](https://badge.fury.io/py/bprinter.svg)](https://badge.fury.io/py/bprinter)
[![Python](https://img.shields.io/pypi/pyversions/bprinter.svg)](https://pypi.org/project/bprinter/)
[![License](https://img.shields.io/github/license/danilhodos/bprinter.svg)](https://github.com/danilhodos/bprinter/blob/main/LICENSE)

[English](#english) | [Русский](#русский)

<a name="english"></a>
## 🌈 BPrinter - Powerful Cross-Platform Terminal Styling Library

BPrinter is a feature-rich library for terminal text styling that works seamlessly across Windows, macOS, and Linux.

### 📦 Installation

```bash
pip install bprinter
```

### 🚀 Quick Start

```python
from bprinter import Color, Background, Style

# Simple color usage
print(Color.RED + "Red text" + Style.RESET)

# Combining styles
print(Color.BLUE + Background.WHITE + Style.BOLD + "Bold blue text on white background" + Style.RESET)

# Using context manager
with Style.color('red'):
    print("This text is red")
    print("And this one too")
```

### ✨ Features

- 🎨 16 basic colors and 256 extended colors
- 🖌 RGB color support
- ✏️ Text styling (bold, italic, underline, etc.)
- 🔤 ASCII art generation
- 📝 Markdown-like text formatting
- 🖥 Cross-platform compatibility
- 🎯 Simple and intuitive API
- 🛠 Extensible architecture

### 🎨 Advanced Usage

#### Logging with Styles

```python
from bprinter import BPrinter

bp = BPrinter(show_time=True)

bp.success("Operation completed successfully!")
bp.error("An error occurred")
bp.warning("Warning: Low memory")
bp.info("Processing data...")
bp.debug("Debug information")
```

#### ASCII Art

```python
from bprinter import ASCIIArtGenerator

# Create ASCII art
print(ASCIIArtGenerator.render("Hello!", color="red"))

# Preview different fonts
print(ASCIIArtGenerator.preview_fonts("ABC"))
```

#### Text Formatting

```python
from bprinter import Printer

printer = Printer(enable_formatting=True)

printer("This is **bold** and _italic_ text")
printer("Use `code` and {red|colored text}")
```

### 📚 Documentation

For detailed documentation and examples, visit our [GitHub repository](https://github.com/DGaliaf/bprinter).

---

<a name="русский"></a>
## 🌈 BPrinter - Мощная кросс-платформенная библиотека для стилизации текста в терминале

BPrinter - это многофункциональная библиотека для стилизации текста в терминале, которая работает на Windows, macOS и Linux.

### 📦 Установка

```bash
pip install bprinter
```

### 🚀 Быстрый старт

```python
from bprinter import Color, Background, Style

# Простое использование цветов
print(Color.RED + "Красный текст" + Style.RESET)

# Комбинирование стилей
print(Color.BLUE + Background.WHITE + Style.BOLD + "Жирный синий текст на белом фоне" + Style.RESET)

# Использование контекстного менеджера
with Style.color('red'):
    print("Этот текст красный")
    print("И этот тоже")
```

### ✨ Возможности

- 🎨 16 базовых цветов и 256 расширенных цветов
- 🖌 Поддержка RGB цветов
- ✏️ Стилизация текста (жирный, курсив, подчеркивание и др.)
- 🔤 Генерация ASCII арта
- �� Форматирование текста в стиле Markdown
- 🖥 Кросс-платформенная совместимость
- 🎯 Простой и интуитивно понятный API
- 🛠 Расширяемая архитектура

### 🎨 Продвинутое использование

#### Логирование со стилями

```python
from bprinter import BPrinter

bp = BPrinter(show_time=True)

bp.success("Операция успешно завершена!")
bp.error("Произошла ошибка")
bp.warning("Внимание: Мало памяти")
bp.info("Обработка данных...")
bp.debug("Отладочная информация")
```

#### ASCII Арт

```python
from bprinter import ASCIIArtGenerator

# Создание ASCII арта
print(ASCIIArtGenerator.render("Привет!", color="red"))

# Предпросмотр разных шрифтов
print(ASCIIArtGenerator.preview_fonts("АБВ"))
```

#### Форматирование текста

```python
from bprinter import Printer

printer = Printer(enable_formatting=True)

printer("Это **жирный** и _курсивный_ текст")
printer("Используйте `код` и {red|цветной текст}")
```

### 📚 Документация

Подробная документация и примеры доступны в нашем [GitHub репозитории](https://github.com/DGaliaf/bprinter).

## 📄 License | Лицензия

MIT License 