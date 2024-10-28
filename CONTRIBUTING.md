# Contributing

> Always code as if the person who ends up maintaining your code is a violent psychopath who knows where you live.

> [C2 Wiki:Code For The Maintainer](https://wiki.c2.com/?CodeForTheMaintainer#:~:text=Always%20code%20as,learning%20from%20it.)

As I will be the only maintainer, that is true

The code should be self-documenting. We should use comments sparingly and only when necessary.

Use constants to store magic variables. 

It should be easy to understand what the code does by reading, main.py. 

It should be clear clear what a function does by it's name.

Extract helper functions which add clutter, whose purposes are obvious and do not help understanding the code should be put in utils.py. like DateEncoder.

Comments which are written must be maintained.

Functions in main.py should be order by operation
1. Download
2. Write
3. Read
4. Parse

Within each operation, they should be ordered by page
1. Search
2. Job

Within page they should be ordered by scope
1. Single Page
2. All Pages for Portal
3. All Pages for All Portals
