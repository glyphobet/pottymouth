String.prototype.strip = function () { 
  return this.replace(/^\s*|\s*$/g, '');
};

var PottyMouth = function (url_check_domains, url_white_lists) {
  this.__version__ = '2.1.0';

  if (! url_check_domains) { url_check_domains = []; }
  if (! url_white_lists  ) { url_white_lists   = []; }

  var url_check_domain = undefined;
  if (url_check_domains.length) {
    url_check_domain = new RegExp('(' + url_check_domains.join(')|(') + ')', 'i');
  }

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
    new TokenMatcher('NEW_LINE'   , /^(\r?\n)([\t ]*)/ ), // fuck you, Microsoft!  // TODO: is the \r even necessary in the JavaScript version?
    // INDENT token is created when the second group in NEW_LINE pattern matches
    new TokenMatcher('YOUTUBE'    , new RegExp('^('+youtube_pattern+')', 'i')),
    new TokenMatcher('IMAGE'      , new RegExp('^('+image_pattern  +')')),
    new TokenMatcher('URL'        , new RegExp('^('+URI_pattern    +')')),
    new TokenMatcher('EMAIL'      , new RegExp('^('+email_pattern  +')')),

    new TokenMatcher('HASH'       , /^([\t ]*#[\t ]+)(?=\S+)/            ),
    new TokenMatcher('DASH'       , /^([\t ]*-[\t ]+)(?=\S+)/            ),
    new TokenMatcher('NUMBERED'   , /^([\t ]*\d+(\.\)?|\))[\t ]+)(?=\S+)/),
    new TokenMatcher('ITEMSTAR'   , /^([\t ]*\*[\t ]+)(?=\S+)/           ),
    new TokenMatcher('BULLET'     , /^([\t ]*\u2022[\t ]+)(?=\S+)/       ),

    new TokenMatcher('UNDERSCORE' , /^(_)/ ),
    new TokenMatcher('STAR'       , /^(\*)/),

    new TokenMatcher('RIGHT_ANGLE', /^(>(?:[\t ]*>)*)([\t ]*)/),

    new TokenMatcher('DEFINITION' , /^([^\n\:]{2,20}\:[\t ]+)(?=\S+)/),

    // The following are simple, context-independent replacement tokens
    new TokenMatcher('EMDASH'  , /^(--)/, '&#8212;'),
    // No way to reliably distinguish Endash from Hyphen, Dash & Minus,
    // so we don't.  See: http://www.alistapart.com/articles/emen/

    new TokenMatcher('ELLIPSIS', /^(\.\.\.)/, '&#8230;')
    // new TokenMatcher('SMILEY' , /^(:\))/   , '&#9786;'), // smiley face, not in HTML 4.01, doesn't work in IE
  ];


  var Replacer = function (pattern, replace) {
    this.pattern = pattern;
    this.replace = replace;
  };

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
    new Replacer(/(`)/, '&#8216;')
    //new Replacer(/(")/, '&#8221;'),
    //new Replacer(/(')/, '&#8217;'),
  ];


  var pre_replace = function (s) {
    for (var i in replace_list) {
      var r = replace_list[i];
      s = s.replace(r.pattern, r.replace);
    }
    return s;
  };


  var Token = function(name, content) {
    this.name = name;
    this.content = content;
    this.add = function (more) {
      this.content += more;
    };
    this.toString = function () {
      return this.content.replace(/</g, '&lt;' ).replace(/>/g, '&gt;' );
    };
    this.strip = function () {
      this.content = this.content.strip();
    };
  };


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
          var content = m[1];
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

          if ((tm.name == 'NEW_LINE' || tm.name == 'RIGHT_ANGLE') && m[2].length) {
            found_tokens.push(new Token('INDENT', m[2]));
            p += m[2].length
          }

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


  var Attributes = function (a) {
    for (var k in a) {
      this[k] = a[k];
    }
    this.toString = function () {
      var s = '';
      for (var k in this) {
        if (k != 'toString') {
          s += ' ' + k+'="' + this[k] + '"';
        }
      }
      return s;
    };
  };


  var Node = function (name, content, attributes) {
    this.name = name;
    this.attributes = new Attributes(attributes ? attributes : {});
    this.content = content ? content : [];

    this.push = function (item) {
      return this.content.push(item);
    };
    this.concat = function (extra) {
      this.content = this.content.concat(extra);
    };
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
        return '<' + this.name + this.attributes.toString() + ' />';
      } else {
        var open = '<' + this.name + this.attributes.toString() + '>';
        var close = '</' + this.name + '>';

        var c = '';
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
  };


  var URLNode = function (content, internal) {
    this.name = 'a';
    this.content = [content.replace(/^http:\/\//, '')];
    this.attributes = new Attributes({href:content});
    if (! internal) {
      this.attributes['class'] = 'external';
    }
  };
  URLNode.prototype = new Node();


  var LinkNode = URLNode;


  var EmailNode = function (content) {
    this.name = 'a';
    this.content = [content];
    this.attributes = new Attributes({href:'mailto:' + content, 'class':'external'});
  };
  EmailNode.prototype = new Node();


  var ImageNode = function (content) {
    this.name = 'img';
    this.content = [];
    this.attributes = new Attributes({src:content});
  };
  ImageNode.prototype = new Node();


  var YouTubeNode = function (content) {
    var ytid = content.match(youtube_pattern)[1];
    var url = 'http://www.youtube.com/v/'+ytid;

    this.name = 'object';
    this.attributes = new Attributes({width:425, height:350});
    this.content = [
      new Node('param', [], {name:'movie', value:url}),
      new Node('param', [], {name:'wmode', value:'transparent'}),
      new Node('embed', [], {
        type:'application/x-shockwave-flash',
        wmode:'transparent',
        src:url,
        width:425,
        height:350
      })
    ];
  };
  YouTubeNode.prototype = new Node();


  var is_list_token = function (t) {
    return t.name == 'HASH' || t.name == 'NUMBERED' || t.name == 'DASH' || t.name == 'ITEMSTAR' || t.name == 'BULLET';
  };


  var handle_url = function (t) {
    var anchor = t.content;
    if (! anchor.match(protocol_pattern)) {
      anchor = 'http://' + anchor;
    }
    if (url_check_domain && anchor.match(url_check_domain)) {
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
      return new Node('span', [anchor]);
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
          collect.push(new Node('span', [t]));
        }
      } else if (t.name == 'URL') {
        collect.push(handle_url(tokens.shift()));
      } else if (t.name == 'IMAGE') {
        collect.push(new ImageNode(tokens.shift().content));
      } else if (t.name == 'EMAIL') {
        collect.push(new EmailNode(tokens.shift().content));
      } else if (t.name == 'YOUTUBE') {
        collect.push(new YouTubeNode(tokens.shift().content));
      } else if (t.name == 'RIGHT_ANGLE' || t.name == 'DEFINITION') {
        collect.push(new Node('span', [tokens.shift()]));
      } else if (is_list_token(t) && t.name != 'ITEMSTAR') {
        collect.push(new Node('span', [tokens.shift()]));
      } else {
        break;
      }
    }
    return collect;
  };


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
          return [new Node('i', collect)];
        } else {
          return [];
        }
      } else {
        break;
      }
    }
    collect.unshift(new Node('span', ['_']));
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
          return [new Node('b', collect)];
        } else {
          return [];
        }
      } else {
        break;
      }
    }
    collect.unshift(new Node('span', ['*']));
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
    var initial_indent = 0;
    if (tokens[0].name == 'INDENT') {
      initial_indent = tokens[0].content.length;
      tokens.shift();
    }
    var t = tokens[0];

    if (t.name == 'HASH' || t.name == 'NUMBERED') {
      var l = new Node('ol');
    } else if (t.name == 'DASH' || t.name == 'ITEMSTAR' || t.name == 'BULLET') {
      var l = new Node('ul');
    }

    while (tokens.length) {
      t = tokens[0];
      if (is_list_token(t)) {
        tokens.shift();
        l.push(new Node('li', parse_line(tokens)));
      } else if (t.name == 'NEW_LINE') {
        tokens.shift();
        if (tokens.length && !is_list_token(tokens[0]) && tokens[0].name != 'INDENT') {
          break;
        }
      } else if (t.name == 'INDENT') {
        tokens.shift();
        if (t.content.length > initial_indent) {
          if (tokens.length && ! is_list_token(tokens[0])) {
            l.content[l.content.length-1].concat(parse_line(tokens));
          }
        }
      } else {
        break;
      }
    }
    return [l];
  };


  var parse_definition = function (tokens) {
    var initial_indent = 0;
    if (tokens[0].name == 'INDENT') {
      initial_indent = tokens[0].content.length;
      tokens.shift();
    }
    var dl = new Node('dl');
    var t;
    while (tokens.length) {
      t = tokens[0];
      if (t.name == 'DEFINITION') {
        dl.push(new Node('dt', [tokens.shift()]));
        dl.push(new Node('dd', parse_line(tokens)));
      } else if (t.name == 'NEW_LINE') {
        tokens.shift();
        if (tokens.length && tokens[0].name != 'DEFINITION' && tokens[0].name != 'INDENT') {
          break;
        }
      } else if (t.name == 'INDENT') {
        tokens.shift();
        if (t.content.length > initial_indent) {
          if (tokens.length && tokens[0].name != 'DEFINITION') {
            var line = parse_line(tokens);
            dl.content[dl.content.length-1].concat(line);
          }
        }
      } else {
        break;
      }
    }
    return [dl];
  };


  var parse_quote = function (tokens) {
    var quote = new Node('blockquote');
    var new_tokens = [];

    var handle_quote = function (token){
      // Strip a single > off of a RIGHT_ANGLE token, effectively decreasing the quoting level
      var new_angle = token.content.replace(/^>\s*/, '').strip();
      if (new_angle.length) {
        new_tokens.push(new Token('RIGHT_ANGLE', new_angle));
      }
    };

    handle_quote(tokens.shift());

    while (tokens.length) {
      if (tokens[0].name == 'NEW_LINE') {
        new_tokens.push(tokens.shift());
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
          collect.push(new Node('br'));
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
      if (t.name == 'NEW_LINE' || t.name == 'INDENT') {
        tokens.shift();
        if (tokens.length && tokens[0].name == 'NEW_LINE') {
          tokens.shift();
          break;
        } else if (tokens.length && (tokens[0].name == 'RIGHT_ANGLE' || tokens[0].name == 'DEFINITION' || is_list_token(tokens[0]))) {
          if (t.name == 'INDENT') {
            tokens.unshift(t);
          }
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
    var t;
    while (tokens.length) {
      t = tokens[0];
      if (t.name == 'NEW_LINE') {
        tokens.shift();
        continue;
      }

      if (t.name == 'INDENT') {
        if (tokens.length == 1) {
          break;
        }
        t = tokens[1];
      }

      if (t.name == 'RIGHT_ANGLE') {
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
