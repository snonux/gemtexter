# Also generate a PDF book

I could use pandoc for this (convert from Markdown to PDF). This works on Fedora Linux 34:


```
sudo dnf install pandoc wkhtmltopdf
pandoc FOO.md --pdf-engine=wkhtmltopdf --output FOO.pdf
```

The Texlive PDF Engine doesn't work due to missing fonts on Fedora, and there aren't any packages providing the missing fonts.
