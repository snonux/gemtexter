buetow.org Gemini capsule
=========================

This is the source code of my Gemini capsule. You can reach the site(s) here:

* Via Gemini/Gemtext : [gemini://buetow.org](gemini://buetow.org)
* Via HTTP/HTML: [https://buetow.org](https://buetow.org)
* [Markdown via HTML viewer](./content/md/index.md)
* [GitHub page](https://snonux.github.io/buetow.org/)
* [Gemini via webproxy](https://portal.mozz.us/gemini/buetow.org)

## Software I use to maintain this capsule

* Text editor: [Vim](https://www.vim.org)
* Gemini server: [a-h/gemini](https://github.com/a-h/gemini)
* Some Bash scripting

## HTTP fallback software used

* Web server: [Apache HTTPD](https://httpd.apache.org)

## TODO

These are things I want to do with this project in near future:

* Make it work on macOS, as it currently doesn't fully (Only ensure correct Bash version?)
* Auto generate ./index.md for github page
* Speed it up a bit: Make it so, that only changed .gmi files (or changed HTML templates) result into re-generating other formats.
* Write a blog post about buetow.org.sh script
