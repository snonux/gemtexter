The Gemtexter blog engine and static site generator
===================================================

This is the source code of my personal internet site and blog engine. All content is written in Gemini Gemtext format, but the script `gemtexter` generates multiple other static output formats from it. You can reach the site(s)...

* Via Gemini/Gemtext: [gemini://buetow.org](gemini://buetow.org) (You need a Gemini client for this)
* Via "normal" HTML: [https://buetow.org](https://buetow.org) (Actually it's XHTML Transitional 1.0)
* Via [Gemini Webproxy](https://portal.mozz.us/gemini/buetow.org)
* Via [GitHub Markdown](https://github.com/snonux/buetow.org/blob/content-md/index.md)
* Via GitHub Page: [https://alt.buetow.org](https://alt.buetow.org) (from Markdown)

Have a look at the `content-*` branches of the [buetow.org Git](https://github.com/snonux/buetow.org) project for static content examples.

# Getting started

## Requirements

These are the requirements of the `gemtexter` static site generator script:

* GNU Bash 5.x or higher
* ShellCheck installed
* GNU Sed
* GNU Date
* Git

The script was tested on a recent Fedora Linux. For *BSD or macOS you would need to install GNU Sed, GNU Date, and a newer version of Bash.

## Usage

So you want such a pretty internet site too?

To get started, just clone this repo and run `./gemtexter`. You will will be prompted with further instructions.

You will notice soon, that all site content is located in `../buetow.org-content/` (you can configure the `$BASE_CONTENT_DIR` in `gemtexter.conf`). There is one sub-directory per output format, e.g.:

```
../buetow.org-content/gemtext
../buetow.org-content/html
../buetow.org-content/md
../buetow.org-content/meta
```

### Alternative config file path

If you don't want to mess with `gemtexter.conf`, you can use an alternative config file path in `~/.config/gemtexter.conf`, which takes precedence if it exists. Another way is to set the `CONFIG_FILE_PATH` environment variable, e.g.:

```
export CONFIG_FILE_PATH=~/.config/my-site.geek.conf
./gemtexter --generate
```

### What is what

Whereas, you only want to directly edit/add/remove content in the `gemtext` folder. The `gemtexter` then will take the Gemtext and update all other formats accordingly. Summary of what is what is:

* `gemtext`: The Gemini Gemtext markup files of the internet site.
* `html`: The XHTML version of it.
* `md`: The Markdown version of it. 
* `meta`: Some meta data of all Gemtext blog posts. It's used by `gemtexter` internally for Atom feed generation.

### Special HTML configuration

You will find the `./header.html.part` and `./footer.html.part` files, they are minimal template files for the HTML generation.

### Special Markdown configuraiton

`gemtexter` will never touch the `../$BASE_CONTENT_DIR/md/_config.yml` file (if it exists). That's a special configuration file for GitHub Pages.

## Store all formats in Git

I personally have for each directory in `../buetow.org-content/` a separate Git repository configured. So whenever something has changed it will be updated/added/removed to version control. The following will run the generator and commit everything to Git:

```
USE_GIT=yes ./gemtexter --generate
```

And the following will additionally perform a `git pull` and `git push` afterwards;

```
USE_GIT=yes GIT_PUSH=yes ./gemtexter --generate
```

You could add the `USE_GIT` and `GIT_PUSH` options to the `gemtexter.conf` config file too.

## Publishing a blog post

All what needs to be done is to create a new file in `./gemtext/gemfeed/YYYY-MM-DD-article-title-dash-separated.gmi`, whereas `YYYY-MM-DD` defines the publishing date of the blog post.

A subsequent `./gemtexter --generate` will then detect the new post and link it from `$BASE_CONTENT_DIR/gemtext/gemfeed/index.gmi`, link it from the main index `$BASE_CONTENT_DIR/gemtext/index.gmi`, and also add it to the Atom feed at `$BASE_CONTENT_DIR/gemtext/gemfeed/atom.xml`. The first level 1 Gemtext title (e.g. `# Title`) will be the displayed link name. `YYYY-MM-DD` will be the publishing date. There are various other settings, such as Author - they come from the `gemtexter.conf` configuration file.

Once all of that is done, the `gemtexter` script will convert the new post (plus all the indices and the Atom feed) to the other formats too (e.g. HTML, Markdown).

You can also have a look at `$BASE_CONTENT_DIR/meta/gemfeed`. There is a meta file for each blog post stored. These meta files are required for the generation of the Atom feed. You can edit these meta files manually and run `./gemtexter --generate` or `./gemtexter --feed` again, in case you want to change some of the Atom feed content.

## Ready to be published

After running `./gemtexter --generate` you will have all static files ready to be published. But before you do that you could preview the content with `firefox ../buetow.org-content/html/index.html` or `glow ../buetow.org-content/md/index.md` (you get the idea).

Have also a look at the generated `atom.xml` files. They make sense (at least) for Gemtext and HTML.

Now it is up to you to setup a Gemini server for the Gemtext, a Webserver for the HTML and/or a GitHub page for the Markdown format.
