.. |package-name| replace:: regexplain

.. |pypi-version| image:: https://img.shields.io/pypi/v/regexplain?label=PyPI%20Version&color=4BC51D
   :alt: PyPI Version
   :target: https://pypi.org/projects/regexplain/

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/regexplain?label=PyPI%20Downloads&color=037585
   :alt: PyPI Downloads
   :target: https://pypi.org/projects/regexplain/

regexplain
##########

|pypi-version| |pypi-downloads|

Description
***********

`regexplainer` consists of two main components:
 - Explainer (technically ``RegexTokenizer``): It tokenizes a given input regex string pattern, and its ``explain()`` method then explains in simpler English what is going on. The output is customizable, i.e. whether you want to see the flags, where a particular token starts and its length, to see the full textual sub-token along with its break-down, etc. In your IDE, check the init parameters to the class. This is working pretty well and you can use it without many issues.
 - Builder (technically ``RegexBuilder``): This is a class that you can instantiate, and start using its properties and methods to build a regex without having to remember the actual Regex syntax. Your Python IDE will prompt you once you type in a letter that is close to what you want to do. Unfortunately, this is very rough around the edges and needs quite a bit of work. Am working on it.

Note: This is an alpha version, and things may change quite a bit.

.. code-block:: python

   from regexplain import RegexTokenizer


   regtokens = RegexTokenizer(r"[^\w\s-]")
   regtokens.explain()

   """
   Explaining Full Pattern: [^\w\s-]
   ┌──
   │   [Span, Length] (0, 8), 8
   │   [Flags] re.NOFLAG
   │  ┌──
   │──│ [^
   │  │   [@0:Character Set] Matches any character not in the set
   │  │   [Span, Length] (0, 8), 8
   │  │   [Flags] re.NOFLAG
   │  │  ┌──
   │  │──│ \w
   │  │  │   [@1:Character Class:Word] Matches any word character (alphanumeric and underscore)
   │  │  │   [Span, Length] (2, 4), 2
   │  │  │   [Flags] re.NOFLAG
   │  │  └──
   │  │  ┌──
   │  │──│ \s
   │  │  │   [@2:Character Class:Whitespace] Matches any whitespace character (space, tab, line-break)
   │  │  │   [Span, Length] (4, 6), 2
   │  │  │   [Flags] re.NOFLAG
   │  │  └──
   │  │  ┌──
   │  │──│ -
   │  │  │   [@3:Literal] Matches a single character from the list '-' (case-sensitive)
   │  │  │   [Span, Length] (6, 7), 1
   │  │  │   [Flags] re.NOFLAG
   │  │  └──
   │  │ ]
   │  │   [@0:End] Token closed
   │  └──
   └──
   """