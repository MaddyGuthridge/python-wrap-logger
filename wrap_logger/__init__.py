"""
# Wrap Logger

A library to wrap around objects and modules in Python and log property
accesses and calls.

`pip install wrap-logger`

## Rationale

In some cases when programming, errors can break things to the point where
you have no idea where things went wrong, for example, crashing the runtime
environment before a backtrace can be printed. In these cases, it can be
extremely useful to log changes to data that are potentially related to the
issue, but doing so can be tedious and slow. I needed a simple solution to
easily inject logging into objects, and so I created `wrap-logger`.

## Usage

Using `wrap-logger` is simple. Simply call the `wrap` function, which will
return a wrapped version.

### With a module

```py
import foo
from wrap_logger import wrap

# Now all function calls and global reads/writes will be logged
foo = wrap(foo)

# Getting a property causes things to be logged
foo.bar
# [WRAP LOG] > Get  foo.bar
# [WRAP LOG] < Get  foo.bar: gave 42

# Same for setting properties
obj.bar = 43
# [WRAP LOG] > Set  foo.bar: 42 -> 43
# [WRAP LOG] < Set  foo.bar

# And calling functions
obj.echo('hello world')
# [WRAP LOG] > Call foo.echo('hello world')
# [WRAP LOG] < Call foo.echo('hello world'): returned 'hello world'
```

### With a class

```py
from wrap_logger import wrap

class Simple:
    def __init__(self) -> None:
        self.value = 42


# Wrap an instance of the object
obj = wrap(Simple())
```

### Without Pip

`wrap-logger` requires no dependencies, and can even function with some parts
of the standard library missing. Simply head over to the releases tab where the
`wrap-logger.zip` file is attached, then extract it into a new folder within
your project, where you can import it easily.

Here is an example file structure:

```txt
+ program.py
+ wrap_logger/  (you create this folder and place the files into it)
    + __init__.py
    + __wrap_logger.py
    + etc
```

You should then be able to use it normally:

```py
# program.py
from wrap_logger import wrap

...
```

### Logging to a file

`wrap-logger` will write to any file you give it.

```py
import sys
from wrap_logger import wrap

some_object = object()
wrapped = wrap(some_object, output=sys.stderr)
# All logs will go to stderr
```

## Implementation details

`wrap-logger` wraps objects in a `WrapLogger` class. Although the class does
override the `__class__` property so as to fool `isinstance` checks, fooling
the `type` function does not appear to work, so those checks may fail leading
to potentially erroneous behaviour.

## TODOs

`wrap-logger` was thrown together so I could quickly debug another project, so
it is incomplete. If there is demand (hint: create an issue), I will be happy
to try my hand at implementing the following features:

* [ ] Recursive wrapping, so that attributes of attributes are also logged
* [ ] Configuration on what is/isn't logged (currently it just prints
      everything)
* [ ] Figure out what happens if you use `wrap-logger` on itself. Does it
      crash? Does it delete System 32? Does the space-time continuum collapse?
      Who knows!

## MIT License

Copyright (c) 2023 Maddy Guthridge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from .__wrap_logger import wrap

__version__ = '0.2.0'
__all__ = ['wrap']
