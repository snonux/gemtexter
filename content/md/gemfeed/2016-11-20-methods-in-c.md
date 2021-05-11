> Written by Paul Buetow 2016-11-20

[Go back to the main site](../)  

# Methods in C

You can do some sort of object oriented programming in the C Programming Language. However, that is very limited. But also very easy and straight forward to use.

## Example

Lets have a look at the following sample program. Basically all you have to do is to add a function pointer such as "calculate" to the definition of struct "something_s". Later, during the struct initialization, assign a function address to that function pointer:

```
#include <stdio.h>

typedef struct {
    double (*calculate)(const double, const double);
    char *name;
} something_s;

double multiplication(const double a, const double b) {
    return a * b;
}

double division(const double a, const double b) {
    return a / b;
}

int main(void) {
    something_s mult = (something_s) {
        .calculate = multiplication,
        .name = "Multiplication"
    };

    something_s div = (something_s) {
        .calculate = division,
        .name = "Division"
    };

    const double a = 3, b = 2;

    printf("%s(%f, %f) => %f\n", mult.name, a, b, mult.calculate(a,b));
    printf("%s(%f, %f) => %f\n", div.name, a, b, div.calculate(a,b));
}
```

As you can see you can call the function (pointed by the function pointer) the same way as in C++ or Java via:

```
printf("%s(%f, %f) => %f\n", mult.name, a, b, mult.calculate(a,b));
printf("%s(%f, %f) => %f\n", div.name, a, b, div.calculate(a,b));
```

However, that's just syntactic sugar for:

```
printf("%s(%f, %f) => %f\n", mult.name, a, b, (*mult.calculate)(a,b));
printf("%s(%f, %f) => %f\n", div.name, a, b, (*div.calculate)(a,b));
```

Output:

```
pbuetow ~/git/blog/source [38268]% gcc methods-in-c.c -o methods-in-c
pbuetow ~/git/blog/source [38269]% ./methods-in-c
Multiplication(3.000000, 2.000000) => 6.000000
Division(3.000000, 2.000000) => 1.500000
```

Not complicated at all, but nice to know and helps to make the code easier to read!

## The flaw

That's actually not really how it works in object oriented languages such as Java and C++. The method call in this example is not really a method call as "mult" and "div" in this example are not "message receivers". What I mean by that is that the functions can not access the state of the "mult" and "div" struct objects. In C you would need to do something like this instead if you wanted to access the state of "mult" from within the calculate function, you would have to pass it as an argument:

```
mult.calculate(mult,a,b));
```

How to overcome this? You need to take it further...

## Taking it further

If you want to take it further type "Object-Oriented Programming with ANSI-C" into your favorite internet search engine, you will find some crazy stuff. Some go as far as writing a C preprocessor in AWK, which takes some object oriented pseudo-C and transforms it to plain C so that the C compiler can compile it to machine code. This is actually similar to how the C++ language had its origins.

E-Mail me your thoughts at comments@mx.buetow.org!
