# Code explained

This guide explains the project in simple terms. Begin with `summarizer.py`: it contains the rule that creates the summary. Read `app.py` afterward to see how the desktop interface uses that rule.

## 1. The project has two main parts

| Part | File | Purpose |
| --- | --- | --- |
| Text-processing logic | `summarizer.py` | Receives text and returns the selected sentences. |
| Desktop interface | `app.py` | Draws the window, accepts input, handles buttons, and displays output. |

The small `prototype_tkinter.py` file is an additional learning version. It demonstrates the same rule with a simpler window.

## 2. Importing the regular expression module

```python
import re
```

`re` is included with Python. It helps find patterns in text. Here, the pattern describes where one sentence ends and the next begins.

## 3. Defining the sentence pattern

```python
SENTENCE_PATTERN = r"(?<=[.!?])\s+"
```

Read the pattern in small pieces:

| Piece | Meaning |
| --- | --- |
| `r"..."` | A raw Python string, which keeps the backslash in the pattern. |
| `[.!?]` | A full stop, exclamation mark, or question mark. |
| `(?<=...)` | Check what appears immediately before the split position. |
| `\s+` | One or more whitespace characters, such as spaces or line breaks. |

Together, the pattern means: split at whitespace that follows `.`, `!`, or `?`. The punctuation remains in the sentence.

## 4. Separating the sentences

```python
def split_sentences(text):
    return [
        s for s in re.split(SENTENCE_PATTERN, text.strip())
        if s.strip()
    ]
```

`text.strip()` removes whitespace from the beginning and end. `re.split()` divides the string into a list. The `if s.strip()` condition removes empty pieces.

For this input:

```text
Python is readable. It supports desktop apps! We can build projects.
```

The list is:

```python
[
    "Python is readable.",
    "It supports desktop apps!",
    "We can build projects."
]
```

## 5. Creating the summary

```python
def summarize(text):
    text = text.strip()
    if not text:
        return ""

    sentences = split_sentences(text)
    return text if len(sentences) <= 2 else " ".join(sentences[:2])
```

The function first checks whether any text remains. Empty input returns an empty string. The interface is responsible for displaying the request to enter text.

`len(sentences)` counts the list items. With two sentences or fewer, the function returns the trimmed paragraph. Otherwise, `sentences[:2]` selects the first two items and `" ".join(...)` joins them using a space.

The previous three-sentence example becomes:

```text
Python is readable. It supports desktop apps!
```

The function does not decide that those sentences are the most important. It selects them because they occur first.

## 6. Why the code does not add a full stop

The split operation keeps sentence punctuation. Adding `". "` between the sentences would add punctuation that is already present. The current code joins with a space, fixing the repeated full stop in the earlier prototype.

For example:

```python
" ".join(["First sentence.", "Second sentence."])
```

produces:

```text
First sentence. Second sentence.
```

## 7. Counting words

```python
def word_count(text):
    return len(text.split())
```

`split()` without an argument separates text at whitespace. The function then counts the resulting pieces. This is a simple word count, not a detailed language analysis.

The input and summary counts are used to display the reduction in words. The percentage does not measure accuracy or retained meaning.

## 8. Understanding the desktop interface

The updated app uses PySide6, which gives Python access to Qt's desktop interface tools.

| Class used | Simple explanation |
| --- | --- |
| `QApplication` | Starts and manages the desktop application. |
| `QMainWindow` | Provides the main app window. |
| `QPlainTextEdit` | Displays editable input text or read-only output text. |
| `QPushButton` | Provides a clickable action. |
| `QLabel` | Shows a heading, instruction, or other text. |
| `QVBoxLayout` and `QHBoxLayout` | Arrange items vertically and horizontally. |
| `QStackedWidget` | Holds the Workspace, How it works, and Our project pages. |
| `QFileDialog` | Lets the user choose a file to open or a save location. |
| `QPropertyAnimation` | Provides the page fade effect. |

The artwork is painted by the `Artwork` and `Scenery` widgets. These visual elements do not change the summarization rule.

## 9. Important interface functions

| Function or method | What it does |
| --- | --- |
| `make_header()` | Creates the branding, navigation, and offline label. |
| `make_workspace()` | Creates the input/output panels and action controls. |
| `make_process()` | Creates the five-step explanation page. |
| `make_project()` | Creates the team and project-material page. |
| `run_summary()` | Reads input, validates it, calls the summarizer, and updates the result. |
| `input_changed()` | Clears the old summary when the paragraph changes. |
| `load_sample()` | Places the demonstration paragraph into the input panel. |
| `clear()` | Resets both panels and the displayed statistics. |
| `copy_summary()` | Copies the current result to the system clipboard. |
| `open_text()` | Opens a UTF-8 text file and handles reading errors. |
| `save_summary()` | Saves the current result and handles writing errors. |
| `demo_next()` | Moves through the guided classroom demonstration. |
| `navigate()` | Switches the visible app page. |

## 10. What happens after a button click

When the user clicks **Summarize**, Qt calls `run_summary()`. That method gets the text from the input panel, checks for missing input, calls `summarize()`, and places the returned string in the output panel. It then calculates the displayed counts and enables Copy and Save.

When the user changes the paragraph, the input panel sends a `textChanged` signal. The app connects that signal to `input_changed()`. This removes the previous result and disables export until a fresh summary is generated.

This is event-driven programming: actions such as clicks and text changes trigger functions.

## 11. Handling errors

- Empty or whitespace-only input shows a request to enter text.
- A cancelled file dialog leaves the current text alone.
- An unreadable or incorrectly encoded text file produces a readable message.
- An unsuccessful save produces a message instead of claiming the file was saved.

The Windows windowless launch script also catches startup exceptions and tries to write a diagnostic log if the app cannot load.

## 12. The small Tkinter version

`prototype_tkinter.py` is close to the original classroom code. It uses two `Text` widgets and buttons to call summarization and clearing functions. The punctuation issue is fixed, and a `main()` function prevents the window from opening when the module is imported.

It is useful for explaining the project before studying the larger PySide6 interface. The modern version adds presentation and file-handling features around the same core idea.

## 13. What the tests check

`tests/test_app.py` checks both the pure text function and actual interface actions. Examples include empty input, short input, punctuation, Unicode, the demonstration paragraph, copying, saving, importing text, error messages, and navigation.

These checks show whether the app follows its rule. They do not show whether its selected sentences are the best possible summary of a passage.

## 14. A simple explanation for a viva

“Our application reads a paragraph, validates the input, and uses a regular expression to split it into sentences. It displays the first two sentences as an extractive summary. The interface lets users compare the source and output, copy or save the result, and follow a guided demo. It works offline, and the present version uses a fixed rule rather than a trained AI model.”
