buetow.org Gemini capsule
=========================

This is the source code of my Gemini capsule. You can reach the site(s) here:

* Via Gemini/Gemtext : [gemini://buetow.org](gemini://buetow.org)
* Via HTTP/HTML: [https://buetow.org](https://buetow.org)
* [Markdown via HTML viewer](./content/md/index.md)
* [Gemini via webproxy](https://portal.mozz.us/gemini/buetow.org)

## Software I use to maintain this capsule

* Text editor: [Vim](https://www.vim.org)
* Gemini server: [a-h/gemini](https://github.com/a-h/gemini)
* Some Bash scripting

## HTTP fallback software used

* Web server: [Apache HTTPD](https://httpd.apache.org)

## TODO

Adjust code to reflect the google style guide. Use this to practice navigating the Vim quickfix list.

* comment complex functions
* comment all lib functions
* TODOs always with a name in it, e.g. "TODO(paul): BLabla"
* Breaking long pipes: Here I disagree, use a different long pipe breaking method and not the one in the google style guide.
* case: indent body with 2 spaces
* not agreeing w "quote your variables", only quote them then its making things clearer
* fix signle vs double quotes: strings without var interpolation
* not a google style: use strings yes and no as my own bools
* prefer quoting words not bare words: yes vs 'yes'
* [[ ]] is preferred over [ ]
* what struck me: "probably unintended lexicographical comparison
* eval (evil) should be avoided: my own alternative for setting vars w.o eval
* arrays: i personally try to design the script to use pipes for list processing.
* bash -c 'help readarray' trick, zsh alias/function for bash help
* avoid a stand alone (( i++ ))
* rename ./modules to ./packages
* buetow.org.conf: declare -xr FOO=bar both constant and env.
* learned: PIPESTATUS stuff 
* don't agree partially: prefer internal over external (e.g. sed)
