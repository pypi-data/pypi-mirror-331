<img src="https://www.salabim.org/ndots/ndots.png"> 

### Introduction

The `ndots` module contains three special matrix font, to be used in applications:



- fifteendots (5 * 3 font)

  <img src="https://www.salabim.org/ndots/fifteendots.png">  
  
  
  an ultra tiny font (particularly useful for digits)
- fiftydots (10 * 5 font)

  <img src="https://www.salabim.org/ndots/fiftydots.png"> 

  a full fledged font, including many accented letters
- twentyfourdots (8 * 3 font)

  <img src="https://www.salabim.org/ndots/twentyfourdots.png">  

  a tiny font to be used when horizontal space is at a premium

### Installation

```
pip install ndots
```

### Usage

In order to use a font:

`from ndots import fiftydots`

Each font has a couple of methods:



#### grid

```python
def grid(s,
         default=" ",
         intra=1,
         proportional=False,
         width=None,
         align="c",
         narrow=False)
```

returns a list of boolean lists to represent the text s in the font

##### Parameters
s : str
    string to represent

default : str
    if a character has no representation in the font, it will be replaced
    with default, that is a blank by default
    if the length is not 1, a ValueError will be raised

intra : int
    number of dots between characters
    default is 1

proportional : bool
    if proportional is False (default), all characters will be 5 dots wide
    if proportional is True, the actual width of the character will be used
    Note that in case of proportional, a blank will be 2 dots wide.

width : int
    width in dots of the result
    the default is the actal width (no align applied)
    if the actual width is smaller than width, the string will be padded according to the align parameter
    if the actual width is larger than width, the string is chopped according to the align parameter

align : str
    if align starts with a c (default), the result will be centered
    if align starts with a l, the result will be left aligned
    if align starts with a r, the result will be right aligned

narrow : bool
    if False (default), blanks will be 2 wide when proportional is True
    if True, blanks will be 1 wide when proportional is True

##### Returns
the representation of s : list of boolean lists
each set dot will be True, not set False

#### coordinates

```python
def coordinates(s,
                value=True,
                default=" ",
                intra=1,
                proportional=False,
                width=None,
                align="c",
                x_first=False,
                narrow=False,
                x_offset=0,
                y_offset=0)
```

returns a list of coordinates representing the text s in the font

##### Parameters
s : str
    string to represent

value : bool
    if True (default), the set dots will be returned
    if False, the non set dots will be returned

default : str
    if a character has no representation in the font, it will be replaced
    with default, that is a blank by default
    if the length is not 1, a ValueError will be raised

intra : int
    number of dots between characters
    default is 1

proportional : bool
    if proportional is False (default), all characters will be 5 dots wide
    if proportional is True, the actual width of the character will be used
    Note that in case of proportional, a blank will be 2 dots wide.

width : int
    width in dots of the result
    the default is the actal width (no align applied)
    if the actual width is smaller than width, the string will be padded according to the align parameter
    if the actual width is larger than width, the string is chopped according to the align parameter

align : str
    if align starts with a c (default), the result will be centered
    if align starts with a l, the result will be left aligned
    if align starts with a r, the result will be right aligned

x_first : bool
    if False (default), coordinates will be given row by row
    if True, coordinates will be given column by column

narrow : bool
    if False (default), blanks will be 2 wide when proportional is True
    if True, blanks will be 1 wide when proportional is True

x_offset : int
    adds this value to each of the x-coordinates (default 0)

y_offset : int
    adds this value to each of the y-coordinates (default 0)

##### Returns
a list of coordinates (tuples)

#### grid\_to\_str

```python
def grid_to_str(s, leftborder="<", rightborder=">", **kwargs)
```

returns a string representing the given string s, using * if a pixel is set, and a space if not.

each line is prefixed with leftborder and postfixed with rightborder.
all parameters for grid may be given as well.

#### width

`width()` returns the with of the font (3 of 5)

```
fiftydots.width() ==> 5
```

#### height

`height` returns the height of the font (5, 8 or 10)

```
fiftydots.height() ==> 10
```
#### name

`name()` returns the name of the font

```
fiftydots.name() ==> "fiftydots"
```

#### has_char()

`has_char(char)` returns True if char is defined in the font, False if not

```
fiftydots.has_char("A") ==> True
```

The module has one function:

#### available_fonts

ndots.available_fonts() returns a tuple with the three defined fonts

```
"|".join(font.name[5] for font in ndots.available_fonts()) ==> "fifte|fifty|twent"
```