# Line breaking playground

Some code for breaking text into lines, inspired by James
O. Achugbue's 1981 paper.

## License
[Simplified BSD](LICENSE)

## Source of the algorithms

The paper _On the Line Breaking Problem in Text Formatting_ by
JameseO. Achugbue was originally published in a special edition of
SIGPLAN Notices
([Proceedings of the ACM SIGPLAN SIGOA Symposium on Text Manipulation,
Portland,
Oregon](https://archive.org/details/sigplan-sigoa-text-manipulation/mode/2up)),
and is available in
[scanned form](line-breaking-text-formatting-achugbue.pdf).
It has been
[transcribed to Markdown](line-breaking-text-formatting.md) with a few
minor typos fixed and some slight changers to layout.

It has its own Copyright notice.

## The code

The various algorithms in the paper have been translated into Python
in file [line_break_from_paper.py](line_break_from_paper.py). The code
is not idiomatic Python, but has tried to stay as close as possible to
the original algorithm. A few changes have been made, as given in
the [notes](NOTES.md).
