String.prototype.strip = function () { 
  return this.replace(/^\s*|\s*$/g, '');
};

var PottyMouth = function (url_check_domains, url_white_lists) {

  if (! url_check_domains) url_check_domains = [];
  if (! url_white_lists  ) url_white_lists   = [];

  url_check_domains = new RegExp('(' + url_check_domains.join(')|(') + ')', 'i');
  var short_line_length = 50;

  var protocol_pattern = /^\w+:\/\//i;

  var _domain_pattern = "([-\\\w]+\\\.)+\\\w\\\w+";

  //                         protocol                                  authentication               or just www   domain            path
  var _URI_pattern = "((" + "(https?|webcal|feed|ftp|news|nntp)://" + "([-\\\w]+(:[-\\\w]+)?@)?" + ")|www\\\.)" + _domain_pattern + "(/([-\\\w$\\\.+!*'(),;:@%&=?/~#]*[-\\\w$+*(@%&=/~#])?)?";

  var URI_pattern = _URI_pattern;

  var email_pattern = '[^()<>@,;:\\\"\\\[\\\]\\\s]+@' + _domain_pattern;

  var image_pattern = _URI_pattern + '\\\.(jpe?g|png|gif)';

  // youtube_pattern matches:
  //  http://www.youtube.com/watch?v=KKTDRqQtPO8 and
  //  http://www.youtube.com/v/KKTDRqQtPO8       and
  //  http://youtube.com/watch?v=KKTDRqQtPO8     and
  //  http://youtube.com/v/KKTDRqQtPO8
  var youtube_pattern = 'http://(?:www\\\.)?youtube.com/(?:watch\\\?)?v=?/?([\\\w\\\-]{11})';

  var TokenMatcher = function (name, pattern, replace) {
    this.name = name;
    this.pattern = pattern;
    this.replace = replace;
    this.match = function (s) {
        return s.match(this.pattern);
    };
  };

  var token_order = [
    new TokenMatcher('NEW_LINE'   , /^(\r?\n)/ ), // fuck you, Microsoft!  // TODO: is the \r even necessary in the JavaScript version?
    new TokenMatcher('YOUTUBE'    , new RegExp('^('+youtube_pattern+')', 'i')),
    new TokenMatcher('IMAGE'      , new RegExp('^('+image_pattern  +')')),
    new TokenMatcher('URL'        , new RegExp('^('+URI_pattern    +')')),
    new TokenMatcher('EMAIL'      , new RegExp('^('+email_pattern  +')')),

    new TokenMatcher('HASH'       , /^([\t ]*#[\t ]+)/            ),
    new TokenMatcher('DASH'       , /^([\t ]*-[\t ]+)/            ),
    new TokenMatcher('NUMBERED'   , /^([\t ]*\d+(\.\)?|\))[\t ]+)/),
    new TokenMatcher('ITEMSTAR'   , /^([\t ]*\*[\t ]+)/           ),
    new TokenMatcher('BULLET'     , /^([\t ]*\u2022[\t ]+)/       ),

    new TokenMatcher('UNDERSCORE' , /^(_)/ ),
    new TokenMatcher('STAR'       , /^(\*)/),

    new TokenMatcher('RIGHT_ANGLE', /^(>[\t ]*(?:>[\t ]*)*)/),

    new TokenMatcher('DEFINITION' , /^([^\n\:]{2,20}\:[\t ]+)(?=\S+)/),

    // The following are simple, context-independent replacement tokens
    new TokenMatcher('EMDASH'  , /^(--)/, '&#8212;'),
    // No way to reliably distinguish Endash from Hyphen, Dash & Minus,
    // so we don't.  See: http://www.alistapart.com/articles/emen/

    new TokenMatcher('ELLIPSIS', /^(\.\.\.)/, '&#8230;'),
    // new TokenMatcher('SMILEY' , /^(:\))/   , '&#9786;'), // smiley face, not in HTML 4.01, doesn't work in IE
  ];


  var Replacer = function (pattern, replace) {
    this.pattern = pattern;
    this.replace = replace;
  }

  var replace_list = [
    new Replacer(/(``)/, '&#8220;'),
    new Replacer(/('')/, '&#8221;'),

    // First we look for inter-word " and '
    new Replacer(/(\b"\b)/, '&#34;'), // double prime
    new Replacer(/(\b'\b)/, '&#8217;'), // apostrophe
    // Then we look for opening or closing " and '
    new Replacer(/(\b"\B)/, '&#8221;'), // close double quote
    new Replacer(/(\B"\b)/, '&#8220;'), // open double quote
    new Replacer(/(\b'\B)/, '&#8217;'), // close single quote
    new Replacer(/(\B'\b)/, '&#8216;'), // open single quote

    // Then we look for space-padded opening or closing " and '
    new Replacer(/(")(\s)/, '&#8221;$2'), // close double quote
    new Replacer(/(\s)(")/, '$1&#8220;'), // open double quote
    new Replacer(/(')(\s)/, '&#8217;$2'), // close single quote
    new Replacer(/(\s)(')/, '$1&#8216;'), // open single quote

    // Then we gobble up stand-alone ones
    new Replacer(/(`)/, '&#8216;'),
    //new Replacer(/(")/, '&#8221;'),
    //new Replacer(/(')/, '&#8217;'),
  ];


  var pre_replace = function (s) {
    for (var i in replace_list) {
      var r = replace_list[i];
      s = s.replace(r.pattern, r.replace);
    }
    return s;
  }


  var Token = function(name, content) {
    this.name = name;
    this.content = content;
    this.add = function (more) {
      this.content += more;
    }
    this.toString = function () {
      return this.content/*.replace('&', '&amp;')*/.replace(/</g, '&lt;' ).replace(/>/g, '&gt;' ); // TODO: figure this out
    }
    this.strip = function () {
      this.content = this.content.strip();
    }
  }


  var tokenize = function(s){
    var p = 0;
    var found_tokens = [];
    var unmatched_collection = '';
    while (p < s.length) {
      var found_token = false;
      for (var ti in token_order) {
        var tm = token_order[ti];
        var m = tm.match(s.slice(p));
        if (m) {
          found_token = true;
          var content = m[0];
          p += content.length;

          if (tm.replace) {
            unmatched_collection += tm.replace;
            break;
          }

          if (unmatched_collection) {
            found_tokens.push(new Token('TEXT', unmatched_collection));
          }

          unmatched_collection = '';

          if (tm.name == 'NEW_LINE') {
            if (found_tokens.length && found_tokens[found_tokens.length-1].name == 'TEXT') {
              found_tokens[found_tokens.length-1].add(' ');
            }
            content=' ';
          }

          found_tokens.push(new Token(tm.name, content));
          break;
        }
      }

      if (! found_token) {
        // Pull one character off the string and continue looking for tokens
        unmatched_collection += s.slice(p, p+1);
        p += 1;
      }
    }

    if (unmatched_collection.length) {
      found_tokens.push(new Token('TEXT', unmatched_collection));
    }
    return found_tokens;
  };


  var Attributes = function () {
    this.toString = function () {
      var s = '';
      for (var k in this) {
        if (k != 'toString') {
          s += ' ' + k+'="' + this[k] + '"';
        }
      }
      return s;
    }
  }


  var Node = function (name) {
    this.name = name;
    this.attributes = new Attributes();
    this.content = [];
    for (var i=1; i<arguments.length; i++){
      if (arguments[i]) {
        this.content.push(arguments[i]);
      }
    }
    this.push = function (item) {
      return this.content.push(item);
    };
    this.concat = function (extra) {
      this.content = this.content.concat(extra);
    }
    this.node_children = function () {
      for (var i in this.content) {
        if (this.content[i] instanceof Node) {
          return true;
        }
      }
      return false;
    };
    this.toString = function () {
      if (this.name == 'br' || this.name == 'img') {
        // <br></br> causes double-newlines, so we do this
        return '<' + this.name + this.attribute_string() + ' />';
      } else {
        var open = '<' + this.name + this.attribute_string() + '>';
        var close = '</' + this.name + '>';

        var c = ''
        for (var i in this.content) {
          c += this.content[i].toString() + '\n';
        }
        c = c.replace(/\n+$/g, '');
        c = c.replace(/^\s+|\s+$/g, '');
        c = c.replace(/\n/g, '\n  ');

        if (this.node_children()) {
          return open + '\n  ' + c + '\n' + close;
        } else if (this.name == 'span') {
          return c;
        } else {
          return open + c + close;
        }
      }
    };
    this.attribute_string = function () {
      return this.attributes.toString();
    }
  };


  var URLNode = function (content, internal) {
    this.name = 'a';
    this.content = [content.replace(/^http:\/\//, '')];
    this.attributes = new Attributes();
    this.attributes.href = content;
    if (! internal) {
      this.attributes['class'] = 'external';
    }
  }
  URLNode.prototype = new Node();


  var LinkNode = URLNode;


  var EmailNode = function (content) {
    this.name = 'a';
    this.content = [content];
    this.attributes = new Attributes();
    this.attributes.href = 'mailto:' + content;
    this.attributes['class'] = 'external';
  };
  EmailNode.prototype = new Node();


  var ImageNode = function (content) {
    this.name = 'img';
    this.content = [];
    this.attributes = new Attributes();
    this.attributes.src = content;
  };
  ImageNode.prototype = new Node();


  var YouTubeNode = function (content) {
    this.name = 'object';
    this.content = [];
    this.attributes = new Attributes();
    this.attributes.width = 425;
    this.attributes.height = 350;

    var ytid = content.match(youtube_pattern)[1];
    var url = 'http://www.youtube.com/v/'+ytid;

    var p = new Node('param');
    p.attributes.name = 'movie';
    p.attributes.value = url;
    this.content.push(p);

    p = new Node('param');
    p.attributes.name = 'wmode';
    p.attributes.value = 'transparent';
    this.content.push(p);

    var e = new Node('embed');
    e.attributes.type = 'application/x-shockwave-flash';
    e.attributes.wmode = 'transparent';
    e.attributes.src = url;
    e.attributes.width = 425;
    e.attributes.height = 350;
    this.content.push(e);
  };
  YouTubeNode.prototype = new Node();


  var is_list_token = function (t) {
    return t.name == 'HASH' || t.name == 'NUMBERED' || t.name == 'DASH' || t.name == 'ITEMSTAR' || t.name == 'BULLET';
  };


  var _handle_url = function (t) {
    var anchor = t.content;
    if (! anchor.match(protocol_pattern)) {
      anchor = 'http://' + anchor;
    }
    if (url_check_domains && anchor.match(url_check_domains)) {
      // console.debug('\tchecking urls for this domain');
      for (var i in url_white_lists) {
        var w = url_white_lists[i];
        // console.debug('\t\tchecking against', w);
        if (anchor.match(w)) {
          // console.debug('\t\tmatches the white lists')
          return new LinkNode(anchor, true);
        }
      }
      // console.debug('\tdidn\'t match any white lists, making text');
      return new Node('span', anchor);;
    } else {
      return new LinkNode(anchor, false);
    }
  };


  var parse_atomics = function (tokens) {
    var collect = [];
    while (tokens.length) {
      var t = tokens[0];
      if (t.name == 'TEXT') {
        tokens.shift();
        if (t.content.strip().length) {
          collect.push(new Node('span', t));
        }
      } else if (t.name == 'URL') {
        collect.push(_handle_url(tokens.shift()))
      } else if (t.name == 'IMAGE') {
        collect.push(new ImageNode(tokens.shift().content))
      } else if (t.name == 'EMAIL') {
        collect.push(new EmailNode(tokens.shift().content))
      } else if (t.name == 'YOUTUBE') {
        collect.push(new YouTubeNode(tokens.shift().content))
      } else if (t.name == 'RIGHT_ANGLE' || t.name == 'DEFINITION') {
        collect.push(new Node('span', tokens.shift()));
      } else if (is_list_token(t) && t.name != 'ITEMSTAR') {
        collect.push(new Node('span', tokens.shift()));
      } else {
        break;
      }
    }
    return collect;
  }


  var parse_italic = function (tokens, inner) {
    var t = tokens.shift();

    var collect = [];
    while (tokens.length) {
      var atomics = parse_atomics(tokens);
      if (atomics.length) {
        collect = collect.concat(atomics);
      } else if ((! inner) && (tokens[0].name == 'STAR' || tokens[0].name == 'ITEMSTAR')) {
        collect = collect.concat(parse_bold(tokens, true));
      } else if (tokens[0].name == 'UNDERSCORE') {
        tokens.shift();
        if (collect.length) {
          var newi = new Node('i');
          newi.concat(collect);
          return [newi];
        } else {
          return [];
        }
      } else {
        break
      }
    }
    collect.unshift(new Node('span', '_'));
    return collect;
  };


  var parse_bold = function (tokens, inner) {
    var t = tokens.shift();

    var collect = [];
    while (tokens.length) {
      var atomics = parse_atomics(tokens);
      if (atomics.length) {
        collect = collect.concat(atomics);
      } else if ((! inner) && tokens[0].name == 'UNDERSCORE') {
        collect = collect.concat(parse_italic(tokens, true));
      } else if (tokens[0].name == 'STAR' || tokens[0].name == 'ITEMSTAR') {
        tokens.shift();
        if (collect.length){
          var newb = new Node('b');
          newb.concat(collect);
          return [newb];
        } else {
          return [];
        }
      } else {
        break;
      }
    }
    collect.unshift(new Node('span', '*'))
    return collect;
  };


  var parse_line = function (tokens) {
    var collect = [];
    while (tokens) {
      var atomics = parse_atomics(tokens);
      if (atomics.length) {
        collect = collect.concat(atomics);
      }
      if (! tokens.length) {
        break;
      } else if (tokens[0].name == 'UNDERSCORE') {
        collect = collect.concat(parse_italic(tokens, false));
      } else if (tokens[0].name == 'STAR' || tokens[0].name == 'ITEMSTAR') {
        collect = collect.concat(parse_bold(tokens, false));
      } else {
        break;
      }
    }
    return collect;
  };


  var parse_list = function (tokens) {
    var t = tokens[0];

    if (t.name == 'HASH' || t.name == 'NUMBERED') {
      var l = new Node('ol');
    } else if (t.name == 'DASH' || t.name == 'ITEMSTAR' || t.name == 'BULLET') {
      var l = new Node('ul');
    }

    while (tokens.length) {
      var t = tokens[0];
      if (is_list_token(t)) {
        tokens.shift();
        var i = new Node('li');
        i.concat(parse_line(tokens));
        l.push(i);
      } else if (tokens[0].name == 'NEW_LINE') {
        tokens.shift();
        if (tokens && is_list_token(t)) {
          break;
        }
      } else {
        break;
      }
    }
    return [l];
  };


  var parse_definition = function (tokens) {
    var dl = new Node('dl');
    while (tokens.length) {
      if (tokens[0].name == 'DEFINITION') {
        dl.push(new Node('dt', tokens.shift()));
        var dd = new Node('dd');
        dd.concat(parse_line(tokens));
        dl.push(dd);
      } else if (tokens[0].name == 'NEW_LINE') {
        tokens.shift();
        if (tokens.length && tokens[0].name != 'DEFINITION') {
          break;
        }
      } else {
        break;
      }
    }
    return [dl]
  };


  var parse_quote = function (tokens) {
    var quote = new Node('blockquote');
    var new_tokens = [];

    var handle_quote = function (token){
      var new_angle = token.content.replace(/^>\s*/, '').strip();
      if (new_angle.length) {
        new_tokens.push(new Token('RIGHT_ANGLE', new_angle))
      }
    };

    handle_quote(tokens.shift());

    while (tokens.length) {
      if (tokens[0].name == 'NEW_LINE') {
        new_tokens.push(tokens.shift())
        if (tokens.length) {
          if (tokens[0].name == 'RIGHT_ANGLE') {
            handle_quote(tokens.shift());
          } else {
            break;
          }
         }
      } else {
        new_tokens.push(tokens.shift());
      }
    }

    quote.concat(parse_blocks(new_tokens));
    return [quote];
  };


  var calculate_line_length = function (line) {
    var length = 0;
    for (var i in line) {
      if (line[i] instanceof Node) {
        length += calculate_line_length(line[i].content);
      } else if (line[i] instanceof Token) {
        length += line[i].content.length;
      } else if (typeof(line[i]) == 'string') {
        length += line[i].length;
      } else {
        throw typeof(line[i]) + line[i].name;
      }
    }
    return length;
  };


  var parse_paragraph = function (tokens) {
    var p = new Node('p');
    var shorts = [];

    var parse_shorts = function(shorts, line) {
      var collect = [];
      if (shorts.length >= 2) {
        if (p.content.length) {
          // there was a long line before this
          collect.push(new Node('br'))
        }
        collect = collect.concat(shorts.shift());
        while (shorts.length) {
          collect.push(new Node('br'));
          collect = collect.concat(shorts.shift());
        }
        if (line.length) {
          // there is a long line after this
          collect.push(new Node('br'));
        }
      } else {
        while (shorts.length) {
          collect = collect.concat(shorts.shift());
        }
      }
      return collect;
    };

    while (tokens.length) {
      var t = tokens[0];
      if (t.name == 'NEW_LINE') {
        tokens.shift();
        if (tokens.length && tokens[0].name == 'NEW_LINE') {
          tokens.shift();
          break;
        } else if (tokens.length && (tokens[0].name == 'RIGHT_ANGLE' || tokens[0].name == 'DEFINITION' || is_list_token(tokens[0]))) {
          break;
        }
      } else {
        var line = parse_line(tokens);
        if (! line.length) {
          break;
        } else if (calculate_line_length(line) < short_line_length) {
          shorts.push(line);
        } else {
          p.concat(parse_shorts(shorts, line));
          p.concat(line);
        }
      }
    }

    p.concat(parse_shorts(shorts, []));

    if (p.content.length) {
      return [p];
    } else {
      return [];
    }
  };


  var parse_blocks = function (tokens) {
    var collect = [];
    while (tokens.length) {
      var t = tokens[0];
      if (t.name == 'NEW_LINE') {
        tokens.shift();
      } else if (t.name == 'RIGHT_ANGLE') {
        collect = collect.concat(parse_quote(tokens));
      } else if (is_list_token(t)) {
        collect = collect.concat(parse_list(tokens));
      } else if (t.name == 'DEFINITION') {
        collect = collect.concat(parse_definition(tokens));
      } else {
        collect = collect.concat(parse_paragraph(tokens));
      }
    }
    return collect;
  };


  this.parse = function (s) {
    var finished = parse_blocks(tokenize(pre_replace(s)));
    var div = new Node('div');
    div.concat(finished);
    return div;
  };


  this.expose_internals_for_tests = function () {
    // This is a list of all the "private" variables that must
    // be "exposed" for testing, by being attached to this.
    this.protocol_pattern = protocol_pattern;
    this.domain_pattern   = _domain_pattern ;
    this.URI_pattern      = URI_pattern     ;
    this.email_pattern    = email_pattern   ;
    this.image_pattern    = image_pattern   ;
    this.youtube_pattern  = youtube_pattern ;

    this.pre_replace = pre_replace;
    this.tokenize = tokenize;
  };

};
