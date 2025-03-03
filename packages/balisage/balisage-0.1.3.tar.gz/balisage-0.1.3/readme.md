<div align="center">

<img src="https://raw.githubusercontent.com/jakebrehm/balisage/main/img/logo.png" alt="balisage Logo" style="width: 100%;"/>

<h1>Use Python to build HTML.</h1>

<br>

<a href="https://github.com/jakebrehm/balisage"><img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/jakebrehm/balisage?color=F16529&logo=Git&logoColor=white&style=for-the-badge"></a>
<a href="https://github.com/jakebrehm/balisage/blob/main/license.txt"><img alt="GitHub License" src="https://img.shields.io/github/license/jakebrehm/balisage?color=F16529&style=for-the-badge"></a>
<a href="https://pypi.org/project/balisage/"><img alt="PyPI Page" src="https://img.shields.io/pypi/v/balisage?color=F16529&logo=pypi&logoColor=white&style=for-the-badge"></a>
<a href="https://github.com/jakebrehm/balisage/actions/workflows/tests.yaml"><img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/jakebrehm/balisage/tests.yaml?label=tests&color=F16529&logo=github&logoColor=white&style=for-the-badge"></a>
<a href="https://codecov.io/gh/jakebrehm/balisage"><img alt="Codecov Test Coverage" src="https://img.shields.io/codecov/c/gh/jakebrehm/balisage?token=W6CWUDTYZC&color=F16529&logo=codecov&logoColor=white&style=for-the-badge"></a>

<br>

<p>
    <strong>balisage</strong> is a Python package that allows you to generate HTML using an intuitive and easy-to-use interface.
</p>

</div>

<img src="https://raw.githubusercontent.com/jakebrehm/balisage/main/img/divider.png" alt="balisage Section Divider" style="width: 100%;"/>

## Table of contents

- [Installation](#installation)
  - [Dependencies](#dependencies)
- [Licensing](#licensing)
- [Example usage](#example-usage)
  - [Creating a basic page](#creating-a-basic-page)
- [Background](#background)
- [Future improvements](#future-improvements)
- [Authors](#authors)

## Installation

`balisage` is available on [PyPI](https://pypi.org/project/balisage/) and can be installed using `pip`:

```bash
pip install balisage
```

The source code can be viewed on [GitHub](https://github.com/jakebrehm/balisage).

### Dependencies

Currently, the minimum required Python version is **3.11**.

`balisage` only uses the Python standard library, which means you don't need to install any additional dependencies to use it.

However, for some more advanced features, you may need to install extra optional dependencies:

<table align="center">
  <tr>
    <th>Extra</th>
    <th>Description</th>
    <th>Dependencies</th>
  </tr>
  <tr>
    <td><code>data</code></td>
    <td>Work with dataframes</td>
    <td><a href="https://pypi.org/project/pandas/"><code>pandas</code></a></td>
  </tr>
  <tr>
    <td><code>formatting</code></td>
    <td>Format HTML nicely</td>
    <td><a href="https://pypi.org/project/beautifulsoup4/"><code>beautifulsoup4</code></a></td>
  </tr>
</table>

You can install these dependencies using the command

`pip install balisage[<extra>]`

where `<extra>` is the name of the extra dependency group.

To install multiple extra dependencies at once, you can use

`pip install balisage[<extra>,<extra>,...]`

## Licensing

This project is licensed under the [MIT License](https://github.com/jakebrehm/balisage/blob/main/license.txt).

## Example usage

The [`samples`](https://github.com/jakebrehm/balisage/blob/main/samples) directory has more examples, which include source code and output, but see below for a quick example of how to use the package.

### Creating a basic page

To create a basic page, you can use the `Page` object and its `add` method. You can also specify stylesheets to link using the `stylesheets` argument.

```python
from balisage import (
  Attributes, Classes, Heading1, Page, Paragraph
)

# Create a page
page = Page(
    title="Sample Page",
    stylesheets=["./style.css"],
)

# Add some elements
page.add(
    Heading1(
      "Heading",
      classes=Classes("title", "large"),
      attributes=Attributes({"id": "title"}),
    ),
    Paragraph(
      "Some text",
      attributes=Attributes({"style": "color: red;"}),
    ),
)

# Save the page
page.save("sample_page.html")
```

## Background

The `balisage` package was originally created to generate hyper-customizable HTML tables from Pandas dataframes, since `DataFrame.to_html()` has very limited styling options. That said, it has since been expanded to include a wider range of HTML elements with support for more advanced features such as Pythonic ways to add classes and attributes.

Admittedly, other tools like `balisage` exist, and many are more mature. However, its creation provided an interesting opportunity to practice Python packaging and unit testing, as well as the ability to learn modern tools, including [`uv`](https://github.com/astral-sh/uv), [`ruff`](https://github.com/astral-sh/ruff), and [`pytest`](https://pypi.org/project/pytest/). Additionally, it was the perfect way to implement CI pipelining using [GitHub Actions](https://github.com/features/actions).

Lastly, the package's name _balisage_ is the French word for _markup_ (as in _markup languages_); the word's true context may have been lost in translation, but it sounds fun, unique, and leaves room to expand to other markup languages in the future.

## Future improvements

Some ideas for future improvements, from highest priority to lowest priority:

- Add the rest of the HTML elements
  - _Version 1.0_ will include the most common elements
- Refactor unit tests to use a class-based approach
  - Primarily for readability and structure
- Improve documentation (docstrings, web docs, etc.)
- Validate that user-specified attributes are valid HTML attributes
  - The current philosophy is that it is the user's responsibility to validate their attributes
  - However, attribute validation may be desirable, especially since classes are already validated
- Expand to other markup languages, such as Markdown

<img src="https://raw.githubusercontent.com/jakebrehm/balisage/main/img/divider.png" alt="balisage Section Divider" style="width: 100%;"/>

## Authors

- **Jake Brehm** - [Email](mailto:mail@jakebrehm.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)
