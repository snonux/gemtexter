# IDEAs

## Also generate a PDF book

I could use pandoc for this (convert from Markdown to PDF). This works on Fedora Linux 34:

```
sudo dnf install pandoc wkhtmltopdf
pandoc **/*.md --pdf-engine=wkhtmltopdf --output foo.zone.pdf
```

There will be some more scripting required to get the page order and ToC correct.

## More ideas

* Sitemap generation.
* More output formats. Gopher? Groff? Plain text? PDF via Pandoc? .sh with interactive menus?
* Use https://github.com/alecthomas/chroma as a syntax highlighter
