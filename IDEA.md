# IDEAs

## Parallel job processing queue

Currently, in order to speed up, Gemtexter forks on certain functions and loops and joins (via `wait`) on the sub-processes. This however can be a problem once a user max process limit is reached.

Use s.t. like `pgrep -c -P$$` to determine how many sub-processes are already active and wait for new forks until a lower limit is reached.

## Also generate a PDF book

I could use pandoc for this (convert from Markdown to PDF). This works on Fedora Linux 34:


```
sudo dnf install pandoc wkhtmltopdf
pandoc FOO.md --pdf-engine=wkhtmltopdf --output FOO.pdf
```

The Texlive PDF Engine doesn't work due to missing fonts on Fedora, and there aren't any packages providing the missing fonts.
