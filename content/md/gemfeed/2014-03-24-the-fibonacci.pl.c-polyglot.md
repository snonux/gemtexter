# The fibonacci.pl.c Polyglot

> Written by Paul Buetow 2014-03-24

In computing, a polyglot is a computer program or script written in a valid form of multiple programming languages, which performs the same operations or output independent of the programming language used to compile or interpret it

[https://en.wikipedia.org/wiki/Polyglot_(computing)](https://en.wikipedia.org/wiki/Polyglot_(computing))  

## The Fibonacci numbers

For fun, I programmed my own Polyglot, which is both, valid Perl and C code. The interesting part about C is, that $ is a valid character to start variable names with:

```
#include <stdio.h>

#define $arg function_argument
#define my int
#define sub int
#define BEGIN int main(void)

my $arg;

sub hello() {
	printf("Hello, welcome to Perl-C!\n");
	printf("This program is both, valid C and Perl code!\n");
	printf("It calculates all fibonacci numbers from 0 to 9!\n\n");
	return 0;
}

sub fibonacci() {
	my $n = $arg;

	if ($n < 2) {
		return $n;
	}

	$arg = $n - 1;
	my $fib1 = fibonacci();
	$arg = $n - 2;
	my $fib2 = fibonacci();

	return $fib1 + $fib2;
}

BEGIN {
	hello();
	my $i = 0;

	for ($i = 0; $i <= 10; ++$i) {
		$arg = $i;
		printf("fib(%d) = %d\n", $i, fibonacci());
	}

	return 0;
}
```

You can find the whole source code at GitHub:

[https://github.com/snonux/perl-c-fibonacci](https://github.com/snonux/perl-c-fibonacci)  

### Let's run it with Perl:

```
❯ perl fibonacci.pl.c
Hello, welcome to Perl-C!
This program is both, valid C and Perl code!
It calculates all fibonacci numbers from 0 to 9!

fib(0) = 0
fib(1) = 1
fib(2) = 1
fib(3) = 2
fib(4) = 3
fib(5) = 5
fib(6) = 8
fib(7) = 13
fib(8) = 21
fib(9) = 34
fib(10) = 55
```


### Let's compile it as C and run the binary:

```
❯ gcc fibonacci.pl.c -o fibonacci
❯ ./fibonacci
Hello, welcome to Perl-C!
This program is both, valid C and Perl code!
It calculates all fibonacci numbers from 0 to 9!

fib(0) = 0
fib(1) = 1
fib(2) = 1
fib(3) = 2
fib(4) = 3
fib(5) = 5
fib(6) = 8
fib(7) = 13
fib(8) = 21
fib(9) = 34
fib(10) = 55
```

It's really fun to play with :-).

E-Mail me your thoughts at comments@mx.buetow.org!

[Go back to the main site](../)  
