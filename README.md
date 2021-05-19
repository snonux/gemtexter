buetow.org Gemini capsule
=========================

This is the source code of my Gemini capsule. You can reach the site(s) here:

* Via Gemini/Gemtext : [gemini://buetow.org](gemini://buetow.org)
* Via HTTP/HTML: [https://buetow.org](https://buetow.org)
* [Gemini Webproxy](https://portal.mozz.us/gemini/buetow.org)
* [GitHub Markdown](https://github.com/snonux/buetow.org/blob/master/content/md/index.md)
* [GitHub Page](https://snonux.github.io/buetow.org)

## Software I use to maintain this capsule

* Text editor: [Vim](https://www.vim.org)
* Gemini server: [a-h/gemini](https://github.com/a-h/gemini)
* Some Bash scripting (GNU Bash probably 5.x or higher required)
* ShellCheck is also required to be installed.

## HTTP fallback software used

* Web server: [Apache HTTPD](https://httpd.apache.org)

# Usage

To get started just clone this repo (master branch) and run `./buetow.org.sh`. You
will will be prompted with further instructions.

Once done, you can edit the Gemtext source and then use the buetow.org.sh script
to generate the other output formats such as:

* HTML
* Markdown (works also with GitHub pages as you saw)
* Meta (that's only generating meta info for the blog post, used for Atom feed generation)

Do a `./buetow.org.sh --help` for a list of all available arguments.

## TODO

These are things I want to do with this project in near future:

* Speed it up a bit: Make it so, that only changed .gmi files (or changed HTML templates) result into re-generating other formats.
* Write a blog post about buetow.org.sh script
* Custom alt.buetow.org domain for GitHub page.
* Read through this README and make sure usage and purpose is clear.
* Add custom config file support (check alt location), and add instructions to the setup wizzard.
* Test + fix on macOS
