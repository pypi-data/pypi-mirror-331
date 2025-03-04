import re
import textwrap


RX_DOCSTRING = re.compile(
    r"""\A
    (?P<title> (?!\s*>>> ) .+?)           # not PS1 line
    ( (?:\n[ \t]*$)+ \n (?P<body>.*?) )?
    \Z""",
    flags=re.DOTALL | re.MULTILINE | re.VERBOSE,
)
RX_EXAMPLE_BLOCK = re.compile(
    r"""
    # Example block consists of a PS1 line followed by non-blank line
    #   or a series of blank lines followed by PS1 line.
    ^(?= [ ]* >>> )  # starts with PS1 line
    (?:
       [ ]* >>> .*                       $  # PS1 line
      |\n (?![ ]*$) .+                   $  # non-blank line
      |(?: \n [ ]* $)+ (?= \n [ ]* >>> ) $  # blank lines followed by PS1 line
    )*
    \n
    """,
    flags=re.MULTILINE | re.VERBOSE,
)


def get_title(item):
    """
    Get title component of the docstring.

    Title is the first block of non-blank lines up to the first blank line.
    Title lines, if multiple, are joined.

    Args:
        item (``object`` | ``str`` | ``None``):
            input to be converted. If ``item`` is ``str``, it will be used as input,
            otherwise ``item.__doc__`` will be used. If input is blank or
            ``None``, empty string is returned.

    Returns:
        ``str``: may be empty string.
    """
    title, _ = parse_title_body(get_doc(item, dedent=True), parse_title=True)
    return title or ''


def get_body(item, remove_title=True, dedent=True):
    """
    Get body component of the docstring.

    Body is the rest of the text after removing title, and, if not empty, always ends
    with newline.

    Args:
        item (``object`` | ``str`` | ``None``):
            input to be converted. If ``item`` is ``str``, it will be used as input,
            otherwise ``item.__doc__`` will be used. If input is blank or
            ``None``, empty string is returned.
        remove_title (``bool``, optional):
            whether to remove title; defaults to ``True``.
        dedent (``bool``, optional):
            whether to apply `textwrap.dedent` first; defaults to ``True``.

    Returns:
        `str`: may be empty string.
    """
    _, body = parse_title_body(get_doc(item, dedent=dedent), parse_title=remove_title)
    return body or ''


def to_markdown(item, title_depth=2, dedent=True, include_title=True):
    """
    Convert docstring to `Markdown <https://www.markdownguide.org>`_.

    The first block of non-blank lines up to first blank line represents test case
    title. It is joined in one line and formatted as section heading.

    Every doctest block is formatted as code block.

    Args:
        item (``object`` | ``str`` | ``None``):
            input to be converted. If ``item`` is `str`, it will be used as input,
            otherwise ``item.__doc__`` will be used. If input is blank or
            ``None``, empty string is returned.
        title_depth (``int`` | ``None``, optional):
            heading level for test case title; defaults to ``2``. If ``None``,
            title is not matched and becomes a part of the body text.
        dedent (``bool``, optional):
            `textwrap.dedent` is applied to the docstring by default; this can be
            turned off by passing ``dedent=False``.
        include_title (``bool``, optional):
            whether to include docstring title in the output; defaults to ``True``.

    Returns:
        ``str``: Markdown formatted text; may be empty.

    Example:

        For ``SimpleCase`` from `~doctestcase.case.doctestcase` example,

        .. code:: pycon

            >>> from doctestcase import to_markdown
            >>> to_markdown(SimpleCase)

        .. code:: markdown

            ## Title

            Paragraph.

            ```pycon
            >>> X * 100
            'yzyz...'
            ```

            Another paragraph.

            ```pycon
            >>> None
            >>> True
            True
            ```
    """
    doc = get_doc(item, dedent=dedent)
    title, body = parse_title_body(doc, parse_title=title_depth is not None)
    if not title and not body:
        return ''

    chunks = []
    if title and include_title:
        chunks.append('{} {}\n'.format('#' * title_depth, title))

    if body:
        if title and include_title:
            chunks.append('\n')
        for item in parse_body_items(body):
            if isinstance(item, ExampleBlock):
                chunks.extend(('```pycon\n', item, '```\n'))
            else:
                chunks.append(item)

    return ''.join(chunks)


def to_rest(item, title_char='-', dedent=True, include_title=True):
    """
    Convert docstring to
    `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext>`_.

    The first block of non-blank lines up to first blank line represents test case
    title. It is joined in one line and formatted as section heading.

    Every doctest block is formatted as code block.

    Args:
        item (``object`` | `str` | `None`):
            input to be converted. If ``item`` is `str`, it will be used as input,
            otherwise ``item.__doc__`` will be used. If input is blank or
            ``None``, empty string is returned.
        title_char (``str`` | ``None``, optional):
            heading underline character for test case title; defaults to ``'-'``.
            If ``None``, title is not matched and becomes a part of the body text.
        dedent (``bool``, optional):
            `textwrap.dedent` is applied to the docstring by default; this can be
            turned off by passing ``dedent=False``.
        include_title (``bool``):
            whether to include docstring title in the output; defaults to ``True``.

    Returns:
        ``str``: reST formatted text; may be empty.

    Example:

        For ``SimpleCase`` from `~doctestcase.case.doctestcase` example,

        .. code:: pycon

            >>> from doctestcase import to_rest
            >>> to_rest(SimpleCase)

        .. code:: restructuredtext

            Title
            -----

            Paragraph.

            >>> X * 100
            'yzyz...'

            Another paragraph.

            >>> None
            >>> True
            True
    """
    doc = get_doc(item, dedent=dedent)
    title, body = parse_title_body(doc, parse_title=title_char is not None)
    if not title and not body:
        return ''

    chunks = []
    if title and include_title:
        chunks.append('{}\n{}\n'.format(title, title_char * max(3, len(title))))

    if body:
        if title and include_title:
            chunks.append('\n')
        chunks.append(body)

    return ''.join(chunks)


# helpers


class ExampleBlock(str):
    """Internal marker type to represent lines of block of examples"""


def get_doc(item, dedent):
    item = item or ''
    item = item if isinstance(item, str) else item.__doc__
    if not item:
        return ''
    if dedent:
        item = textwrap.dedent(item)
    return item.strip() + '\n'


def parse_title_body(doc, parse_title):
    if parse_title:
        match = RX_DOCSTRING.match(doc)
        if match is not None:
            title = ' '.join((t.strip() for t in match.group('title').splitlines()))
            body = match.group('body')
        else:
            title = ''
            body = doc
    else:
        title = ''
        body = doc

    if body is not None:
        body = body.strip()
        if body:  # pragma: nocover  # always true, but we don't rely on it
            body += '\n'

    return title, body


def parse_body_items(body):
    charno = 0
    for m in RX_EXAMPLE_BLOCK.finditer(body):
        yield body[charno : m.start()]
        yield ExampleBlock(body[m.start() : m.end()])
        charno = m.end()
    yield body[charno:]
