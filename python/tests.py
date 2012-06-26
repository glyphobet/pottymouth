#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import nose
import unittest
from difflib import Differ
from pottymouth import PottyMouth, Node, Token


class TestPottyMouth(object):

    def setup(self):
        self.parser = PottyMouth(
            url_check_domains=('mysite.com',),
            url_white_lists=(
                'https?://mysite\.com/allowed/service',
                'https?://mysite\.com/safe/url',
            ),
       )


    def test_repr(self):
        assert repr(self.parser.parse("foo • bar")) == "[[[TEXT{u'foo'}], [BULLET{u' \\u2022 '}], [TEXT{u'bar'}]]]"
        assert repr(self.parser.parse("foo • bar".encode('utf8'))) == "[[[TEXT{u'foo'}], [BULLET{u' \\u2022 '}], [TEXT{u'bar'}]]]"


    def _helper(self, source, expected):
        blocks = self.parser.parse(source)
        generated = b'\n'.join(map(bytes, blocks))
        if isinstance(expected, list):
            expected  = b'\n'.join(map(bytes, expected))
        if generated != expected:
            d = Differ()
            result = list(d.compare(expected.split(b'\n'), generated.split(b'\n')))
            print b'\n'.join(result)
            print source.encode('utf8')
            assert generated == expected


    def test_some_paragraphs(self):
        self._helper("""
Here is a _paragraph_ with big _fat_ looong text lines
that go *on and_ on* foreeeeeever with no end in sight.

Yes, that's right,  another paragraph. http://google.com/ is my site
Will wonders ever cease?
""",
            [Node('P',
                Node('span', 'Here is a '),
                Node('i',
                    Node('span', 'paragraph'),
                    ),
                Node('span', ' with big '),
                Node('i',
                    Node('span', 'fat'),
                    ),
                Node('span', ' looong text lines '), Node('span', 'that go '),
                Node('b',
                    Node('span', 'on and'), Node('span', '_'), Node('span', ' on'),
                    ),
                Node('span', 'foreeeeeever with no end in sight. ')
            ),
            Node('P',
                Node('span', 'Yes, that\u2019s right,  another paragraph. '),
                Node('a', 'google.com/', attributes={'href':'http://google.com/','class':'external'}),
                Node('span', ' is my site '), Node('span', 'Will wonders ever cease? '),
            )]
        )


    def test_short_lines(self):
        self._helper("""
this paragraph
has short
lines so it
should get
break tags
all over the
place
""",
            [Node('P',
                Node('span', 'this paragraph '),
                Node('br'),
                Node('span', 'has short '),
                Node('br'),
                Node('span', 'lines so it '),
                Node('br'),
                Node('span', 'should get '),
                Node('br'),
                Node('span', 'break tags '),
                Node('br'),
                Node('span', 'all over the '),
                Node('br'),
                Node('span', 'place '),
            )]
        )


    def test_mid_paragraph_list(self):
        self._helper("""This paragraph has a list embedded in the middle of itself:
item one
item two
item three
See, wasn't that easy?""",
            [Node('P',
                Node('span', 'This paragraph has a list embedded in the middle of itself: '),
                Node('br'),
                Node('span', 'item one '),
                Node('br'),
                Node('span', 'item two '),
                Node('br'),
                Node('span', 'item three '),
                Node('br'),
                Node('span', 'See, wasn\u2019t that easy?')
            )]
        )


    def test_beginning_paragraph_list(self):
        self._helper("""
item one
item two
item three
See, wasn't that easy?""",
            [Node('P',
                Node('span', 'item one '),
                Node('br'),
                Node('span', 'item two '),
                Node('br'),
                Node('span', 'item three '),
                Node('br'),
                Node('span', 'See, wasn\u2019t that easy?')
           )]
        )


    def test_end_paragraph_list(self):
        self._helper("""This paragraph has a list embedded in the middle of itself:
item one
item two
item thre
""",
            [Node('P',
                Node('span', 'This paragraph has a list embedded in the middle of itself: '),
                Node('br'),
                Node('span', 'item one '),
                Node('br'),
                Node('span', 'item two '),
                Node('br'),
                Node('span', 'item thre '),
            )]
        )


    def test_hard_text_wrapped_paragraph(self):
        self._helper("""
This paragraph is classic and typical evidence of why the process of hard text
wrapping
was ultimately a short-sighted practice that was deeply, wholly and firmly
grounded
in complete idiocy, sincerely stupid and fallacious techniques and practices
of programming.
""",
            [Node('p',
                Node('span', 'This paragraph is classic and typical evidence of why the process of hard text '),
                Node('span', 'wrapping '),
                Node('span', 'was ultimately a short-sighted practice that was deeply, wholly and firmly '),
                Node('span', 'grounded '),
                Node('span', 'in complete idiocy, sincerely stupid and fallacious techniques and practices '),
                Node('span', 'of programming. '),
            )]
        )


    def test_reply_to_a_reply(self):
        self._helper("""
This is a reply to an reply
> this is a reply
> > this is the original
> > and another original line
> > aand yet ononther ariginal
> >
> > more of the original in a different paragraph
> more of the reply
>
> even more reply
> wow this just keeps going
rest of the message

no news 
""",
            [Node('p',
                Node('span', 'This is a reply to an reply '),
            ),
            Node('blockquote',
                Node('p',
                    Node('span', 'this is a reply '),
                ),
                Node('blockquote',
                    Node('p',
                        Node('span', 'this is the original '),
                        Node('br'),
                        Node('span', 'and another original line '),
                        Node('br'),
                        Node('span', 'aand yet ononther ariginal '),
                    ),
                    Node('p',
                        Node('span', 'more of the original in a different paragraph '),
                    ),
                ),
                Node('p',
                    Node('span', 'more of the reply '),
                ),
                Node('p',
                    Node('span', 'even more reply '),
                    Node('br'),
                    Node('span', 'wow this just keeps going ')
                ),
            ),
            Node('p',
                Node('span', 'rest of the message '),
            ),
            Node('p',
                Node('span', 'no news  ')
            )]
            )


    def test_reply_reply_reply(self):
        self._helper("""You suck
> no, you suck
>> no, really, you suck
>>> I told you, you are the sucky one
> whatever you say

eat shit with your findegs
this iss also shit

eat shit some more """,
            [Node('p',
                Node('span', 'You suck '),
            ),
            Node('blockquote',
                Node('p',
                    Node('span', 'no, you suck '),
                ),
                Node('blockquote',
                    Node('p',
                        Node('span', 'no, really, you suck '),
                    ),
                    Node('blockquote',
                        Node('p',
                            Node('span', 'I told you, you are the sucky one ')
                        ),
                    ),
                ),
                Node('p',
                    Node('span', 'whatever you say '),
                ),
            ),
            Node('p',
                Node('span', 'eat shit with your findegs '),
                Node('br'),
                Node('span', 'this iss also shit '),
            ),
            Node('p',
                Node('span', 'eat shit some more ')
            )]
        )


    def test_triple_deep_quote_by_itself(self):
        self._helper(""">>> this begins a deep quote
>>> this ends a deep quote
""",
            [Node('blockquote',
                Node('blockquote',
                    Node('blockquote',
                        Node('p',
                            Node('span', 'this begins a deep quote '),
                            Node('br'),
                            Node('span', 'this ends a deep quote '),
                        ),
                    ),
                ),
            )]
        )


    def test_alternating_quote_depth(self):
        self._helper(""">>>> a very very deep quote
>> not so deep of a quote
>>> middle of the road
> deatherly quotingly
""",
            [Node('blockquote',
                Node('blockquote',
                    Node('blockquote',
                        Node('blockquote',
                            Node('p',
                                Node('span', 'a very very deep quote '),
                            ),
                        ),
                    ),
                    Node('p',
                        Node('span', 'not so deep of a quote '),
                    ),
                    Node('blockquote',
                        Node('p',
                            Node('span', 'middle of the road ')
                        )
                    ),
                ),
                Node('p',
                    Node('span', 'deatherly quotingly '),
                ),
            )]
        )


    def test_early_deep_quote(self):
        self._helper("""> early in the quote
>>>> deep in the quote
not quoted at all
""",
            [Node('blockquote',
                Node('p',
                    Node('span', 'early in the quote '),
                ),
                Node('blockquote',
                    Node('blockquote',
                        Node('blockquote',
                            Node('p',
                                Node('span', 'deep in the quote '),
                            ),
                        ),
                    )
                ),
            ),
            Node('p',
                Node('span', 'not quoted at all '),
            )]
        )


    def test_allowed_and_disallowed_urls(self):
        self._helper("""This should be a URL http://mysite.com/allowed/service but this should not be http://mysite.COM/something/dangerous. And finally, these two should also be allowed http://mysite.com/safe/url and http://another.site.com/something/else.""",
            [Node('p',
                Node('span', 'This should be a URL '),
                Node('a', 'mysite.com/allowed/service', attributes={'href':'http://mysite.com/allowed/service'}),
                Node('span', ' but this should not be '), Node('span', 'http://mysite.COM/something/dangerous'), Node('span', '. And finally, these two should also be allowed '),
                Node('a', 'mysite.com/safe/url', attributes={'href':'http://mysite.com/safe/url'}),
                Node('span', ' and '),
                Node('a', 'another.site.com/something/else', attributes={'href':'http://another.site.com/something/else', 'class':'external'}),
                Node('span', '.'),
            )]
        )


    def encoding_test(self):
        self._helper(
            'fran\u00e7aise',
            [Node('p', Node('span', 'fran\u00e7aise')),]
        )


    def test_short_then_long_line(self):
        self._helper("""short line
short line
short line
a very very long line that surpasses the maximum short line length""",
            [Node('p',
                Node('span', 'short line '),
                Node('br'),
                Node('span', 'short line '),
                Node('br'),
                Node('span', 'short line '),
                Node('br'),
                Node('span', 'a very very long line that surpasses the maximum short line length'),
            )]
        )


    def test_two_short_lines(self):
        self._helper("""two short lines
all by themselves
""",
            [Node('p',
                Node('span', 'two short lines '),
                Node('br'),
                Node('span', 'all by themselves '),
            )]
        )


    def test_bold(self):
        self._helper("""***just a bold***""",
            [Node('p',
                '**',
                Node('b',
                    Node('span', 'just a bold'),
                ),
                '**',
            )]
        )


    def test_not_bold(self):
        self._helper("""**the Higgs Boson is not bold**""",
            [Node('p',
                Node('span', '**the Higgs Boson is not bold**'),
            )]
        )


    def test_only_whitespace_line(self):
        self._helper("A paragraph separated from the next one with a line\n"
            "    \n"
            "that contains just some whitespace becomes two paragraphs\n",
            [Node('p',
                Node('span', 'A paragraph separated from the next one with a line ')
            ),
            Node('p',
                Node('span', 'that contains just some whitespace becomes two paragraphs ')
            )]
        )


    def test_only_tabspace_line(self):
        self._helper("A paragraph separated from the next one with a line\n"
            "\t\n"
            "that contains just a tab becomes two paragraphs\n",
            [Node('p',
                Node('span', 'A paragraph separated from the next one with a line ')
            ),
            Node('p',
                Node('span', 'that contains just a tab becomes two paragraphs ')
            )]
        )


    def test_email_hyperlink(self):
        self._helper("this is someone's e.mail@email.com address",
            [Node('P',
                Node('span', "this is someone\u2019s "),
                Node('a', 'e.mail@email.com', attributes={'href':'mailto:e.mail@email.com','class':'external'}),
                Node('span', ' address'),
            )]
        )


    def test_image_hyperlink(self):
        self._helper("And shit, this http://www.theory.org/~matt/matt-1.jpg is an image.",
            [Node('P',
                Node('span', "And shit, this "),
                Node('img', '', attributes={'src':'http://www.theory.org/~matt/matt-1.jpg'}),
                Node('span', " is an image."),
            )]
        )


    def test_youtube_embed_1(self):
        self._helper("http://www.youtube.com/v/PVY5IpSDUYE",
            [Node('p',
                Node('object',
                    Node('param',
                        attributes={'name':'movie', 'value':"http://www.youtube.com/v/PVY5IpSDUYE",}
                    ),
                    Node('param',
                        attributes={'name':'wmode', 'value':'transparent',}
                    ),
                    Node('embed',
                        attributes={'type':'application/x-shockwave-flash',
                            'wmode':'transparent',
                            'src':"http://www.youtube.com/v/PVY5IpSDUYE",
                            'width':'425', 'height':'350',}
                    ),
                    attributes={'width':'425', 'height':'350',}
                )
            )]
         )


    def test_youtube_embed_2(self):
        self._helper("http://www.youtube.com/watch?v=KKTDRqQtPO8",
            [Node('p',
                Node('object',
                    Node('param',
                        attributes={'name':'movie', 'value':"http://www.youtube.com/v/KKTDRqQtPO8",}
                    ),
                    Node('param',
                        attributes={'name':'wmode', 'value':'transparent',}
                    ),
                    Node('embed',
                        attributes={'type':'application/x-shockwave-flash',
                            'wmode':'transparent',
                            'src':"http://www.youtube.com/v/KKTDRqQtPO8",
                            'width':'425', 'height':'350',}
                    ),
                    attributes={'width':'425', 'height':'350',}
                ),
            )]
        )


    def test_fancy_curly_quotes(self):
        self._helper("""Oh my "Gosh," said 'Jonah' and 'Tom.' This "Shure" isn't my idea of Quotes.""",
            [Node('p',
                Node('span',
                    "Oh my \u201cGosh,\u201d said \u2018Jonah\u2019 and \u2018Tom.\u2019 This \u201cShure\u201d isn\u2019t my idea of Quotes."
                )
            )]
        )


    def test_too_clever_quotes(self):
        self._helper("""Someone's ``being'' too `clever' with quotes.""",
            [Node('p',
                Node('span',
                    "Someone\u2019s \u201cbeing\u201d too \u2018clever\u2019 with quotes."
                ),
            )]
        )


    def test_emdashes(self):
        self._helper("Whatever happened -- I wondered -- to Illimunated-Distributed Motherf----ers?",
            [Node('p',
                Node('span',
                    "Whatever happened \u2014 I wondered \u2014 to Illimunated-Distributed Motherf\u2014\u2014ers?",
                )
            )]
        )


    def test_ellipses(self):
        self._helper("what... I think... nevermind.",
            [Node('p',
                Node('span',
                    "what\u2026 I think\u2026 nevermind."
                )
            )]
        )


    def test_bold_urls(self):
        self._helper("*bold http://www.theory.org/ URL * and _italic http://www.theory.org/ URL_ and *http://www.theory.org extra stuff*",
            [Node('p',
                Node('b',
                    Node('span', "bold "),
                    Node('a', 'www.theory.org/', attributes={'href':'http://www.theory.org/', 'class':'external'}),
                    Node('span', " URL"),
                ),
                Node('span', "and "),
                Node('i',
                    Node('span', "italic "),
                    Node('a', 'www.theory.org/', attributes={'href':'http://www.theory.org/', 'class':'external'}),
                    Node('span', " URL"),
                ),
                Node('span', " and "),
                Node('b',
                    Node('a', 'www.theory.org', attributes={'href':'http://www.theory.org', 'class':'external'}),
                    Node('span', ' extra stuff'),
                ),
            )]
        )


    def test_nested_bold_and_italic(self):
        self._helper("this is *bold _and italic *and I dunno* what_ this* is.",
            [Node('p',
                Node('span', "this is "),
                Node('b',
                    Node('span', "bold "), Node('span', "_"), Node('span', "and italic ",)
                ),
                Node('span', "and I dunno"),
                Node('b',
                    Node('span', " what"), Node('span', "_"), Node('span', " this"),
                ),
                Node('span', "is."),
            )]
        )


    def test_mis_nested_bold_and_italic(self):
        self._helper("but *I dunno _what* this_ is *supposed to* be.",
            [Node('p',
                Node('span', "but "),
                Node('b',
                    Node('span', "I dunno "), Node('span', "_"), Node('span', "what")
                ),
                Node('span', "this"), Node('span', "_"), Node('span', " is "),
                Node('b',
                    Node('span', "supposed to")
                ),
                Node('span', "be.")
            )]
        )


    def test_nested_italic_and_bold(self):
        self._helper("this is _bold *and italic _and I dunno_ what* this_ is.",
            [Node('p',
                Node('span', "this is "),
                Node('i',
                    Node('span', "bold "), Node('span', "*"), Node('span', "and italic ",)
                ),
                Node('span', "and I dunno"),
                Node('i',
                    Node('span', " what"), Node('span', "*"), Node('span', "this"),
                ),
                Node('span', " is."),
            )]
        )


    def test_mis_nested_italic_and_bold(self):
        self._helper("but _I dunno *what_ this* is _supposed to_ be.",
            [Node('p',
                Node('span', "but "),
                Node('i',
                    Node('span', "I dunno "), Node('span', "*"), Node('span', "what")
                ),
                Node('span', " this"), Node('span', "*"), Node('span', "is "),
                Node('i',
                    Node('span', "supposed to")
                ),
                Node('span', " be.")
            )]
        )


    def test_attempted_HTML_insertion(self):
        self._helper('<a href="spleengrokes@email.com" target="_blank">Contact Me</a>',
            [Node('p',
                Node('span', "<a "),
                Node('a', "href=\u201cspleengrokes@email.com", attributes={'href':"mailto:href=\u201cspleengrokes@email.com", 'class':'external'}),
                Node('span', "\u201d target=\u201c"),
                Node('span', "_"),
                Node('span', "blank\u201d"),
                Node('span', ">"),
                Node('span', "Contact Me</a"),
                Node('span', ">"),
            )]
        )


    def test_unicode_email(self):
        self._helper('\u1503@theory.org',
            [Node('p',
                Node('a', "\u1503@theory.org", attributes={'href':"mailto:\u1503@theory.org", 'class':'external'}),
            )]
        )


    def test_identification_of_URLs_beginning_with_www(self):
        self._helper('go to www.google.com but not ww.goggle.com nor goggoil.com nor gar.goyle.com',
            [Node('p',
                Node('span', "go to "),
                Node('a', 'www.google.com', attributes={'href':'http://www.google.com', 'class':'external'}),
                Node('span', ' but not ww.goggle.com nor goggoil.com nor gar.goyle.com')
            )]
        )


    def test_simple_list(self):
        self._helper("""Hello this is a list:

 # item 1 is #1!
 # item 2 has some  stuff
 # item 3 is really long and it just goes on for a while, longer than fifty characters and more of item 3

And no more of the list.
     """,
            [Node('p', Node('span', "Hello this is a list: ")),
            Node('ol',
                Node('li', Node('span', "item 1 is #1! ")),
                Node('li', Node('span', "item 2 has some  stuff ")),
                Node('li', Node('span', "item 3 is really long and it just goes on for a while, longer than fifty characters and more of item 3 ")),
                ),
            Node('p', Node('span', "And no more of the list. "))
            ]
        )


    def test_numbered_list_periods(self):
        self._helper("""Hello this is a list:

 1. item #1 is #1!
 2. item #2 has some  stuff
 77. item #77 is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list.
     """,
            [Node('p', Node('span', "Hello this is a list: ")),
            Node('ol',
                Node('li', Node('span', "item #1 is #1! ")),
                Node('li', Node('span', "item #2 has some  stuff ")),
                Node('li', Node('span', "item #77 is really long and it just goes on for a while, longer than fifty characters and more of item #77 ")),
                ),
            Node('p', Node('span', "And no more of the list. "))
            ]
        )


    def test_numbered_list_parentheses(self):
        self._helper("""This is a list:
    1) One
    2) Too
    7.) Tree
    """,
            [Node('p', Node('span', "This is a list:")),
            Node('ol',
                Node('li', Node('span', "One")),
                Node('li', Node('span', "Too")),
                Node('li', Node('span', "Tree")),
            ),
            ])


    def test_list_with_long_line(self):
        self._helper("""Hello this is a list:

 * item is here
 * item has some  stuff
 * item is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list.
     """,
            [Node('p', Node('span', "Hello this is a list: ")),
            Node('ul',
                Node('li', Node('span', "item is here ")),
                Node('li', Node('span', "item has some  stuff ")),
                Node('li', Node('span', "item is really long and it just goes on for a while, longer than fifty characters and more of item #77 ")),
                ),
            Node('p', Node('span', "And no more of the list. "))
            ]
        )


    def test_bulleted_list(self):
        self._helper("""Hello this is a list:

 \u2022 item is here
 \u2022 item has some  stuff
 \u2022 item is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list.
     """,
            [Node('p', Node('span', "Hello this is a list: ")),
            Node('ul',
                Node('li', Node('span', "item is here ")),
                Node('li', Node('span', "item has some  stuff ")),
                Node('li', Node('span', "item is really long and it just goes on for a while, longer than fifty characters and more of item #77 ")),
                ),
            Node('p', Node('span', "And no more of the list. "))
            ]
        )


    def test_dashed_list(self):
        self._helper("""Hello this is a list:

 - item is here
 - item has some  stuff
 - item is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list. """,
            [Node('p', Node('span', "Hello this is a list: ")),
            Node('ul',
                Node('li', Node('span', "item is here ")),
                Node('li', Node('span', "item has some  stuff ")),
                Node('li', Node('span', "item is really long and it just goes on for a while, longer than fifty characters and more of item #77 ")),
                ),
            Node('p', Node('span', "And no more of the list. "))
            ]
       )


    def test_simple_bold(self):
        self._helper("""*this is bold*""",
            [Node('p', Node('b', Node('span', "this is bold")))]
        )


    def test_bare_leading_star(self):
        self._helper("""*this is just a leading star""",
            [Node('p', 
                Node('span', "*"),
                Node('span', "this is just a leading star")
            )]
        )


    def test_list_containing_blockquote(self):
        self._helper("""* line 1
* >> quoted item 2
* satan

paragraph not quoted paragraphy
""",
            [Node('ul',
                Node('li', Node('span', "line 1 ")),
                Node('li',
                    Node('span', ">>"),
                    Node('span', "quoted item 2 "),
                ),
                Node('li', Node('span', "satan "))
            ),
            Node('p', Node('span', "paragraph not quoted paragraphy ")),
            ]
        )


    def test_list_containing_two_quotes(self):
        self._helper("""* item
* > item quote
* > butta

paragraph damage
""",
            [Node('ul',
                Node('li', Node('span', "item ")),
                Node('li',
                    Node('span', ">"),
                    Node('span', "item quote "),
                ),
                Node('li',
                    Node('span', ">"),
                    Node('span', "butta "),
                ),
            ),
            Node('p',
                Node('span', "paragraph damage ")
            )]
        )


    def test_list_containing_blockquotes_2(self):
        self._helper("""
> * quoted item 2
> * quoted item 3
""",
            [Node('blockquote',
                Node('ul',
                    Node('li', Node('span', "quoted item 2 ")),
                    Node('li', Node('span', "quoted item 3 ")),
                )
            )]
        )


    def test_multiple_blockquotes_containing_list(self):
        self._helper("""
> Bubba

> * quoted item 2
> * quoted item 3

> Toady
""",
            [Node('blockquote',
                Node('p', Node('span', "Bubba "))
            ),
            Node('blockquote',
                Node('ul',
                        Node('li', Node('span', "quoted item 2 ")),
                        Node('li', Node('span', "quoted item 3 ")),
                ),
            ),
            Node('blockquote',
                Node('p', Node('span', "Toady "))
            )]
        )


    def test_single_blockquote_containing_list(self):
        self._helper("""
> Bubba
>
> * quoted item 2
> * quoted item 3
>
> Toady
""",
            [Node('blockquote',
                Node('p', Node('span', "Bubba ")),
                Node('ul',
                    Node('li', Node('span', "quoted item 2 ")),
                    Node('li', Node('span', "quoted item 3 ")),
                ),
                Node('p', Node('span', "Toady "))
            )]
        )


    def test_paragraph_containing_list(self):
        self._helper("""
Bubba
* quoted item 2
* quoted item 3
Toady
""",
            [Node('p', Node('span', "Bubba ")),
             Node('ul',
                 Node('li', Node('span', "quoted item 2 ")),
                 Node('li', Node('span', "quoted item 3 ")),
            ),
            Node('p', Node('span', "Toady ")),
            ]
        )


    def test_quote_containing_paragraph_containing_list(self):
        self._helper("""
> Bubba
> * quoted item 2
> * quoted item 3
> Toady
""",
            [Node('blockquote',
                Node('p', Node('span', "Bubba ")),
                Node('ul',
                    Node('li', Node('span', "quoted item 2 ")),
                    Node('li', Node('span', "quoted item 3 ")),
                ),
                Node('p', Node('span', "Toady ")),
            )]
        )


    def test_definition_list(self):
        self._helper("""
Host:     Braig Crozinsky
Location: Braig's Pad
         666 Mareclont Avenue, Apt. 6
         Loakand, CA 94616 US
         View Map
When:     Saturday, November 7, 4:30PM
Phone:    530-555-1212
""",
            [Node('dl',
                Node('dt', "Host:"),
                Node('dd', Node('span', "Braig Crozinsky")),
                Node('dt', "Location:"),
                Node('dd', 
                    Node('span', "Braig\u2019s Pad "),
                    Node('span', "666 Mareclont Avenue, Apt. 6 "),
                    Node('span', "Loakand, CA 94616 US "),
                    Node('span', "View Map"),
                ),
                Node('dt', "When:"),
                Node('dd', Node('span', "Saturday, November 7, 4:30PM")),
                Node('dt', "Phone:"),
                Node('dd', Node('span', "530-555-1212")),
            )]
        )


    def test_messy_quoted_definition_list(self):
        self._helper("""
> Host:     Braig Crozinsky
> Location: Braig's Pad
>    666 Mareclont Avenue, Apt. 6
>       Loakand, CA 94616 US
>View Map
>  When: Neptuday, Pentember 37th, 4:90PM
>Phone:    530-555-1212
""",
            [Node('blockquote',
                Node('dl',
                    Node('dt', "Host:"),
                    Node('dd', Node('span', "Braig Crozinsky")),
                    Node('dt', "Location:"),
                    Node('dd', 
                        Node('span', "Braig\u2019s Pad "),
                        Node('span', "666 Mareclont Avenue, Apt. 6 "),
                        Node('span', "Loakand, CA 94616 US"),
                    ),
                ),
                Node('p', Node('span', "View Map")),
                Node('dl',
                    Node('dt', "When:"),
                    Node('dd', Node('span', "Neptuday, Pentember 37th, 4:90PM")),
                    Node('dt', "Phone:"),
                    Node('dd', Node('span', "530-555-1212")),
                )
            )]
        )


    def test_paragraphs_and_definition_list(self):
        self._helper("""
Bubba Gump

Fishing: in the ocean, yes, and sometimes in the deep blue sea
Hurricane: in the ocean, yes, and sometimes in the deep blue sea

Toady the Wild G-Frog's wild ride of a lifetime channel tunnel
""",
            [Node('p', 
                Node('span', "Bubba Gump"),
            ),
            Node('dl', 
                Node('dt', "Fishing:"),
                Node('dd', Node('span', "in the ocean, yes, and sometimes in the deep blue sea")),
                Node('dt', "Hurricane:"),
                Node('dd', Node('span', "in the ocean, yes, and sometimes in the deep blue sea")),
            ),
            Node('p',
                Node('span', "Toady the Wild G-Frog\u2019s wild ride of a lifetime channel tunnel"),
            )]
        )


    def test_quote_containing_paragraph_and_definition_list(self):
        self._helper("""
> Bubba Gump
>
> Fishing: in the ocean, yes, and sometimes in the deep blue sea
> Hurricane: in the ocean, yes, and sometimes in the deep blue sea
>
> Toady the Wild G-Frog's ride of a lifetime channel tunnel
""",
            [Node('blockquote', 
                Node('p', Node('span', "Bubba Gump")),
                Node('dl', 
                    Node('dt', "Fishing:"),
                    Node('dd', Node('span', "in the ocean, yes, and sometimes in the deep blue sea")),
                    Node('dt', "Hurricane:"),
                    Node('dd', Node('span', "in the ocean, yes, and sometimes in the deep blue sea")),
                ),
                Node('p', Node('span', "Toady the Wild G-Frog\u2019s ride of a lifetime channel tunnel")),
            )]
        )


    def test_quote_containing_paragraph_containing_definition_list(self):
        self._helper("""
> Header header
> this: that
> these: those
> Footer footer
""",
            [Node('blockquote',
                Node('p', Node('span', "Header header ")),
                Node('dl',
                    Node('dt', 'this:'),
                    Node('dd', Node('span', "that ")),
                    Node('dt', 'these:'),
                    Node('dd', Node('span', "those ")),
                ),
                Node('p', Node('span', "Footer footer ")),
            )]
        )


    def test_not_actually_a_definiton_list(self):
        self._helper("About Smuggler's Cove: Nothing",
        [Node('p',
            Node('span', "A"),
            Node('span', "bout Smuggler\u2019s Cove: "), 
            Node('span', "Nothing"),
        )]
        )


    def test_stray_asterisk(self):
        self._helper('* ',
            [Node('p',
                Node('span', "* ")
            )]
        )


    def test_unbalanced_underscore(self):
        self._helper('This is a_lonely underscore',
            [Node('p',
                Node('span', "This is a_lonely underscore"),
            )]
        )


    def test_unbalanced_asterisk(self):
        self._helper('This is a*lonely asterisk',
            [Node('p',
                Node('span', "This is a*lonely asterisk"),
            )]
        )


    def test_indented_lists(self):
        self._helper('''
        And now a descriptive list:

1) I like to read books in the rain
2) Number one sounds silly, I guess it is. I suppose a dry area
  would be a better location.
3) I suppose you wouldn't be surprised to hear I read newspapers
  in the swimming pool.
 4) Roger

''', [
        Node('p', Node('span', "And now a descriptive list:")),
        Node('ol', 
            Node('li', Node('span', "I like to read books in the rain")),
            Node('li', Node('span', "Number one sounds silly, I guess it is. I suppose a dry area"), Node('span', " would be a better location.")),
            Node('li', Node('span', "I suppose you wouldn\u2019t be surprised to hear I read newspapers"), Node('span', " in the swimming pool.")),
            Node('li', Node('span', "Roger"))
        ),
    ])


    def test_indented_definitions(self):
        self._helper('''
Ben: a name consisting of two consonants and
  one vowel
Eva: a name consisting of one consonant and
  two vowels
Qi: Not a name at all
''', [
        Node('dl',
            Node('dt', "Ben:"),
            Node('dd', Node('span', "a name consisting of two consonants and"), Node('span', " one vowel")),
            Node('dt', "Eva:"),
            Node('dd', Node('span', "a name consisting of one consonant and"), Node('span', " two vowels")),
            Node('dt', "Qi:"),
            Node('dd', Node('span', "Not a name at all")),
        )
    ])


    def test_indented_blockquote(self):
        self._helper('''
        > thing
        > other thing
''', [Node('blockquote', Node('p', Node('span', 'thing '), Node('br'), Node('span', 'other thing')))])


    def test_indented_blockquote_followed_by_indented_paragraph(self):
        self._helper('''
        > thing
        other thing
''', [Node('blockquote', Node('p', Node('span', 'thing '))), Node('p', Node('span', 'other thing'))])


    def test_indented_blockquote_followed_by_differently_indented_paragraph(self):
        self._helper('''
        > thing
          other thing
''', [Node('blockquote', Node('p', Node('span', 'thing '))), Node('p', Node('span', 'other thing'))])

    def test_double_underline_passthrough(self):
        self._helper('__', [Node('p', '__')])

    def test_double_asterisk__passthrough(self):
        self._helper('**', [Node('p', '**')])

    def test_null_indent(self):
        self._helper('\n\t', [])

    def test_null_indent_blockquoted(self):
        self._helper('>\t', [Node('blockquote')])

    def test_empty_paragraph(self):
        self._helper('\n\t\n\n', [])

    def test_tokenizer(self):
        assert(self.parser.tokenize("A *BOLD* thing") == [Token('TEXT', 'A '), Token('STAR', '*'), Token('TEXT', 'BOLD'), Token('ITEMSTAR', '* '), Token('TEXT', 'thing'),])



if __name__ == '__main__':
    try:
        from nose.core import runmodule
    except ImportError:
        print "Usage: nosetests test"
    else:
        runmodule()
