#!/usr/bin/env python
#
# The Basic PottyMouth grammar:
# =============================
#
# start => block +
# block => ( quote | itemlist | definitionlist | paragraph ) newline *
# quote => ( quote | block) +
# itemlist => ( bullet line ) +
# definitionlist => ( term line) +
# paragraph => line + newline newline
# line => ( atomic | bold | italic ) +
# bold => ( atomic | italic ) +
# italic => ( atomic | italic ) +

import re

__version__ = '2.0.0'
short_line_length = 50
encoding = 'utf8' # Default output encoding


class TokenMatcher(object):

    def __init__(self, name, pattern, replace=None):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE | re.UNICODE)
        self.replace = replace

    def match(self, string):
        return self.pattern.match(string)


protocol_pattern = re.compile(r'^\w+://', re.IGNORECASE)

domain_pattern = r"([-\w]+\.)+\w\w+"

_URI_pattern = ("(("                                     +
               r"(https?|webcal|feed|ftp|news|nntp)://" + # protocol
               r"([-\w]+(:[-\w]+)?@)?"                  + # authentication
               r")|www\.)"                              + # or just www.
               domain_pattern                           + # domain
               r"(/([-\w$\.+!*'(),;:@%&=?/~#]*[-\w$+*(@%&=/~#])?)?" # path
               )

URI_pattern = _URI_pattern

email_pattern = r'[^()<>@,;:\"\[\]\s]+@' + domain_pattern

image_pattern = _URI_pattern + '\.(jpe?g|png|gif)'

# youtube_pattern matches:
#  http://www.youtube.com/watch?v=KKTDRqQtPO8 and
#  http://www.youtube.com/v/KKTDRqQtPO8       and
#  http://youtube.com/watch?v=KKTDRqQtPO8     and
#  http://youtube.com/v/KKTDRqQtPO8
youtube_pattern = r'http://(?:www\.)?youtube.com/(?:watch\?)?v=?/?([\w\-]{11})'
youtube_matcher = re.compile(youtube_pattern, re.IGNORECASE)

# Unicode whitespace, not including newlines
white = ur'[ \t\xa0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F\u3000]'

token_order = (
    TokenMatcher('NEW_LINE'   , r'(\r?\n)'), #fuck you, Microsoft!
    TokenMatcher('YOUTUBE'    , '('+youtube_pattern+')'),
    TokenMatcher('IMAGE'      , '('+image_pattern  +')'),
    TokenMatcher('URL'        , '('+URI_pattern    +')'),
    TokenMatcher('EMAIL'      , '('+email_pattern  +')'),

    TokenMatcher('HASH'       , '(' + white + '*#' + white + '+)(?=\S+)'             ),
    TokenMatcher('DASH'       , '(' + white + '*-' + white + '+)(?=\S+)'             ),
    TokenMatcher('NUMBERED'   , '(' + white + r'*\d+(\.\)?|\))' + white + '+)(?=\S+)'),
    TokenMatcher('ITEMSTAR'   , '(' + white + r'*\*' + white + '+)(?=\S+)'           ),
    TokenMatcher('BULLET'     , '(' + white + ur'*\u2022' + white + '+)(?=\S+)'      ),

    TokenMatcher('UNDERSCORE' , r'(_)' ),
    TokenMatcher('STAR'       , r'(\*)'),

    TokenMatcher('RIGHT_ANGLE', '(>' + white + '*(?:>' + white + '*)*)'),

    TokenMatcher('DEFINITION' , r'([^\n\:]{2,20}\:' + white + r'+)(?=\S+)'),

    # The following are simple, context-independent replacement tokens
    TokenMatcher('EMDASH'  , r'(--)'    , replace=unichr(8212)),
    # No way to reliably distinguish Endash from Hyphen, Dash & Minus,
    # so we don't.  See: http://www.alistapart.com/articles/emen/

    TokenMatcher('ELLIPSIS', r'(\.\.\.)', replace=unichr(8230)),
    #TokenMatcher('SMILEY' , r'(:\))'   , replace=unichr(9786)), # smiley face, not in HTML 4.01, doesn't work in IE
    )



# The "Replacers" are context sensitive replacements, therefore they
# must be applied in-line to the string as a whole before tokenizing.
# Another option would be to keep track of previous context when
# applying tokens.
class Replacer(object):

    def __init__(self, pattern, replace):
        self.pattern = re.compile(pattern)
        self.replace = replace

    def sub(self, string):
        return self.pattern.sub(self.replace, string)


replace_list = [
    Replacer(r'(``)', unichr(8220)),
    Replacer(r"('')", unichr(8221)),

    # First we look for inter-word " and '
    Replacer(r'(\b"\b)', unichr(34)), # double prime
    Replacer(r"(\b'\b)", unichr(8217)), # apostrophe
    # Then we look for opening or closing " and '
    Replacer(r'(\b"\B)', unichr(8221)), # close double quote
    Replacer(r'(\B"\b)', unichr(8220)), # open double quote
    Replacer(r"(\b'\B)", unichr(8217)), # close single quote
    Replacer(r"(\B'\b)", unichr(8216)), # open single quote

    # Then we look for space-padded opening or closing " and '
    Replacer(r'(")(\s)', unichr(8221)+r'\2'), # close double quote
    Replacer(r'(\s)(")', r'\1'+unichr(8220)), # open double quote 
    Replacer(r"(')(\s)", unichr(8217)+r'\2'), # close single quote
    Replacer(r"(\s)(')", r'\1'+unichr(8216)), # open single quote

    # Then we gobble up stand-alone ones
    Replacer(r'(`)', unichr(8216)),
    #Replacer(r'(")', unichr(8221)),
    #Replacer(r"(')", unichr(8217)),
    ]



class Token(unicode):

    def __new__(cls, name, content=''):
        self = unicode.__new__(cls, content)
        return self

    def __init__(self, name, content=''):
        self.name = name

    def __repr__(self):
        return '%s{%s}'%(self.name, super(Token, self).__repr__())

    def __add__(self, extra):
        return Token(self.name, super(Token, self).__add__(extra))

    def __str__(self):
        return self.encode(encoding, 'xmlcharrefreplace')



# escape() is made available to calling code in case it needs to
# escape the content of PottyMouth Nodes before converting it to
# another tree object that does not automatically escape these
# disallowed HTML characters.
def escape(string):
    out = string.replace('&', '&amp;')
    out =    out.replace('<', '&lt;' )
    out =    out.replace('>', '&gt;' )
    return out



class Node(list):

    def __init__(self, name, *contents, **kw):
        super(list, self).__init__()
        self.name = name.lower()
        self.extend(contents)
        self._attributes = kw.get('attributes', {})


    def node_children(self):
        for n in self:
            if isinstance(n, Node):
                return True
        return False


    def __str__(self):
        if self.name in ('br','img'): # Also <hr>
            # <br></br> causes double-newlines, so we do this
            return '<%s%s />' % (self.name, self._attribute_string())
        else:
            content = ''
            for c in self:
                if isinstance(c, Node):
                    content += str(c)
                else:
                    content += escape(c).encode(encoding, 'xmlcharrefreplace')
                content += '\n'
            content = content.strip().rstrip('\n')
            content = content.replace('\n', '\n  ')

            interpolate = {'name'   :self.name               ,
                           'attrs'  :self._attribute_string(),
                           'content':content                 ,}

            if self.node_children():
                return '<%(name)s%(attrs)s>\n  %(content)s\n</%(name)s>' % interpolate
            elif self.name == 'span':
                return content
            else:
                return '<%(name)s%(attrs)s>%(content)s</%(name)s>' % interpolate


    def _attribute_string(self):
        content = ''
        if self._attributes:
            for k, v in self._attributes.items():
                content += ' %s="%s"' % (k, escape(v).encode(encoding, 'xmlcharrefreplace'))
        return content



class URLNode(Node):

    def __init__(self, content, internal=False):
        attributes = {'href':content}
        if not internal:
            attributes['class'] = 'external'

        if content.startswith('http://'):
            content = content[7:]

        Node.__init__(self, 'a', content, attributes=attributes)



class LinkNode(URLNode):

    pass



class EmailNode(URLNode):

    def __init__(self, content, internal=False):
        attributes = {'href':'mailto:'+content}
        if not internal:
            attributes['class'] = 'external'

        Node.__init__(self, 'a', content, attributes=attributes)



class ImageNode(Node):

    def __init__(self, content):
        Node.__init__(self, 'img', '', attributes={'src':content})



class YouTubeNode(Node):

    def __init__(self, content):
        Node.__init__(self, 'object', attributes={'width':'425', 'height':'350',})

        ytid = youtube_matcher.match(content).groups()[0]
        url = 'http://www.youtube.com/v/'+ytid

        self.append(Node(name='param',
                         attributes={'name':'movie', 'value':url,}))
        self.append(Node('param',
                         attributes={'name':'wmode', 'value':'transparent',}))
        self.append(Node('embed',
                         attributes={'type':'application/x-shockwave-flash',
                                     'wmode':'transparent','src':url,
                                     'width':'425', 'height':'350',}))



def debug(*a):
    print ' '.join(map(repr, a))



class PottyMouth(object):

    def __init__(self, url_check_domains=(), url_white_lists=(),
                 all_links=True,      # disables all URL hyperlinking
                 image=True,          # disables <img> tags for image URLs
                 youtube=True,        # disables YouTube embedding
                 email=True,          # disables mailto:email@site.com URLs
                 all_lists=True,      # disables all lists (<ol> and <ul>)
                 unordered_list=True, # disables all unordered lists (<ul>)
                 ordered_list=True,   # disables all ordered lists (<ol>)
                 numbered_list=True,  # disables '\d+\.' lists 
                 blockquote=True,     # disables '>' <blockquote>s
                 definition_list=True,# disables all definition lists (<dl>)
                 bold=True,           # disables *bold*
                 italic=True,         # disables _italics_
                 emdash=True,         # disables -- emdash
                 ellipsis=True,       # disables ... ellipsis
                 smart_quotes=True,   # disables smart quotes
                 ):

        self._url_check_domain = None
        if url_check_domains:
            if isinstance(url_check_domains, str):
                url_check_domains = (url_check_domains,)
            self._url_check_domain = re.compile('(\w+://)?((' + ')|('.join(url_check_domains) + '))',
                                                flags=re.I)

        self._url_white_lists  = [re.compile(w) for w in url_white_lists]
        self.smart_quotes = smart_quotes

        self.token_list = []
        for t in token_order:
            n = t.name
            if n in ('URL','IMAGE','YOUTUBE','EMAIL') and not all_links:
                continue
            elif n == 'IMAGE' and not image:                           continue
            elif n == 'YOUTUBE' and not youtube:                       continue
            elif n == 'EMAIL' and not email:                           continue
            elif n in ('HASH','DASH','NUMBERED','ITEMSTAR','BULLET') and not all_lists:
                continue 
            elif n in ('DASH','ITEMSTAR','BULLET') and not unordered_list:
                continue
            elif n in ('HASH','NUMBERED') and not ordered_list:
                continue
            elif n == 'DEFINITION' and not definition_list:            continue
            elif n == 'NUMBERED' and not numbered_list:                continue
            elif n == 'STAR' and not bold:                             continue
            elif n == 'UNDERSCORE' and not italic:                     continue
            elif n == 'RIGHT_ANGLE' and not blockquote:                continue
            elif n == 'EMDASH' and not emdash:                         continue
            elif n == 'ELLIPSIS' and not ellipsis:                     continue

            self.token_list.append(t)


    def debug(self, *s):
        return
        print ' '.join(map(str, s))


    def pre_replace(self, string):
        for r in replace_list:
            string = r.sub(string)
        return string


    def tokenize(self, string):
        p = 0
        found_tokens = []
        unmatched_collection = ''
        while p < len(string):
            found_token = False
            for tm in self.token_list:
                m = tm.match(string[p:])
                if m:
                    found_token = True
                    content = m.groups()[0]
                    p += len(content)

                    if tm.replace is not None: 
                        unmatched_collection += tm.replace
                        break

                    if unmatched_collection:
                        try:
                            found_tokens.append(Token('TEXT', unmatched_collection))
                        except UnicodeDecodeError:
                            found_tokens.append(Token('TEXT', unmatched_collection.decode('utf8')))
                        except:
                            raise

                    unmatched_collection = ''

                    if tm.name == 'NEW_LINE':
                        if found_tokens and found_tokens[-1].name == 'TEXT':
                            found_tokens[-1] += ' '
                        content=' '

                    found_tokens.append(Token(tm.name, content))
                    break

            if not found_token:
                # Pull one character off the string and continue looking for tokens
                unmatched_collection += string[p]
                p += 1

        if unmatched_collection:
            found_tokens.append(Token('TEXT', unmatched_collection))

        return found_tokens


    def is_list_token(self, t):
        return t.name == 'HASH' or t.name == 'NUMBERED' or t.name == 'DASH' or t.name == 'ITEMSTAR' or t.name == 'BULLET'


    def handle_url(self, t):
        if not protocol_pattern.match(t):
            t = Token(t.name, 'http://' + t)

        if self._url_check_domain and self._url_check_domain.findall(t):
            # debug('\tchecking urls for this domain', len(self._url_white_lists))
            for w in self._url_white_lists:
                # debug('\t\tchecking against', str(w))
                if w.match(t):
                    self.debug('\t\tmatches the white lists')
                    return LinkNode(t, internal=True)
            # debug('\tdidn\'t match any white lists, making text')
            return Node('span', t)
        else:
            return LinkNode(t)


    def parse_atomics(self, tokens):
        collect = []
        while tokens:
            t = tokens[0]
            if t.name == 'TEXT':
                t = tokens.pop(0).strip()
                if t:
                    collect.append(Node('span', t))
            elif t.name == 'URL':
                collect.append(self.handle_url(tokens.pop(0)))
            elif t.name == 'IMAGE':
                collect.append(ImageNode(tokens.pop(0)))
            elif t.name == 'EMAIL':
                collect.append(EmailNode(tokens.pop(0)))
            elif t.name == 'YOUTUBE':
                collect.append(YouTubeNode(tokens.pop(0)))
            elif t.name == 'RIGHT_ANGLE':
                collect.append(Node('span', tokens.pop(0)))
            elif t.name == 'DEFINITION':
                collect.append(Node('span', tokens.pop(0)))
            elif self.is_list_token(t) and t.name != 'ITEMSTAR':
                collect.append(Node('span', tokens.pop(0)))
            else:
                break
        return collect


    def parse_italic(self, tokens, inner=False):
        t = tokens.pop(0)
        assert t.name == 'UNDERSCORE'

        collect = []
        while tokens:
            atomics = self.parse_atomics(tokens)
            if atomics:
                collect.extend(atomics)
            elif not inner and (tokens[0].name == 'STAR' or tokens[0].name == 'ITEMSTAR'):
                collect.extend(self.parse_bold(tokens, inner=True))
            elif tokens[0].name == 'UNDERSCORE':
                tokens.pop(0)
                if collect:
                    newi = Node('i')
                    newi.extend(collect)
                    return [newi]
                else:
                    return []
            else:
                break
        return [Node('span', '_')] + collect


    def parse_bold(self, tokens, inner=False):
        t = tokens.pop(0)
        assert t.name == 'STAR' or t.name == 'ITEMSTAR'

        collect = []
        while tokens:
            atomics = self.parse_atomics(tokens)
            if atomics:
                collect.extend(atomics)
            elif not inner and tokens[0].name == 'UNDERSCORE':
                collect.extend(self.parse_italic(tokens, inner=True))
            elif tokens[0].name == 'STAR' or tokens[0].name == 'ITEMSTAR':
                tokens.pop(0)
                if collect:
                    newb = Node('b')
                    newb.extend(collect)
                    return [newb]
                else:
                    return []
            else:
                break

        return [Node('span', '*')] + collect


    def parse_line(self, tokens):
        collect = []
        while tokens:
            atomics = self.parse_atomics(tokens)
            if atomics:
                collect.extend(atomics)
            if not tokens:
                break
            elif tokens[0].name == 'UNDERSCORE':
                collect.extend(self.parse_italic(tokens))
            elif tokens[0].name == 'STAR' or tokens[0].name == 'ITEMSTAR':
                collect.extend(self.parse_bold(tokens))
            else:
                break
        return collect


    def parse_list(self, tokens):
        t = tokens[0]
        assert self.is_list_token(t)

        if t.name == 'HASH' or t.name == 'NUMBERED':
            l = Node('ol')
        elif t.name == 'DASH' or t.name == 'ITEMSTAR' or t.name == 'BULLET':
            l = Node('ul')

        while tokens:
            t = tokens[0]
            if self.is_list_token(t):
                tokens.pop(0)
                i = Node('li')
                i.extend(self.parse_line(tokens))
                l.append(i)
            elif tokens[0].name == 'NEW_LINE':
                tokens.pop(0)
                if tokens and self.is_list_token(t):
                    break
            else:
                break
        return [l]


    def parse_definition(self, tokens):
        assert tokens[0].name == 'DEFINITION'

        dl = Node('dl')
        while tokens:
            if tokens[0].name == 'DEFINITION':
                dt = tokens.pop(0)
                dl.append(Node('dt', dt))
                dd = Node('dd')
                dd.extend(self.parse_line(tokens))
                dl.append(dd)
            elif tokens[0].name == 'NEW_LINE':
                tokens.pop(0)
                if tokens and tokens[0].name != 'DEFINITION':
                    break
            else:
                break
        return [dl]


    def parse_quote(self, tokens):
        assert tokens[0].name == 'RIGHT_ANGLE'
        quote = Node('blockquote')
        new_tokens = []

        def handle_quote(token):
            new_angle = token.replace('>', '', 1).strip()
            if new_angle:
                new_tokens.append(Token('RIGHT_ANGLE', new_angle))

        handle_quote(tokens.pop(0))

        while tokens:
            if tokens[0].name == 'NEW_LINE':
                new_tokens.append(tokens.pop(0))
                if tokens:
                    if tokens[0].name == 'RIGHT_ANGLE':
                        handle_quote(tokens.pop(0))
                    else:
                        break
            else:
                new_tokens.append(tokens.pop(0))

        quote.extend(self.parse_blocks(new_tokens))
        return [quote]


    def calculate_line_length(self, line):
        length = 0
        for i in line:
            if issubclass(type(i), list):
                length += self.calculate_line_length(i)
            elif issubclass(type(i), unicode) or issubclass(type(i), str):
                length += len(i)
            else:
                raise Exception(str(type(i)))
        return length


    def parse_paragraph(self, tokens):
        p = Node('p')
        shorts = []

        def parse_shorts(shorts, line=None):
            collect = []
            if len(shorts) >= 2:
                if p:
                    # there was a long line before this
                    collect.append(Node('br'))
                collect.extend(shorts.pop(0))
                while shorts:
                    collect.append(Node('br'))
                    collect.extend(shorts.pop(0))
                if line:
                    # there is a long line after this
                    collect.append(Node('br'))
            else:
                while shorts:
                    collect.extend(shorts.pop(0))
            return collect

        while tokens:
            t = tokens[0]
            if t.name == 'NEW_LINE':
                tokens.pop(0)
                if tokens and tokens[0].name == 'NEW_LINE':
                    tokens.pop(0)
                    break
                elif tokens and (tokens[0].name == 'RIGHT_ANGLE' or tokens[0].name == 'DEFINITION' or self.is_list_token(tokens[0])):
                    break
            else:
                line = self.parse_line(tokens)
                if not line:
                    break
                elif self.calculate_line_length(line) < short_line_length:
                    shorts.append(line)
                else:
                    p.extend(parse_shorts(shorts, line))
                    p.extend(line)

        p.extend(parse_shorts(shorts))

        if p:
            return [p]
        else:
            return []


    def parse_blocks(self, tokens):
        collect = []
        while tokens:
            t = tokens[0]
            if t.name == 'NEW_LINE':
                tokens.pop(0)
            elif t.name == 'RIGHT_ANGLE':
                collect.extend(self.parse_quote(tokens))
            elif self.is_list_token(t):
                collect.extend(self.parse_list(tokens))
            elif t.name == 'DEFINITION':
                collect.extend(self.parse_definition(tokens))
            else:
                collect.extend(self.parse_paragraph(tokens))
        return collect


    def parse(self, s):
        if isinstance(s, str):
            s = s.decode(encoding)
        assert isinstance(s, unicode), "PottyMouth input must be unicode or str types"

        s = self.pre_replace(s)

        tokens = self.tokenize(s)

        finished = self.parse_blocks(tokens)

        return finished



if __name__ == '__main__':
    import sys
    w = PottyMouth(url_check_domains=('www.mysite.com', 'mysite.com'),
                   url_white_lists=('https?://www\.mysite\.com/allowed/url\?id=\d+',),
                   )
    while True:
        print 'input (end with Ctrl-D)>>'
        try:
            text = sys.stdin.read()
            sys.stdin.seek(0)
        except KeyboardInterrupt:
            break
        if text:
            blocks = w.parse(text)
            for b in blocks:
                print b
            print '=' * 70
