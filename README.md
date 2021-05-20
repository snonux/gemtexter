The buetow.org internet site
============================

This is the source code of my personal internet site and blog engine. All content is written in Gemini Gemtext format, but the script `buetow.org.sh` generates multiple other static output formats from it. You can reach the site(s)...

* Via Gemini/Gemtext: [gemini://buetow.org](gemini://buetow.org) (You need a Gemini client for this)
* Via "normal" HTML: [https://buetow.org](https://buetow.org) (Actually it's XHTML Transitional 1.0)
* Via [Gemini Webproxy](https://portal.mozz.us/gemini/buetow.org)
* Via [GitHub Markdown](https://github.com/snonux/buetow.org/blob/content-md/index.md)
* Via [GitHub Page](https://snonux.github.io/buetow.org) (from Markdown)

Have a look at the `content-*` branches of this buetow.org Git project for source samples.

## Software I use to maintain this site

* Text editor: [Vim](https://www.vim.org)
* Gemini server: [a-h/gemini](https://github.com/a-h/gemini)
* Some Bash scripting (GNU Bash probably 5.x or higher required)
* ShellCheck is also required, otherwise `buetow.org.sh` refuses to do anything :-)
* Web server: [Apache HTTPD](https://httpd.apache.org) (for "normal" HTML site)

# Getting started

## Requirements

These are the requirements of the `buetow.org.sh` static site generator script:

* GNU Bash 5.x or higher
* ShellCheck installed
* GNU Sed
* GNU Date
* Git

The script was tested on a recent Fedora Linux. For *BSD or macOS you would need to install GNU Sed, GNU Date, and a newer version of Bash.

## Usage

So you want such a pretty internet site too?

To get started, just clone this repo (master branch) and run `./buetow.org.sh`. You will will be prompted with further instructions.

You will notice soon, that all site content is located in `../buetow.org-content/` (you can configure the `BASE_CONTENT_DIR` in `buetow.org.conf`). There is one sub-directory per output format, e.g.:

```
../buetow.org-content/gemtext
../buetow.org-content/html
../buetow.org-content/md
../buetow.org-content/meta
```

### Alternative config file path

If you don't want to mess with `buetow.org.conf`, you can use an alternative config file path in `~/.config/buetow.org.conf`, which takes precedence if it exists. Another way is to set the `CONFIG_FILE_PATH` environment variable, e.g.:

```
export CONFIG_FILE_PATH=~/.config/my-site.geek.conf
./buetow.org.sh --generate
```

### What is what

Whereas, you only want to directly edit/add/remove content in the `gemtext` folder. The `buetow.org.sh` then will take the Gemtext and update all other formats accordingly. Summary of what is what:

* `gemtext`: The Gemini Gemtext markup files of the internet site.
* `html`: The XHTML version of it.
* `md`: The Markdown version of it. 
* `meta`: Some meta data of all Gemtext blog posts. It's used by `buetow.org.sh` internally for Atom feed generation.

### Special HTML configuration

You will find the `./header.html.part` and `./footer.html.part` files, they are minimal template files for the HTML generation.

### Special Markdown configuraiton

`buetow.org.sh` will never touch the `../buetow.org-content/md/_config.yml` file (if it exists). That's a special configuration file for GitHub Pages.

## Store all formats in Git

I personally have for each directory in `../buetow.org-content/` a separate Git repository configured. So whenever something has changed it will be updated/added/removed to version control. The following will run the generator and commit everything to Git:

```
USE_GIT=yes ./buetow.org --generate
```

And the following will additionally perform a `git pull` and `git push` afterwards;

```
USE_GIT=yes GIT_PUSH=yes ./buetow.org --generate
```

You could add the `USE_GIT` and `GIT_PUSH` options to the `buetow.org.conf` config file too.

## Finito

After running `./buetow.org --genreate` you will have all static files ready to be published. But before you do that you could preview the content with `firefox ../buetow.org-content/html/index.html` or `glow ../buetow.org-content/md/index.md` (you get the idea).

Have also a look at the generated `atom.xml` files. They make sense (at least) for Gemtext and HTML.

Now it is up to you to setup a Gemini server for the Gemtext, a Webserver for the HTML and/or a GitHub page for the Markdowns.

# TODO

These are things I want to do with this project in near future:

* Custom alt.buetow.org domain for GitHub page.
* Test + fix on macOS (I havn't tested it for macOS fully yet)
* Write a blog post about buetow.org.sh script
* Document how to add a blog post.
* Once blog post published request buetow.org.sh to be added to the Awesome Gemini list.
