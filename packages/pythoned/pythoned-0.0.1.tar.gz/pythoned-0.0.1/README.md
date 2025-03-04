# `pythoned`

### *PYTHON EDitor: edit lines via Python expressions*

> For those knowing Python and tired of forgetting `sed`/`awk`/`grep`/`tr` syntaxes.

## install
```bash
pip install pythoned
```
(it installs `pythoned` in your PATH)

## edit
The provided Python expression must be an `str`. It manipulates the line stored in the variable `_: str`:

```bash
# get last char of each line
echo -e 'f00\nbar\nf00bar' | pythoned '_[-1]'
```
output:
```
0
r
r
```

## filter
If the expression is a `bool` instead of an `str`, then the lines will be filtered according to it:
```bash
# keep only lines containing a zero
echo -e 'f00\nbar\nf00bar' | pythoned '"0" in _'
```
output:
```
f00
f00bar
```

### modules auto-import

Modules are auto-imported, example with `re`:
```bash
# replace digits by Xs
echo -e 'f00\nbar\nf00bar' | pythoned 're.sub(r"\d", "X", _)'
```
output:
```
fXX
bar
fXXbar
```