# Project description

AI Text Summarizer is a student desktop project that accepts a paragraph and displays a shorter extract containing its first two sentences. Its purpose is to demonstrate Python text processing through a simple application that can be explained and shown during a classroom presentation.

## The problem

A long paragraph can take time to inspect. A short opening extract gives a reader a quick preview. This project provides that preview with a consistent selection rule and a graphical interface. It does not attempt to judge every sentence's importance.

## The method

The program removes outer whitespace, checks for empty input, and separates sentences using a regular expression. If the text contains more than two sentences, it keeps the first two. If there are already two or fewer, the trimmed text stays unchanged. A space joins selected sentences so that punctuation is not duplicated.

This is an extractive method because it takes sentences directly from the source. It does not generate new wording and does not use a trained AI model.

## The desktop application

The original prototype uses Python's Tkinter library. The updated app uses PySide6 for its interface while preserving the same summarization rule. The app includes a workspace, an explanation page, project information, sample text, a guided demonstration, word and sentence counts, file import, copying, and saving.

The Windows setup includes Python and the interface components. It creates a desktop shortcut and allows local use without an online account or API key. The text-processing code is separated from the interface so that the rule can be studied and tested independently.

## Demonstration result

The included sample contains six sentences and 64 words. The generated extract contains two sentences and 24 words. This confirms the expected first-two-sentence behaviour for that example. It does not establish that those two sentences are the most informative ones for every passage.

## Learning outcomes

The project gives practice with strings, lists, conditions, functions, regular expressions, input validation, button callbacks, and reusable code. It also demonstrates the difference between following a clear programming rule and evaluating the quality of a summary.

## Current scope

The app processes typed/pasted text and UTF-8 `.txt` files. The import action accepts files up to 2 MB. It does not import PDF or Word files directly, translate text, check factual accuracy, or identify the most important sentences.

Abbreviations and unusual punctuation can affect sentence splitting. Future work could improve sentence detection, rank sentences, and let users select a summary length.
