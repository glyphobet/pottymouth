#!/usr/bin/env python
from difflib import Differ
from PottyMouth import PottyMouth, Node

contents = (
    ("""
Here is a _paragraph_ with big _fat_ long text lines
that go *on and_ on* forever with no end in sight.

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
           Node('span', ' long text lines \nthat go '),
           Node('b',
                Node('span', 'on and\n_\n on'),
                ),
           Node('span', ' forever with no end in sight. ')
           ),
      Node('P',
           Node('span', u'Yes, that\u2019s right,  another paragraph. '),
           Node('a', 'google.com/', attributes={'href':'http://google.com/','class':'external'}),
           Node('span', ' is my site \nWill wonders ever cease? '),
           )
      ]
     ),
    ("""
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
           )
      ]
     ),

    ("""This paragraph has a list embedded in the middle of itself:
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
           Node('span', u'See, wasn\u2019t that easy?')
           ),
      ]
     ),

    ("""
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
           Node('span', u'See, wasn\u2019t that easy?')
           ),
      ]
     ),
    
    ("""This paragraph has a list embedded in the middle of itself:
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
           ),
      ]
     ),

    ("""
This paragraph is classic and typical evidence of why the process of hard text
wrapping
was ultimately a short-sighted practice that was deeply, wholly and firmly
grounded
in complete idiocy, sincerely stupid and fallacious techniques and practices
of programming.
""",
     [Node('p',
           Node('span',
                'This paragraph is classic and typical evidence of why the process of hard text \n'
                'wrapping \n'
                'was ultimately a short-sighted practice that was deeply, wholly and firmly \n'
                'grounded \n'
                'in complete idiocy, sincerely stupid and fallacious techniques and practices \n'
                'of programming. '
                ),
           )
      ]
     ),

    ("""
This is a reply to an reply
> this is a reply
> > this is the original
> > and another original line
> > aand yet ononther ariginal
> >
> > more of the original in a different block quote
> more of the reply
>
> even more reply
> wow this just keeps going
rest of the message

no news 
""",
     [ Node('p',
            Node('span', 'This is a reply to an reply '),
            Node('blockquote',
                 Node('p',
                      Node('span', 'this is a reply '),
                      Node('blockquote',
                           Node('p',
                                Node('span', 'this is the original '),
                                Node('br'),
                                Node('span', 'and another original line '),
                                Node('br'),
                                Node('span', 'aand yet ononther ariginal '),
                                )
                           ),
                      Node('blockquote',
                           Node('p',
                                Node('span', 'more of the original in a different block quote '),
                                ),
                           ),
                      Node('span', 'more of the reply '),
                      )
                 ),
            Node('blockquote',
                 Node('p',
                      Node('span', 'even more reply '),
                      Node('br'),
                      Node('span', 'wow this just keeps going ')
                      ),
                 ),
            Node('span', 'rest of the message '),
            ),
       Node('p',
            Node('span', 'no news  ')
            )
       ]
     ),

    ("""You suck
> no, you suck
>> no, really, you suck
>>> I told you, you are the sucky one
> whatever you say

eat shit with your findegs
this iss also shit

eat shit some more """,
     [Node('p',
           Node('span', 'You suck '),
           Node('blockquote',
                Node('p',
                     Node('span', 'no, you suck '),
                     Node('blockquote',
                          Node('p',
                               Node('span', 'no, really, you suck '),
                               Node('blockquote',
                                    Node('p',
                                         Node('span', 'I told you, you are the sucky one ')
                                         ),
                                    ),
                               ),
                          ),
                     Node('span', 'whatever you say '),
                     )
                ),
           ),
      Node('p',
           Node('span', 'eat shit with your findegs '),
           Node('br'),
           Node('span', 'this iss also shit '),
           ),
      Node('p',
           Node('span', 'eat shit some more ')
           ),
      ]
     ),

    (""">>> this begins a deep quote
>>> this ends a deep quote
""",
     [Node('p',
           Node('blockquote',
                Node('p',
                     Node('blockquote',
                          Node('p',
                               Node('blockquote',
                                    Node('p',
                                         Node('span', 'this begins a deep quote '),
                                         Node('br'),
                                         Node('span', 'this ends a deep quote '),
                                         ),
                                    ),
                               ),
                          ),
                     ),
                ),
           ),
                
    ]

     ),
    (""">>>> a very very deep quote
>> not so deep of a quote
>>> middle of the road
> deatherly quotingly
""",
     [Node('p',
           Node('blockquote',
                Node('p',
                     Node('blockquote',
                          Node('p',
                               Node('blockquote',
                                    Node('p',
                                         Node('blockquote',
                                              Node('p',
                                                   Node('span', 'a very very deep quote '),
                                                   ),
                                              ),
                                         ),
                                    ),
                               Node('span', 'not so deep of a quote '),
                               Node('blockquote',
                                    Node('p',
                                         Node('span', 'middle of the road ')
                                         )
                                    ),
                               ),
                          ),
                     Node('span', 'deatherly quotingly '),
                     ),
                ),
           ),
      ]
     ),

    ( """> early in the quote
>>>> deep in the quote
not quoted at all
""",
      [ Node('p',
             Node('blockquote',
                  Node('p',
                       Node('span', 'early in the quote '),
                  
                       Node('blockquote',
                            Node('p',
                                 Node('blockquote',
                                      Node('p',
                                           Node('blockquote',
                                                Node('p',
                                                     Node('span', 'deep in the quote '),
                                                     ),
                                                ),
                                           ),
                                      ),
                                 ),
                            ),
                       ),
                  ),
             Node('span', 'not quoted at all '),
             )
        ]
      ),

    ("""This should be a URL http://mysite.com/allowed/service but this should not be http://mysite.COM/something/dangerous. And finally, these two should also be allowed http://mysite.com/safe/url and http://another.site.com/something/else."""
    ,
     [Node('p',
           Node('span', 'This should be a URL '),
           Node('a', 'mysite.com/allowed/service', attributes={'href':'http://mysite.com/allowed/service'}),
           Node('span', ' but this should not be \nhttp://mysite.COM/something/dangerous\n. And finally, these two should also be allowed '),
           Node('a', 'mysite.com/safe/url', attributes={'href':'http://mysite.com/safe/url'}),
           Node('span', ' and '),
           Node('a', 'another.site.com/something/else', attributes={'href':'http://another.site.com/something/else', 'class':'external'}),
           Node('span', '.'),
           )
      ]
     ),
    ('fran\xc3\xa7aise'.decode('utf8'),
     [Node('p',
           Node('span', u'fran\u00e7aise')
           ),
      ]
     ),
    ("""short line
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
           )
      ]
     ),
    ("""two short lines
all by themselves
""",
     [Node('p',
           Node('span', 'two short lines '),
           Node('br'),
           Node('span', 'all by themselves '),
           )
      ]
     ),
    ("""***just a bold***""",
     [Node('p',
           Node('b',
                Node('span', 'just a bold'),
                ),
           ),
      ]
    ),
    ("""**the Higgs Boson is not bold**""",
     [Node('p',
           Node('span', 'the Higgs Boson is not bold'),
           ),
      ]
    ),
    ("A paragraph separated from the next one with a line\n"
     "    \n"
     "that contains just some whitespace becomes two paragraphs\n",
     [Node('p',
           Node('span', 'A paragraph separated from the next one with a line ')
           ),
      Node('p',
           Node('span', 'that contains just some whitespace becomes two paragraphs ')
           ),
      ]
     ),
    ("A paragraph separated from the next one with a line\n"
     "\t\n"
     "that contains just a tab becomes two paragraphs\n",
     [Node('p',
           Node('span', 'A paragraph separated from the next one with a line ')
           ),
      Node('p',
           Node('span', 'that contains just a tab becomes two paragraphs ')
           ),
      ]
     ),
    ("this is someone's e.mail@email.com address",
     [Node('P',
           Node('span', u"this is someone\u2019s "),
           Node('a', 'e.mail@email.com', attributes={'href':'mailto:e.mail@email.com','class':'external'}),
           Node('span', ' address'),
           ),
      ],
     ),
    ("And shit, this http://www.theory.org/~matt/matt-1.jpg is an image.",
     [Node('P',
           Node('span', "And shit, this "),
           Node('img', '', attributes={'src':'http://www.theory.org/~matt/matt-1.jpg'}),
           Node('span', " is an image."),
           )
      ]
    ),
    ("http://www.youtube.com/v/PVY5IpSDUYE",
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
                attributes={'width':'425', 'height':'350',})
           )
      ]
     ),
    ("http://www.youtube.com/watch?v=KKTDRqQtPO8",
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
                attributes={'width':'425', 'height':'350',}),
           )
      ]
     ),
    ("""Oh my "Gosh," said 'Jonah' and 'Tom.' This "Shure" isn't my idea of Quotes.""",
     [Node('p',
           Node('span',
                u"Oh my \u201cGosh,\u201d said \u2018Jonah\u2019 and \u2018Tom.\u2019 This \u201cShure\u201d isn\u2019t my idea of Quotes."
                )
           )
      ]
     ),
     ("""Someone's ``being'' too `clever' with quotes.""",
      [Node('p',
            Node('span',
                 u"Someone\u2019s \u201cbeing\u201d too \u2018clever\u2019 with quotes."
                ),
            ),
       ]
      ),
     ("Whatever happened -- I wondered -- to Illimunated-Distributed Motherf----ers?",
      [Node('p',
            Node('span',
                 u"Whatever happened \u2014 I wondered \u2014 to Illimunated-Distributed Motherf\u2014\u2014ers?",
                 )
            )
       ]
      ),
     ("what... I think... nevermind.",
      [Node('p',
            Node('span',
                 u"what\u2026 I think\u2026 nevermind."
                 )
            )
       ]
      ),
     ("*bold http://www.theory.org/ URL * and _italic http://www.theory.org/ URL_ and *http://www.theory.org extra stuff*",
      [Node('p',
            Node('b',
                 Node('span', "bold "),
                 Node('a', 'www.theory.org/', attributes={'href':'http://www.theory.org/', 'class':'external'}),
                 Node('span', " URL"),
                 ),
            Node('span', " and "),
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
            ),
       ]
      ),
     ("this is *bold _and italic *and I dunno* what_ this* is.",
      [Node('p',
            Node('span',
                 "this is "),
            Node('b',
                 Node('span', "bold ", "_", "and italic ",)
                 ),
            Node('span', "and I dunno"),
            Node('b',
                 Node('span', " what", "_", " this"),
                 ),
            Node('span', " is."),
            )
       ]
      ),
     ("but *I dunno _what* this_ is *supposed to* be.",
      [Node('p',
            Node('span', "but "),
            Node('b',
                 Node('span', "I dunno ", "_", "what")
                 ),
            Node('span', " this", "_", " is "),
            Node('b',
                 Node('span', "supposed to")
                 ),
            Node('span', " be.")
            )
       ]
      ),
     # Test attempted HTML insertion
     ('<a href="spleengrokes@email.com" target="_blank">Contact Me</a>',
      [Node('p',
            Node('span', "<a "),
            Node('a', u"href=\u201cspleengrokes@email.com", attributes={'href':u"mailto:href=\u201cspleengrokes@email.com", 'class':'external'}),
            Node('span', u"\u201d target=\u201c", "_", u"blank\u201d", ">", "Contact Me</a", ">")
            )
       ]
      ),
    (u'\u1503@theory.org',
     [Node('p',
           Node('a', u"\u1503@theory.org", attributes={'href':u"mailto:\u1503@theory.org", 'class':'external'}),
           )
      ]
     ),
     # Test identification of URLs that begin with www.
     ('go to www.google.com but not ww.goggle.com nor goggoil.com nor gar.goyle.com',
      [Node('p',
            Node('span', "go to "),
            Node('a', 'www.google.com', attributes={'href':'http://www.google.com', 'class':'external'}),
            Node('span', ' but not ww.goggle.com nor goggoil.com nor gar.goyle.com')
            )
       ]
      ),
     ("""Hello this is a list:

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
       Node('p', Node('span', "And no more of the list. "))],
      ),
     ("""Hello this is a list:

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
       Node('p', Node('span', "And no more of the list. "))],
      ),
     ("""Hello this is a list:

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
       Node('p', Node('span', "And no more of the list. "))],
      ),
     (u"""Hello this is a list:

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
       Node('p', Node('span', "And no more of the list. "))],
       ),
       ("""Hello this is a list:

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
       Node('p', Node('span', "And no more of the list. "))],
       ),
       ("""*this is bold*""",
        [Node('p', Node('b', Node('span', "this is bold")))]
        ),
       ("""*this is just a leading star""",
        [Node('p', Node('span', "*", "this is just a leading star"))]
        ),
       ("""* line 1
* >> quoted item 2
* satan

paragraph not quoted paragraphy
""",
        [Node('ul',
              Node('li', Node('span', "line 1 ")),
              Node('li',
                   Node('blockquote',
                        Node('p',
                             Node('blockquote',
                                  Node('p',
                                       Node('span', "quoted item 2 ")
                                       )
                                  )
                             )
                        )
                   ),
              Node('li', Node('span', "satan "))
              ),
         Node('p', Node('span', "paragraph not quoted paragraphy ")),
              ]
        ),
    ("""* item
* > item quote
* > butta

paragraph damage
""",
     [Node('ul',
           Node('li', Node('span', "item ")),
           Node('li',
                Node('blockquote',
                     Node('p', Node('span', "item quote "))
                     )
                ),
           Node('li',
                Node('blockquote',
                     Node('p', Node('span', "butta "))
                     )
                ),
           ),
      Node('p',
           Node('span', "paragraph damage ")
           )
           ]),
    
    ("""
> * quoted item 2
> * quoted item 3
""",
        [Node('p',
              Node('blockquote',
                   Node('ul',
                        Node('li', Node('span', "quoted item 2 ")),
                        Node('li', Node('span', "quoted item 3 ")),
                        ),
                   )
              )]
        ),

    ("""
> Bubba

> * quoted item 2
> * quoted item 3

> Toady
""",
        [Node('p',
              Node('blockquote',
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
                   ),
              ),
         ]
        ),


    ("""
> Bubba
>
> * quoted item 2
> * quoted item 3
>
> Toady
""",
        [Node('p',
              Node('blockquote',
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
                   ),
              ),
         ]
        ),
    ("""
Bubba
* quoted item 2
* quoted item 3
Toady
""",
        [Node('p', Node('span', "Bubba ")),
         Node('ul',
              Node('li', Node('span', "quoted item 2 ")),
              Node('li',
                   Node('span', "quoted item 3 "),
                   Node('br'),
                   Node('span', "Toady "),
                   ),
              ),
         ]
        ),
    ("""
> Bubba
> * quoted item 2
> * quoted item 3
> Toady
""",
        [Node('p',
              Node('blockquote',
                   Node('p', Node('span', "Bubba ")),
                   Node('ul',
                        Node('li', Node('span', "quoted item 2 ")),
                        Node('li',
                             Node('span', "quoted item 3 "),
                             Node('br'),
                             Node('span', "Toady "),
                             ),
                        ),
                   ),
              ),
         ]
        ),

    )


w = PottyMouth(url_check_domains=('mysite.com',),
               url_white_lists=('https?://mysite\.com/allowed/service',
                                'https?://mysite\.com/safe/url',),
               )
failures = 0

##import hotshot, hotshot.stats
##prof = hotshot.Profile('/tmp/hotshot_pottymouth')

for i, (source, output) in enumerate(contents):#[-2:]:
    try:
        #prof.start()
        blocks = w.parse(source)
        #prof.stop()
        generated = '\n'.join(map(str, blocks))
        expected = '\n'.join(map(str, output))
        if generated != expected:
            failures += 1
            d = Differ()
            result = list(d.compare(expected.split('\n'), generated.split('\n')))
            print '\n'.join(result)
            print '=' * 70
    except:
        print "Error in test %d" % i
        print source
        raise

if failures:
    print failures, 'failures'

##prof.close()
##pstats = hotshot.stats.load('/tmp/hotshot_pottymouth')
##pstats.strip_dirs()
##pstats.sort_stats('time', 'cumulative', 'calls')
##pstats.print_stats()
