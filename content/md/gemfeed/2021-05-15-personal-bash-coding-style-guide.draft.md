# Personal Bash coding style guide

```
   .---------------------------.
  /,--..---..---..---..---..--. `.
 //___||___||___||___||___||___\_|
 [j__ ######################## [_|
    \============================|
 .==|  |"""||"""||"""||"""| |"""||
/======"---""---""---""---"=|  =||
|____    []*          ____  | ==||
//  \\               //  \\ |===||  hjw
"\__/"---------------"\__/"-+---+'
```                     

> Written by Paul Buetow 2021-15-21

Lately, I have been polishing and writing a lot of Bash code. Not that I never wrote a lot of Bash, but now as I also looked through the "Google Shell Style Guide" I thought it is time to also write my thoughts on that. I agree to that guide in most, but not in all points. 

[Gogle Shell Style Guide](https://google.github.io/styleguide/shellguide.html)  

I also highly recommend to have a read through the "Advanced Bash-Scripting Guide" (which is not from Google but written by Mendel Cooper). I learn something new every time I have a look at it.

[Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/)  

## My modifications

These are my personal modifications of the Google Guide.

### 2 space soft-tabs indentation

I know there have been many tab and soft-tab wars on this planet. Google recommends to use 2 space soft-tabs. 

My own reality is I don't really care if I use 2 or 4 space indentations. I agree however that tabs should not be used. I personally tend to use 4 space soft-tabs as that's currently how my personal Vim is configured for any programming languages. What matters most though is consistency within the same script/project.

Google also recommends to limit line length to 80 characters. For some people that seem's to be an ancient habit from the 80's, where all computer terminals couldn't display longer lines. But I think that the 80 character mark is still a good practise at least for shell scripts. For example I am often writing code on a Microsoft Go Tablet PC (running Linux of course) and it comes in very handy if the lines are not too long due to the relatively small display on the device.

I hit the 80 character line length quicker with the 4 spaces, but that makes me refactor the Bash code more aggressively which is actually a good thing. 

### Breaking long pipes

### Quoting your variables

### Prefer internal over external commands

## My additions

### Use of 'yes' and 'no'

### Non-evil alternative to variable assignments via eval

### Prefer pipes over arrays for list processing

## Learned

### Strucking me

### PIPESTATUS






E-Mail me your thoughts at comments@mx.buetow.org!

[Go back to the main site](../)  
