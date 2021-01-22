# MarkdownGeminiConverter

Python code (and CLI tool) to convert from markdown to [gemini](https://gemini.circumlunar.space/ "Gemini project website") and vice versa.

Meant to be used as a CLI tool, or to import methods to other projects.

## Features so far (checked means implemented):

- [x] Convert string from markdown to gemini
- [x] Convert string from gemini to markdown
- [x] Command line interface to access code functions
- [x] Convert all .md files in a folder to gemini (CLI only)
- [x] Convert all .gmni files in a folder to markdown (CLI only)

## Requirements

You only need default Python to use this script, no external libraries were used.

## Usage

Works like most CLI tools with `argparse`. To get started use

    python md2gmni.py -h

which will display the help window:

       -h, --help   show this help message and exit
       -m MARKDOWN  Specify a markdown file or folder.
       -g GEMINI    Specify a gemini file or folder.
       -o OUTPUT    (Optional) Specify a output file or folder.

You are limited to one mode only (either markdown with `-m` or gemini with `-g`). The path of the file or folder is expected as an argument. If you choose a file, the file will be converted. If you choose a folder, *all* files in that folder and its subfolders that are valid `.md` or `.gmni` files will be converted. This may replace your original code, so be careful.

If you specify a output with `-o path` the input will not be overwritten, instead a new file or folder will be created at path. Please note that this file or folder should not already exist.

## Examples

    python md2gmni.py -m readme.md

would replace `readme.md` with gemini text.

    python md2gmni.py -g readme.gmni -o converted.gmni

would convert `readme.gmni` and put it in a new file called `converted.gmni`.

    python md2gmni.py -m website/input -o geminiout

would convert all files in the folder `website/input` into a new folder named `geminiout`.

## Formatting rules and decisions from .md to .gmni

Gemini has only 6 line types, 3 of which are essential and 3 of which are optional:

* Text lines (which work a little like paragraphs in Markdown)
* => Link lines (MUST be its own line. Inline links are not supported.)
* ```Toggle lines (toggles between "raw" and "normal" mode)
* (optional) # Heading lines
* (optional) * Unordered list lines
* (optional) &gt; Quote lines

Markdown allows for a lot more fancy formatting, so to reduce it down to gemini you need to take some artistic liberties, which are listed below:


* Ordered list items get turned into unordered list items
* Any form of identation in lists is lost.
* Nested blockquotes get collapsed into a single blockquote.
* Links that have a title (the optional argument in quotes you can give in Markdown) loose it during the conversion. Only the link address and link text are preserved.
* Any inline emphasis (bold, italics or both) is lost.
* Images get treated as links.
* Any inline styling that has a equivalent in gemini (that's images, code (inline or over multiple lines) and links) is handled by breaking a paragraph into three lines, where the link/image/code has its own line.
* The following Markdown aspects are **not** being considered/supported: Inline html & escaping single characters, line breaks (ending a line with 2 or more whitespaces) don't work either because I'm not sure on how I want them to behave. Reference-style links aren't being translated. Horizontal rules aren't being translated.

## Formatting rules from .gmni to .md

All gemini features have an equivalent in markdown, so no information is lost when converting from `.gmni` to `.md`.

## Disclaimer

This code was written only to help me convert files from `.md` to `.gmni` personally. It's neither ellegant, nor efficient, nor does it support all features of markdown. If things go wrong, or there's bugs, or anything else happens as a result of this code, I'm neither liable, nor responsible. You explicitly agree to this by downloading and using the code. I appreciate bugreports, reporting of issues and improvements, but I can't guarantee I will fix them in a timely manner, if at all. 
