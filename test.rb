#!/usr/bin/env ruby1.9
require 'PottyMouth'

contents = [
  ["""
Here is a _paragraph_ with big _fat_ long text lines
that go *on and_ on* forever with no end in sight.

Yes, that's right,  another paragraph. http://google.com/ is my site
Will wonders ever cease?
""",
   [PottyMouth::Node.new(:P, [
	      PottyMouth::Node.new(:span, ['Here is a ']),
	      PottyMouth::Node.new(:i, [PottyMouth::Node.new(:span, ['paragraph'])]),
	      PottyMouth::Node.new(:span, [' with big ']),
	      PottyMouth::Node.new(:i, [
			 PottyMouth::Node.new(:span, ['fat']),
			]),
	      PottyMouth::Node.new(:span, [" long text lines \nthat go "]),
	      PottyMouth::Node.new(:b, [
			 PottyMouth::Node.new(:span, ["on and\n_\n on"]),
			]),
	      PottyMouth::Node.new(:span, [' forever with no end in sight. '])
	       ]),
     PottyMouth::Node.new(:P, [
		PottyMouth::Node.new(:span, ['Yes, that&#8217;s right,  another paragraph. ']),
		PottyMouth::LinkNode.new('http://google.com/'),
		PottyMouth::Node.new(:span, [" is my site \nWill wonders ever cease? "]),
	       ]),
    ]
  ],
  ["""
this paragraph
has short
lines so it
should get
break tags
all over the
place
""",
    [PottyMouth::Node.new(:P, [
     PottyMouth::Node.new(:span, ['this paragraph ']),
     PottyMouth::Node.new(:br),
     PottyMouth::Node.new(:span, ['has short ']),
     PottyMouth::Node.new(:br),
     PottyMouth::Node.new(:span, ['lines so it ']),
     PottyMouth::Node.new(:br),
     PottyMouth::Node.new(:span, ['should get ']),
     PottyMouth::Node.new(:br),
     PottyMouth::Node.new(:span, ['break tags ']),
     PottyMouth::Node.new(:br),
     PottyMouth::Node.new(:span, ['all over the ']),
     PottyMouth::Node.new(:br),
     PottyMouth::Node.new(:span, ['place ']),
			  ])
    ]
  ],

  ["""This paragraph has a list embedded in the middle of itself:
item one
item two
item three
See, wasn't that easy?""",
   [PottyMouth::Node.new(:P, [
      PottyMouth::Node.new(:span, ['This paragraph has a list embedded in the middle of itself: ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item one ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item two ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item three ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['See, wasn&#8217;t that easy?']),
       ]),
    ]
   ],

  ["""
item one
item two
item three
See, wasn't that easy?""",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['item one ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item two ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item three ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['See, wasn&#8217;t that easy?'])
	     ]),
    ]
   ],
  
  ["""This paragraph has a list embedded in the middle of itself:
item one
item two
item thre
""",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['This paragraph has a list embedded in the middle of itself: ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item one ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item two ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['item thre ']),
	     ]),
    ]
   ],

  ["""
This paragraph is classic and typical evidence of why the process of hard text
wrapping
was ultimately a short-sighted practice that was deeply, wholly and firmly
grounded
in complete idiocy, sincerely stupid and fallacious techniques and practices
of programming.
""",
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, [
			   "This paragraph is classic and typical evidence of why the process of hard text \n" + 
			   "wrapping \n" + 
			   "was ultimately a short-sighted practice that was deeply, wholly and firmly \n" + 
			   "grounded \n" + 
			   "in complete idiocy, sincerely stupid and fallacious techniques and practices \n" + 
			   "of programming. "
			 ])
	      ])
    ],
  ],
  ["""
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
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['This is a reply to an reply ']),
		PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [
				     PottyMouth::Node.new(:span, ['this is a reply ']),
				     PottyMouth::Node.new(:blockquote, [
						PottyMouth::Node.new(:p, [
							   PottyMouth::Node.new(:span, ['this is the original ']),
							   PottyMouth::Node.new(:br),
							   PottyMouth::Node.new(:span, ['and another original line ']),
							   PottyMouth::Node.new(:br),
							   PottyMouth::Node.new(:span, ['aand yet ononther ariginal ']),
							  ])
					       ]),
				     PottyMouth::Node.new(:blockquote, [
						PottyMouth::Node.new(:p, [
							   PottyMouth::Node.new(:span, ['more of the original in a different block quote ']),
							  ]),
					       ]),
				     PottyMouth::Node.new(:span, ['more of the reply ']),
				    ])
			 ]),
		PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [
				     PottyMouth::Node.new(:span, ['even more reply ']),
				     PottyMouth::Node.new(:br),
				     PottyMouth::Node.new(:span, ['wow this just keeps going '])
				    ]),
			 ]),
		PottyMouth::Node.new(:span, ['rest of the message ']),
	      ]),
     PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['no news  '])
	       ])
    ]
   ],

  ["""You suck
> no, you suck
>> no, really, you suck
>>> I told you, you are the sucky one
> whatever you say

eat shit with your findegs
this iss also shit

eat shit some more """,
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['You suck ']),
		PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [
				     PottyMouth::Node.new(:span, ['no, you suck ']),
				     PottyMouth::Node.new(:blockquote, [
						PottyMouth::Node.new(:p, [
							   PottyMouth::Node.new(:span, ['no, really, you suck ']),
							   PottyMouth::Node.new(:blockquote, [
								      PottyMouth::Node.new(:p, [
										 PottyMouth::Node.new(:span, ['I told you, you are the sucky one '])
										]),
								     ]),
							  ]),
						 ]),
				     PottyMouth::Node.new(:span, ['whatever you say ']),
				    ])
			 ]),
	      ]),
     PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['eat shit with your findegs ']),
		PottyMouth::Node.new(:br),
		PottyMouth::Node.new(:span, ['this iss also shit ']),
	       ]),
     PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['eat shit some more '])
		 ]),
    ]
   ],

  [""">>> this begins a deep quote
>>> this ends a deep quote
""",
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [
				     PottyMouth::Node.new(:blockquote, [
						PottyMouth::Node.new(:p, [
							   PottyMouth::Node.new(:blockquote, [
								      PottyMouth::Node.new(:p, [
										 PottyMouth::Node.new(:span, ['this begins a deep quote ']),
										 PottyMouth::Node.new(:br),
										 PottyMouth::Node.new(:span, ['this ends a deep quote ']),
										  ]),
								       ]),
							  ]),
					       ]),
				    ]),
			 ]),
	      ]),
    ]
   ],
  [""">>>> a very very deep quote
>> not so deep of a quote
>>> middle of the road
> deatherly quotingly
""",
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [
				     PottyMouth::Node.new(:blockquote, [
						PottyMouth::Node.new(:p, [
							   PottyMouth::Node.new(:blockquote, [
								      PottyMouth::Node.new(:p, [
										 PottyMouth::Node.new(:blockquote, [
											    PottyMouth::Node.new(:p, [
													PottyMouth::Node.new(:span, ['a very very deep quote ']),
													]),
											     ]),
										  ]),
								     ]),
							   PottyMouth::Node.new(:span, ['not so deep of a quote ']),
							   PottyMouth::Node.new(:blockquote, [
								      PottyMouth::Node.new(:p, [
										 PottyMouth::Node.new(:span, ['middle of the road '])
										  ])
								     ]),
							  ]),
					       ]),
				     PottyMouth::Node.new(:span, ['deatherly quotingly ']),
				    ]),
			 ]),
	      ]),
    ]
   ],

  ["""> early in the quote
>>>> deep in the quote
not quoted at all
""",
   [PottyMouth::Node.new(:p, [
	      PottyMouth::Node.new(:blockquote, [
			 PottyMouth::Node.new(:p, [
				    PottyMouth::Node.new(:span, ['early in the quote ']),
				    PottyMouth::Node.new(:blockquote, [
						PottyMouth::Node.new(:p, [
							  PottyMouth::Node.new(:blockquote, [
								     PottyMouth::Node.new(:p, [
										PottyMouth::Node.new(:blockquote, [
											   PottyMouth::Node.new(:p, [
												      PottyMouth::Node.new(:span, ['deep in the quote ']),
												     ]),
											  ]),
									       ]),
								    ]),
							 ]),
					      ]),
				   ]),
			]),
	      PottyMouth::Node.new(:span, ['not quoted at all ']),
	     ])
    ]
  ],

  ["""This should be a URL http://mysite.com/allowed/service but this should not be http://mysite.COM/something/dangerous. And finally, these two should also be allowed http://mysite.com/safe/url and http://another.site.com/something/else.""",
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['This should be a URL ']),
		PottyMouth::LinkNode.new('http://mysite.com/allowed/service', internal=true),
		PottyMouth::Node.new(:span, [" but this should not be \nhttp://mysite.COM/something/dangerous\n. And finally, these two should also be allowed "]),
		PottyMouth::LinkNode.new('http://mysite.com/safe/url', internal=true),
		PottyMouth::Node.new(:span, [' and ']),
		PottyMouth::LinkNode.new('http://another.site.com/something/else'),
		PottyMouth::Node.new(:span, ['.']),
	      ])
    ]
  ],
  ["française",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['fran&#231;aise'])
       ]),
    ]
  ],
  ["""short line
short line
short line
a very very long line that surpasses the maximum short line length""",
    [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['short line ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['short line ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['short line ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['a very very long line that surpasses the maximum short line length']),
	      ])
    ]
  ],
  ["""two short lines
all by themselves
""",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['two short lines ']),
      PottyMouth::Node.new(:br),
      PottyMouth::Node.new(:span, ['all by themselves ']),
	     ])
    ]
  ],
  ["""***just a bold***""",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:b, [
		 PottyMouth::Node.new(:span, ['just a bold']),
		]),
	     ]),
    ]
  ],
  ["""**the Higgs Boson is not bold**""",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['the Higgs Boson is not bold']),
	     ]),
    ]
  ],
  ["A paragraph separated from the next one with a line\n" +
   "  \n" +
   "that contains just some whitespace becomes two paragraphs\n", 
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['A paragraph separated from the next one with a line '])
	      ]),
     PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ['that contains just some whitespace becomes two paragraphs '])
	       ]),
    ]
  ],
  ["A paragraph separated from the next one with a line\n" +
   "\t\n" +
   "that contains just a tab becomes two paragraphs\n",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['A paragraph separated from the next one with a line '])
	     ]),
   PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ['that contains just a tab becomes two paragraphs '])
	     ]),
    ]
   ],
  ["this is someone's e.mail@email.com address",
   [PottyMouth::Node.new(:p, [
	      PottyMouth::Node.new(:span, ["this is someone&#8217;s "]),
	      PottyMouth::EmailNode.new('e.mail@email.com'),
	      PottyMouth::Node.new(:span, [' address']),
	     ]),
    ],
  ],
  ["And shit, this http://www.theory.org/~matt/matt-1.jpg is an image.",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:span, ["And shit, this "]),
      PottyMouth::ImageNode.new('http://www.theory.org/~matt/matt-1.jpg'),
      PottyMouth::Node.new(:span, [" is an image."]),
	     ])
    ]
  ],
  ["http://www.youtube.com/v/PVY5IpSDUYE",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:object, [
		 PottyMouth::Node.new(:param, [], 
			   {:name=>'movie', :value=>"http://www.youtube.com/v/PVY5IpSDUYE",}
			   ),
		 PottyMouth::Node.new(:param, [],
			   {:name=>'wmode', :value=>'transparent',}
			   ),
		 PottyMouth::Node.new(:embed, [],
			   { :type=>'application/x-shockwave-flash',
			     :wmode=>'transparent',
			     :src=>"http://www.youtube.com/v/PVY5IpSDUYE",
			     :width=>'425', :height=>'350',}
			   )
		],
		{:width=>'425', :height=>'350',})
	     ])
    ]
  ],
  ["http://www.youtube.com/watch?v=KKTDRqQtPO8",
   [PottyMouth::Node.new(:p, [
      PottyMouth::Node.new(:object, [
		 PottyMouth::Node.new(:param, [], 
			   {:name=>'movie', :value=>"http://www.youtube.com/v/KKTDRqQtPO8",}
			   ),
		 PottyMouth::Node.new(:param, [],
			   {:name=>'wmode', :value=>'transparent',}
			   ),
		 PottyMouth::Node.new(:embed, [],
			   { :type=>'application/x-shockwave-flash',
			     :wmode=>'transparent',
			     :src=>"http://www.youtube.com/v/KKTDRqQtPO8",
			     :width=>'425', :height=>'350',}
			   )
		],
		{:width=>'425', :height=>'350',})
	     ])
    ]
   ],
  ["""Oh my \"Gosh,\" said 'Jonah' and 'Tom.' This \"Shure\" isn't my idea of Quotes.""", 
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span,
			 ["Oh my &#8220;Gosh,&#8221; said &#8216;Jonah&#8217; and &#8216;Tom.&#8217; This &#8220;Shure&#8221; isn&#8217;t my idea of Quotes."]
        )
	      ])
    ]
  ],
  ["Someone's ``being'' too `clever' with quotes.",
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span,
			 ["Someone&#8217;s &#8220;being&#8221; too &#8216;clever&#8217; with quotes."]
			 ),
	      ]),
    ]
  ],
  ["Whatever happened -- I wondered -- to Illimunated-Distributed Motherf----ers?",
    [PottyMouth::Node.new(:p, [
     PottyMouth::Node.new(:span,
         ["Whatever happened &#8212; I wondered &#8212; to Illimunated-Distributed Motherf&#8212;&#8212;ers?"]
	       )
	      ])
    ]
  ],
  ["what... I think... nevermind.",
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span,
			 ["what&#8230; I think&#8230; nevermind."]
			 )
	      ])
     ]
  ],
  ["*bold http://www.theory.org/ URL * and _italic http://www.theory.org/ URL_ and *http://www.theory.org extra stuff*",
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:b, [
			  PottyMouth::Node.new(:span, ["bold "]),
			  PottyMouth::LinkNode.new('http://www.theory.org/'),
			  PottyMouth::Node.new(:span, [" URL"]),
			 ]),
		PottyMouth::Node.new(:span, [" and "]),
		PottyMouth::Node.new(:i, [
			  PottyMouth::Node.new(:span, ["italic "]),
			  PottyMouth::LinkNode.new('http://www.theory.org/'),
			  PottyMouth::Node.new(:span, [" URL"]),
			 ]),
		PottyMouth::Node.new(:span, [" and "]),
		PottyMouth::Node.new(:b, [
			  PottyMouth::LinkNode.new('http://www.theory.org'),
			  PottyMouth::Node.new(:span, [' extra stuff']),
			 ]),
	      ]),
    ]
  ],
  ["this is *bold _and italic *and I dunno* what_ this* is.",
    [PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ["this is "]),
		PottyMouth::Node.new(:b, [
			  PottyMouth::Node.new(:span, ["bold ", "_", "and italic "])
			 ]),
		PottyMouth::Node.new(:span, ["and I dunno"]),
		PottyMouth::Node.new(:b, [
			  PottyMouth::Node.new(:span, [" what", "_", " this"]),
			 ]),
		PottyMouth::Node.new(:span, [" is."]),
	      ])
     ]
  ],
  ["but *I dunno _what* this_ is *supposed to* be.",
    [PottyMouth::Node.new(:p, [
	        PottyMouth::Node.new(:span, ["but "]),
	        PottyMouth::Node.new(:b, [
			PottyMouth::Node.new(:span, ["I dunno ", "_", "what"])
			 ]),
	        PottyMouth::Node.new(:span, [" this", "_", " is "]),
	        PottyMouth::Node.new(:b, [
			  PottyMouth::Node.new(:span, ["supposed to"])
			 ]),
	        PottyMouth::Node.new(:span, [" be."])
	      ])
     ]
  ],
  # Test attempted HTML insertion
  ['<a href="spleengrokes@email.com" target="_blank">Contact Me</a>',
    [PottyMouth::Node.new(:p, [
	        PottyMouth::Node.new(:span, ["&lt;a "]),
		PottyMouth::EmailNode.new("href=“spleengrokes@email.com"), ###
	        PottyMouth::Node.new(:span, ["&#8221; target=&#8220;", "_", "blank&#8221;", "&gt;", "Contact Me&lt;/a", "&gt;"])
	      ])
     ]
  ],
  # Test identification of URLs that begin with www.
  ['go to www.google.com but not ww.goggle.com nor goggoil.com nor gar.goyle.com',
    [PottyMouth::Node.new(:p, [
	        PottyMouth::Node.new(:span, ["go to "]),
		PottyMouth::LinkNode.new('http://www.google.com'),
	        PottyMouth::Node.new(:span, [' but not ww.goggle.com nor goggoil.com nor gar.goyle.com'])
	      ])
    ]
  ],
  ["""Hello this is a list:

 # item 1 is #1!
 # item 2 has some  stuff
 # item 3 is really long and it just goes on for a while, longer than fifty characters and more of item 3

And no more of the list.
   """,
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Hello this is a list: "])]),
     PottyMouth::Node.new(:ol, [
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item 1 is #1! "])]),
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item 2 has some  stuff "])]),
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item 3 is really long and it just goes on for a while, longer than fifty characters and more of item 3 "])]),
	       ]),
     PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["And no more of the list. "])])],
  ],
  ["""Hello this is a list:

 1. item #1 is #1!
 2. item #2 has some  stuff
 77. item #77 is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list.
   """,
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Hello this is a list: "])]),
    PottyMouth::Node.new(:ol, [
	        PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item #1 is #1! "])]),
	        PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item #2 has some  stuff "])]),
	        PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item #77 is really long and it just goes on for a while, longer than fifty characters and more of item #77 "])]),
	      ]),
    PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["And no more of the list. "])])
    ],
  ],
  ["""Hello this is a list:

 * item is here
 * item has some  stuff
 * item is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list.
   """,
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Hello this is a list: "])]),
    PottyMouth::Node.new(:ul, [
     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item is here "])]),
     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item has some  stuff "])]),
     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item is really long and it just goes on for a while, longer than fifty characters and more of item #77 "])]),
	      ]),
     PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["And no more of the list. "])])
    ],
  ],
  ["""Hello this is a list:

 • item is here
 • item has some  stuff
 • item is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list.
   """,
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Hello this is a list: "])]),
     PottyMouth::Node.new(:ul, [
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item is here "])]),
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item has some  stuff "])]),
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item is really long and it just goes on for a while, longer than fifty characters and more of item #77 "])]),
	       ]),
     PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["And no more of the list. "])])
    ],
  ],
  ["""Hello this is a list:

 - item is here
 - item has some  stuff
 - item is really long and it just goes on for a while, longer than fifty characters and more of item #77

And no more of the list. """,
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Hello this is a list: "])]),
     PottyMouth::Node.new(:ul, [
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item is here "])]),
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item has some  stuff "])]),
		PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item is really long and it just goes on for a while, longer than fifty characters and more of item #77 "])]),
      ]),
     PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["And no more of the list. "])])
    ],
  ],
  ["*this is bold*",
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:b, [PottyMouth::Node.new(:span, ["this is bold"])])])]
  ],
  ["*this is just a leading star",
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["*", "this is just a leading star"])])]
  ],
  [%(* line 1
* >> quoted item 2
* satan

paragraph not quoted paragraphy
),
    [PottyMouth::Node.new(:ul, [
	        PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["line 1 "])]),
	        PottyMouth::Node.new(:li, [
			  PottyMouth::Node.new(:blockquote, [
				     PottyMouth::Node.new(:p, [
						PottyMouth::Node.new(:blockquote, [
							   PottyMouth::Node.new(:p, [
								      PottyMouth::Node.new(:span, ["quoted item 2 "])
								     ])
							  ])
					       ])
				    ])
			 ]),
	        PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["satan "])])
	      ]),
     PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["paragraph not quoted paragraphy "])]),
    ]
  ],
  [%(* item
* > item quote
* > butta

paragraph damage
),
    [PottyMouth::Node.new(:ul, [
	        PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["item "])]),
	        PottyMouth::Node.new(:li, [
			  PottyMouth::Node.new(:blockquote, [
				     PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["item quote "])])
				    ])
			 ]),
	        PottyMouth::Node.new(:li, [
			  PottyMouth::Node.new(:blockquote, [
				     PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["butta "])])
				    ])
			 ]),
	      ]),
     PottyMouth::Node.new(:p, [
		PottyMouth::Node.new(:span, ["paragraph damage "])
	       ])
    ]
  ],
  
  [%(
> * quoted item 2
> * quoted item 3
),
    [PottyMouth::Node.new(:p, [
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:ul, [
				     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 2 "])]),
				     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 3 "])]),
				    ]),
			 ])
	      ])
    ]
  ],

  [%(
> Bubba

> * quoted item 2
> * quoted item 3

> Toady
),
    [PottyMouth::Node.new(:p, [
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Bubba "])])
			 ]),
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:ul, [
				     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 2 "])]),
				     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 3 "])]),
				    ]),
			 ]),
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Toady "])])
			 ]),
	      ]),
     ]
  ],
  [%(
> Bubba
>
> * quoted item 2
> * quoted item 3
>
> Toady
),
    [PottyMouth::Node.new(:p, [
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Bubba "])])
			 ]),
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:ul, [
				     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 2 "])]),
				     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 3 "])]),
				    ]),
			 ]),
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Toady "])])
			 ]),
	      ]),
     ]
  ],
  [%(
Bubba
* quoted item 2
* quoted item 3
Toady
),
    [PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Bubba "])]),
    PottyMouth::Node.new(:ul, [
	        PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 2 "])]),
	        PottyMouth::Node.new(:li, [
			  PottyMouth::Node.new(:span, ["quoted item 3 "]),
			  PottyMouth::Node.new(:br),
			  PottyMouth::Node.new(:span, ["Toady "]),
			 ]),
	      ]),
     ]
  ],
  [%(
> Bubba
> * quoted item 2
> * quoted item 3
> Toady
),
    [PottyMouth::Node.new(:p, [
	        PottyMouth::Node.new(:blockquote, [
			  PottyMouth::Node.new(:p, [PottyMouth::Node.new(:span, ["Bubba "])]),
			  PottyMouth::Node.new(:ul, [
				     PottyMouth::Node.new(:li, [PottyMouth::Node.new(:span, ["quoted item 2 "])]),
				     PottyMouth::Node.new(:li, [
						PottyMouth::Node.new(:span, ["quoted item 3 "]),
						PottyMouth::Node.new(:br),
						PottyMouth::Node.new(:span, ["Toady "]),
					       ]),
				    ]),
			 ]),
	      ]),
     ]
  ],

]


w = PottyMouth::PottyMouth.new(url_check_domains=["www.mysite.com", "mysite.com"],
		   url_white_lists=[
		     /https?:\/\/mysite\.com\/allowed\/service/,
		     /https?:\/\/mysite\.com\/safe\/url/,
		   ],
		   allow_media=true)

failures = 0
i = 0

for source, output in contents
  blocks = w.parse(source)
  generated = blocks.to_str
  expected =PottyMouth::Node.new('div', output).to_str
  if generated != expected
    failures += 1
    puts "##{i}", "Expected:", expected, "Generated:", generated
    puts '=' * 70
    #break
  end
  i += 1
end

if failures
  puts "#{contents.length} tests; #{failures} failures"
end
