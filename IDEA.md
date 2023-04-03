# IDEAs

## Also generate a PDF book

I could use pandoc for this (convert from Markdown to PDF). This works on Fedora Linux 34:

```
sudo dnf install pandoc wkhtmltopdf
pandoc **/*.md --pdf-engine=wkhtmltopdf --output foo.zone.pdf
```

There will be some more scripting required to get the page order and ToC correct.

## More ideas

* Use GNU `source-highlight` for code highlighting in bare-blocks. Can add lang in block beginning.  See also https://www.gnu.org/savannah-checkouts/gnu/src-highlite/style_examples.html
* Automatic ToC generation.
* Sitemap generation.
* More output formats. Gopher? Groff? Plain text? PDF via Pandoc? .sh with interactive menus?
