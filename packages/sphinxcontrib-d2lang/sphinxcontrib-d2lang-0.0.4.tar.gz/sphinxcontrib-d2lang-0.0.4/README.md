# sphinxcontrib-d2lang

This is a Sphinx extension for [d2lang](https://d2lang.com/). 

## Usage

### Install

```bash
$ pip install sphinxcontrib-d2lang
```

### Adding the extension

`conf.py`

```python
extensions = [
    "sphinxcontrib.d2lang",
]
```

### Adding a diagram (inline)

You can use d2lang in sphinx directive

`source/index.rst`

```
Hello World
===========

.. d2lang::

    hello -> world
```


### Adding a diagram (external file)

You can use an external file like this

```
Hello World
===========

.. d2lang:: helloworld.d2

```

### Options

There is two options you can use

- layout
- filename

#### Layout engine

You can specify layout engine to use

```rest
Hello World
===========

.. d2lang::
   :layout: elk

    hello -> world
```

#### Output filename

```rest
Hello World
===========

.. d2lang::
   :filename: d2lang_files/helloworld.svg

    hello -> world
```

