The Gemtexter blog engine and static site generator
===================================================

This is the source code of my personal internet site and blog engine. All content is written in Gemini Gemtext format, but the script `gemtexter` generates multiple other static output formats from it. You can reach the site(s)...

* Via Gemini/Gemtext: [gemini://foo.zone](gemini://foo.zone)  (You need a Gemini client for this)
* Via "normal" HTML: [https://foo.zone](https://foo.zone) (Actually it's XHTML Transitional 1.0)
* Via [Gemini Webproxy](https://portal.mozz.us/gemini/foo.zone)
* Via [Codeberg Markdown](https://codeberg.org/snonux/foo.zone/src/branch/content-md/index.md)
* Via Codeberg Page (with custom domain): [https://www2.buetow.org](https://www2.buetow.org) (from HTML)
* Via GitHub Page: It's possible to create a GitHub page from the Markdown output but I won't demo it anymore as I moved this project to Codeberg.

Have a look at the `content-*` branches of the [foo.zone Git](https://codeberg.org/snonux/foo.zone) project for static content examples.

# Getting started

## Requirements

These are the requirements of the `gemtexter` static site generator script:

* GNU Bash 5.x or higher
* ShellCheck installed
* GNU Sed
* GNU Date
* Git

The script is tested on a recent Fedora Linux. For *BSD or macOS, you would need to install GNU Sed, GNU Date, and a newer version of Bash.

## Usage

So you want such a pretty internet site too?

To get started, clone this repo and run `./gemtexter`. You will be prompted with further instructions.

You will notice soon that all site content is located in `../foo.zone-content/` (you can configure the `$BASE_CONTENT_DIR` in `gemtexter.conf`). There is one sub-directory per output format, e.g.:

```
../foo.zone-content/gemtext
../foo.zone-content/html
../foo.zone-content/md
../foo.zone-content/meta
```

### Alternative config file path

If you don't want to mess with `gemtexter.conf`, you can use an alternative config file path in `~/.config/gemtexter.conf`, which takes precedence if it exists. Another way is to set the `CONFIG_FILE_PATH` environment variable, e.g.:

```
export CONFIG_FILE_PATH=~/.config/my-site.geek.conf
./gemtexter --generate
```

### What is what

Whereas you only want to edit the content in the `gemtext` folder directly. The `gemtexter` then will take the Gemtext and update all other formats accordingly. Summary of what is what:

* `gemtext`: The Gemini Gemtext markup files of the internet site.
* `html`: The XHTML version of it.
* `md`: The Markdown version of it. 
* `meta`: Some metadata of all Gemtext blog posts. It's used by `gemtexter` internally for Atom feed generation.

### Special HTML configuration

You will find the `./header.html.part` and `./footer.html.part` files, they are minimal template files for the HTML generation. There's also the `style.css` for HTML.

### Special HTML configuration

`gemtexter` will never touch the `../$BASE_CONTENT_DIR/html/.domains`, as this is a required file for a Codeberg page. Furthermore, the `robots.txt` file won't be overridden as well.

### Special Markdown configuration for GitHub pages

`gemtexter` will never touch the `../$BASE_CONTENT_DIR/md/_config.yml` file (if it exists). That's a particular configuration file for GitHub Pages. `gemtexter` also will never modify the file `../$BASE_CONTENT_DIR/md/CNAME`, as this is also a file required by GitHub pages for using custom domains.

## Store all formats in Git

I personally have for each directory in `../foo.zone-content/` a separate Git repository configured. So whenever something has changed, it will be updated/added/removed to version control. The following will run the generator and commit everything to Git:

```
USE_GIT=yes ./gemtexter --generate
```

And the following will additionally perform a `git pull` and `git push` afterwards;

```
USE_GIT=yes GIT_PUSH=yes ./gemtexter --generate
```

You could add the `USE_GIT` and `GIT_PUSH` options to the `gemtexter.conf` config file too.

## Publishing a blog post

All that needs to be done is to create a new file in `./gemtext/gemfeed/YYYY-MM-DD-article-title-dash-separated.gmi`, whereas `YYYY-MM-DD` defines the publishing date of the blog post.

A subsequent `./gemtexter --generate` will then detect the new post and link it from `$BASE_CONTENT_DIR/gemtext/gemfeed/index.gmi`, link it from the main index `$BASE_CONTENT_DIR/gemtext/index.gmi`, and also add it to the Atom feed at `$BASE_CONTENT_DIR/gemtext/gemfeed/atom.xml`. The first level 1 Gemtext title (e.g. `# Title`) will be the displayed link name. `YYYY-MM-DD` will be the publishing date. Various other settings, such as Author, come from the `gemtexter.conf` configuration file.

Once all of that is done, the `gemtexter` script will convert the new post (plus all the indices and the Atom feed) to the other formats, too (e.g. HTML, Markdown).

You can also have a look at `$BASE_CONTENT_DIR/meta/gemfeed`. There is a metafile for each blog post stored. These metafiles are required for the generation of the Atom feed. You can edit these metafiles manually and run `./gemtexter --generate` or `./gemtexter --feed` again if you want to change some of the Atom feed content.

## Ready to be published

After running `./gemtexter --generate`, you will have all static files ready to be published. But before you do that, you could preview the content with `firefox ../foo.zone-content/html/index.html` or `glow ../foo.zone-content/md/index.md` (you get the idea).

Have also a look at the generated `atom.xml` files. They make sense (at least) for Gemtext and HTML.

It is up to you to set up a Gemini server for the Gemtext, a Webserver for the HTML or a GitHub page for the Markdown format (or both).

# Future features

I might or might not implement those:

* Templating of .gmi files (e.g. insert %%TOC%% to Gemtext files as well). Could also template common .gmi page headers and footers. Could also insert bash code here.
* Automatic ToC generation.
* Sitemap generation.
* More output formats. Gopher? Groff? Plain text? PDF via Pandoc? .sh with interactive menus?
