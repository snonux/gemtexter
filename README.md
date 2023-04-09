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

## External Licenses

Gemtexter uses some external TrueType fonts for the HTML output. For license information please look into all [font sub-directories of the HTML extras folder](./extras/html). But to summarize, all fonts are free for personal use.

# Getting started

## Requirements

These are the requirements for running the `gemtexter` static site generator script:

* GNU Bash 5.x or higher
* GNU Sed
* GNU Date
* GNU Grep
* GNU Source Highlight (optional for source code highlighting of bare text blocks)
* Git (optional for version control)
* ShellCheck installed (optional for testing)
* XMLLint (optional for validating the atom feed syntax)

The script is tested on a recent Fedora Linux. For *BSD or macOS, you would need to install GNU Sed, GNU Date, GNU Grep and a newer version of Bash.

## Usage

So you want such a pretty internet site too?

To get started, clone this repo and run `./gemtexter`. You will be prompted with further instructions.

You will notice soon that all site content is located in `../foo.zone-content/` (you can configure the `$BASE_CONTENT_DIR` in `gemtexter.conf`). There is one sub-directory per output format, e.g.:

```
../foo.zone-content/gemtext
../foo.zone-content/html
../foo.zone-content/md
```

### What is what

Whereas you only want to edit the content in the `gemtext` folder directly. The `gemtexter` then will take the Gemtext and update all other formats accordingly. Summary of what is what:

* `gemtext`: The Gemini Gemtext markup files of the internet site. This can also contain Gemtext template files.
* `html`: The XHTML version of it.
* `md`: The Markdown version of it. 
* `cache`: Some volatile cache data for speeding up Atom feed generation.

## Store all formats in Git

It is advisable to store `$BASE_CONTENT_DIR/{gemtext,html,md}` in a separate Git repository each. Gemtexter automatically detects whether one of these directories is in Git. It is then possible to run `./gemtexter --git-add` command for adding all new and changed files to Git and `./gemtexter --git-sync` for synchronizing everything with the remote repositories.  The `GIT_COMMIT_MESSAGE` environment variable can be set to for customizing the Git commit message (E.g.: `GIT_COMMIT_MESSAGE='New blog post' ./gemtexter --git-add`.

## Publishing a blog post

What needs to be done is to create a new file in `$BASE_CONTENT_DIR/gemtext/gemfeed/YYYY-MM-DD-article-title-dash-separated.gmi`, whereas `YYYY-MM-DD` defines the publishing date of the blog post.

A subsequent `./gemtexter --generate` will then detect the new post and link it from `$BASE_CONTENT_DIR/gemtext/gemfeed/index.gmi`, link it from the main index `$BASE_CONTENT_DIR/gemtext/index.gmi`, and also add it to the Atom feed at `$BASE_CONTENT_DIR/gemtext/gemfeed/atom.xml`.

* The first level 1 Gemtext title (e.g. `# Title here`) will be the displayed link name from the `index.gmi`'s mentioned above.
* By default, the last modification time of the Gemtext file will be the publishing date. Gemtexter will add a `> Published at TIMESTAMP` right underneath the title if that line isn't there yet. That timestamp will be used for subsequent `atom.xml` feed generations as the feed entry timestamp.
* Various other settings, such as Author, come from the `gemtexter.conf` configuration file. 

An example blog posts looks like this:

```
% cat gemfeed/2023-02-26-title-here.gmi
# Title here

> Published at 2023-02-26T21:43:51+01:00

The remaining content of the Gemtext file...
```

Once all of that is done, the `gemtexter` script will convert the new post (plus all the indices and the Atom feed) to the other formats, too (e.g. HTML, Markdown).

## Ready to be published

After running `./gemtexter --generate`, you will have all static files ready to be published. But before you do that, you could preview the content with `firefox $BASE_CONTENT_DIR/html/index.html` or `glow $BASE_CONTENT_DIR/md/index.md` (you get the idea).

Have also a look at the generated `$BASE_CONTENT_DIR/{gemtext,html}/gemfeed/atom.xml` Atom feed files.

If you use git, you can use `./gemtexter --publish`, which does a `--generate` followed by a `--git-add` and a `--git-sync`.

It is up to you to set up a Gemini server for the Gemtext, a webserver for the HTML or a GitHub page for the Markdown format (or both). You could also set up a cron job on your server to periodically pull new Gemtext, HTML and Markdown content from your Git repository.

## Advanced usage

### Content filter

Once your capsule reaches a certain size it can become annoying to re-generate everything if you only want to preview one single content file. The following will add a filter to only generate the files matching a regular expression:

```
./gemtexter --generate '.*hello.*'
```

This will help you to quickly review the results once in a while. Once you are happy you should always re-generate the whole capsule before publishing it! Note, that there will be no Atom feed generation in filter mode so before publishing it you should always run a full `--generate`.

### Source code highlighting

The HTML output supports source code highlighting. The requirement is to have the `source-highlight` command, which is GNU Source Highlight, to be installed. Once done, you can annotate a bare block with the language to be highlighted. E.g.:

```
 ```bash
 if [ -n "$foo" ]; then
   echo "$foo"
 fi
 ...
```

Please run `source-highlight --lang-list` for a list of all supported languages.

### Templating

Since version `2.0.0`, Gemtexter supports templating. A template file name must have the suffix `gmi.tpl`. A template must be put into the same directory as the Gemtext `.gmi` file to be generated. Gemtexter will generate a Gemtext file `index.gmi` from a given template `index.gmi.tpl`. All lines starting with `<< ` will be evaluated as a single line of Bash code and the output will be written into the resulting Gemtext file. A `<<<` and `>>>` encloses a multiline template.

For example, the template `index.gmi.tpl`:

```
# Hello world

<< echo "> This site was generated at $(date --iso-8601=seconds) by \`Gemtexter\`"

Welcome to this capsule!

<<<
  for i in {1..10}; do
    echo Multiline template line $i
  done
>>>
```

... results into the following `index.gmi` after running `./gemtexter --generate` (or `./gemtexter --template`, which instructs to do only template processing and nothing else):

```
# Hello world

> This site was generated at 2023-03-15T19:07:59+02:00 by `Gemtexter`

Welcome to this capsule!

Multiline template line 1
Multiline template line 2
Multiline template line 3
Multiline template line 4
Multiline template line 5
Multiline template line 6
Multiline template line 7
Multiline template line 8
Multiline template line 9
Multiline template line 10
```

Another thing you can do is insert an index with links to similar blog posts. E.g.:

```
See more entries about DTail and Golang:

<< template::inline::index dtail golang

Blablabla...
```

... scans all other post entries with `dtail` and `golang` in the file name and generates a link list like this:

```
See more entries about DTail and Golang:

=> ./2022-10-30-installing-dtail-on-openbsd.gmi 2022-10-30 Installing DTail on OpenBSD
=> ./2022-04-22-programming-golang.gmi 2022-04-22 The Golang Programming language
=> ./2022-03-06-the-release-of-dtail-4.0.0.gmi 2022-03-06 The release of DTail 4.0.0
=> ./2021-04-22-dtail-the-distributed-log-tail-program.gmi 2021-04-22 DTail - The distributed log tail program (You are currently reading this)

Blablabla...
```

### Alternative configuration file path

If you don't want to mess with `gemtexter.conf`, you can use an alternative config file path in `~/.config/gemtexter.conf`, which takes precedence if it exists. Another way is to set the `CONFIG_FILE_PATH` environment variable, e.g.:

```
export CONFIG_FILE_PATH=~/.config/my-site.geek.conf
./gemtexter --generate
```

### Special HTML configuration

You will find the `./extras/html/header.html.part` and `./extras/html/footer.html.part` files, they are minimal template files for the HTML generation. There's also the `./extras/html/style.css` for HTML.

`gemtexter` will never touch the `$BASE_CONTENT_DIR/html/.domains`, as this is a required file for a Codeberg page. Furthermore, the `robots.txt` file won't be overridden as well.

### Special Markdown configuration for GitHub pages

`gemtexter` will never touch the `$BASE_CONTENT_DIR/md/_config.yml` file (if it exists). That's a particular configuration file for GitHub Pages. `gemtexter` also will never modify the file `$BASE_CONTENT_DIR/md/CNAME`, as this is also a file required by GitHub pages for using custom domains.

Happy gemtexting!!
