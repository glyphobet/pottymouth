var pottymouth = new (function () {
  var url_check_domains = new RegExp('(' + ['www.mysite.com', 'mysite.com'].join(')|(') + ')', 'i');
  var url_white_lists = [ /https?:\/\/www\.mysite\.com\/allowed\/url\?id=\d+/, ];
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


  var Token = function(name, content) {
     this.name = name;
     this.content = content;
     this.add = function (more) {
       this.content += more;
     }
     this.toString = function () {
       return this.content;
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
            if (found_tokens && found_tokens[found_tokens.length-1].name == 'TEXT') {
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


  var Line = function () {
    this.content = [];
    this.depth = 0;
    this.length = 0;
    this.bool = function () {
      return !! this.content.length;
    }
    this.push = function (item) {
      this.content.push(item);
      this.length = this.content.length;
    }
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
    this.content = [];
    this.attributes = new Attributes();
    this.push = function (item) {
      return this.content.push(item);
    };
    this.extend = function (items) {
      for (var i in items) {
        this.content.push(items[i]);
      }
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
        return '<' + this.name + this.attribute_string() + ' />';
      } else {
        var open = '<' + this.name + this.attribute_string() + '>';
        var close = '</' + this.name + '>';

        var c = ''
        for (var i in this.content) {
          c += this.content[i].toString() + '\n';
        }
        c = c.replace(/^[ ]+|[ ]$/g, '');
        c = c.replace(/\n+$/g, '');
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


  var _find_blocks = function(tokens) {
        var finished = [];

        var current_line = new Line();

        var stack = [];

        var old_depth = 0;

        for (var ti in tokens) {
            var t = tokens[ti];

            if (t.name == 'NEW_LINE') {
                console.debug('found a NEW_LINE; current line is ' + current_line.bool());
                if (current_line.bool()) {
                    if (current_line.depth == 0 && old_depth != 0) {
                        // figure out whether we're closing >> or * here and collapse the stack accordingly
                        console.debug('\tneed to collapse the stack by' + old_depth);
                        var top = undefined;
                        for (var i=0; i<old_depth; i++) {
                            if (stack.length && stack[stack.length-1].name == 'p') {
                                top = stack.pop();
                            }
                            if (stack.length && stack[stack.length-1].name == 'blockquote') {
                                top = stack.pop();
                            }
                        }

                        if (! stack.length) {
                            if (top) {
                                finished.push(top);
                            }
                            stack.push(new Node('p'));
                        }
                        console.debug('\tclosing out the stack')
                        old_depth = 0
                    }
                    console.debug('\tappending line to top of stack');
                    if (! stack.length) {
                        stack.push(new Node('p'));
                    }
                    stack[stack.length-1].push(current_line);
                    console.debug('\tcurrent line is now', current_line.bool());
                    current_line = new Line();

                } else if (stack.length) {
                    if (stack[stack.length-1].name == 'p' || stack[stack.length-1].name == 'li' || stack[stack.length-1].name == 'dd') {
                        var top = stack.pop(); // the p, li or dd
                        console.debug('\tpopped off because saw a blank line')

                        while (stack.length) {
                            if (stack[stack.length-1].name == 'blockquote' || stack[stack.length-1].name == 'ul' || stack[stack.length-1].name == 'ol' || stack[stack.length-1].name == 'li' || stack[stack.length-1].name == 'dl') {
                                var top = stack.pop();
                            } else {
                                break;
                            }
                        }
                        if (! stack.length) {
                            finished.push(top);
                        }
                    }
                }
            } else if (! current_line.bool() && (t.name == 'HASH' || t.name == 'NUMBERED' || t.name == 'ITEMSTAR' || t.name == 'BULLET' || t.name == 'DASH')) {
                if (stack.length && stack[stack.length-1].name == 'p') {
                    var top = stack.pop();
                    if (current_line.depth < old_depth) {
                        // pop off <blockquote> and <li> or <p> so we can apppend the new <li> in the right node
                        for (var i=0; i<old_depth-current_line.depth; i++) {
                            top = stack.pop(); // the <blockquote>
                            top = stack.pop(); // the previous <li> or <p>
                        }
                    }
                    if (! stack.length) {
                        finished.push(top);
                    }
                }

                if (stack.length && stack[stack.length-1].name == 'li') {
                    stack.pop(); // the previous li
                } else if (stack.length && (stack[stack.length-1].name == 'ul' || stack[stack.length-1].name == 'ol')) {
                    ; // pass
                } else {
                    if (t.name == 'HASH' || t.name == 'NUMBERED') {
                        var newl = new Node('ol');
                    } else if (t.name == 'ITEMSTAR' || t.name == 'BULLET' || t.name == 'DASH') {
                        var newl = new Node('ul');
                    }
                    if (stack.length) {
                        stack[stack.length-1].push(newl);
                    }
                    stack.push(newl)
                }
                var newli = new Node('li');
                stack[stack.length-1].push(newli);
                stack.push(newli);

            } else if (t.name == 'DEFINITION' && ! current_line.bool()) {
                if (stack.length && stack[stack.length-1].name == 'p') {
                    var top = stack.pop();
                    if (current_line.depth < old_depth) {
                        // pop off <blockquote> and <li> or <p> so we can apppend the new <li> in the right node
                        for (var i=0; i<old_depth-current_line.depth; i++) {
                            top = stack.pop(); // the <blockquote>
                            top = stack.pop(); // the previous <li> or <p>
                        }
                    }
                    if (! stack.length) {
                        finished.push(top);
                    }
                }

                if (stack.length && stack[stack.length-1].name == 'dd') {
                    stack.pop(); // the previous dd
                } else if (stack.length && stack[stack.length-1].name == ('dl')) {
                    ; // pass
                } else {
                    var newdl = new Node('dl');
                    if (stack.length) {
                        stack[stack.length-1].push(newdl);
                    }
                    stack.push(newdl);
                }

                var l = new Line();
                l.push(t);
                var newdt = new Node('dt');
                newdt.push(l);
                stack[stack.length-1].push(newdt);
                var newdd = new Node('dd');
                stack[stack.length-1].push(newdd);
                stack.push(newdd);

            } else if (t.name == 'RIGHT_ANGLE' && ! current_line.bool()) {
                var new_depth = t.content.match(/>/g).length;
                var old_depth = 0;

                for (var i=stack.length-1; i>=0; i--) {
                    var n = stack[i];
                    if (n.name == 'blockquote') {
                        old_depth += 1
                    } else if (n.name == 'p' || n.name == 'li' || n.name == 'ul' || n.name == 'ol' || n.name == 'dt' || n.name == 'dd' || n.name == 'dl') {
                        ; // pass
                    } else {
                        break;
                    }
                }

                current_line.depth = new_depth;
                if (new_depth == old_depth) {
                    // same level, do nothing
                    console.debug('\tsame level, do nothing');
                } else if (new_depth > old_depth) {
                    // current_line is empty, so we just make some new nodes
                    for (var i=0; i<new_depth - old_depth; i++) {
                        if (! stack.length) {
                            var newp = new Node('p');
                            stack.push(newp);
                        } else if (stack[stack.length-1].name != 'p' && stack[stack.length-1].name != 'li') {
                            var newp = Node('p')
                            stack[stack.length-1].push(newp);
                            stack.push(newp);
                        }
                        var newq = new Node('blockquote');
                        stack[stack.length-1].push(newq);
                        stack.push(newq);
                    }

                } else if (new_depth < old_depth) {
                    // current line is empty, so we just pop off the existing nodes
                    for (var i=0; i<new_depth - old_depth; i++) {
                        stack.pop() // the p
                        stack.pop() // the blockquote
                    }
                }
                old_depth = new_depth

            } else {
                if (stack.length && stack[stack.length-1].name == 'blockquote') {
                    var newp = new Node('p');
                    stack[stack.length-1].push(newp);
                    stack.push(newp);
                }

                if (t.name == 'URL') {
                    _handle_url(t.content, current_line);
                } else if (t.name == 'YOUTUBE') {
                    _handle_youtube(t.content, current_line);
                } else if (t.name == 'IMAGE') {
                    _handle_image(t.content, current_line);
                } else if (t.name == 'EMAIL') {
                    _handle_email(t.content, current_line);
                } else if (current_line.bool() && t.content.replace(/^[\t\n\r]+|[\t\n\r]+$/g, '')) {
                    current_line.push(t);
                    console.debug('\tadding (possibly empty space) text token to current line');
                } else if (t.content.replace(/^[ \t\n\r]+|[ \t\n\r]+$/g, '')) {
                    current_line.push(t);
                    console.debug('\tadding non-empty text token to current line');
                }
            } // closes switch on token name
        } // closes for t in tokens

        if (current_line.bool()) {
          if (! stack.length) {
            stack.push(new Node('p'));
          }
          stack[stack.length-1].push(current_line);
        }

        while (stack.length) {
          var top = stack.pop();
          var top_in_stack = false;
          if (stack.length) {
            for (var i in stack[stack.length-1].content) {
              if (top == stack[stack.length-1].content[i]) {
                top_in_stack = true;
                break;
              }
            }
          }
          if (stack.length && top_in_stack) {
            ; // pass
          } else{
            finished.push(top);
          }
        }
        return finished;
  };


  var _handle_email = function (email, current_line) {
      current_line.push( new EmailNode(email) );
  };


  var _handle_url = function (anchor, current_line) {
      if (! anchor.match(protocol_pattern)) {
        anchor = 'http://' + anchor;
      }

      if (this.url_check_domains && anchor.match(this.url_check_domains)) {
          console.debug('\tchecking urls for this domain');
          for (var i in this.url_white_lists) {
              var w = this.url_white_lists[i];
              console.debug('\t\tchecking against', w);
              if (anchor.match(w)) {
                  console.debug('\t\tmatches the white lists')
                  var a = _handle_link(anchor, true);
                  current_line.push(a);
                  return;
              }
          }
          console.debug('\tdidn\'t match any white lists, making text');
          current_line.push(anchor);
      } else {
          var a = _handle_link(anchor, false);
          current_line.push(a);
      }
  };


  var _handle_link = function (anchor, internal) {
    return new LinkNode(anchor, internal);
  };


  var _handle_youtube = function (t, current_line) {
    var ytn = new YouTubeNode(t);
    current_line.push(ytn);
  };


  var _handle_image = function (t, current_line) {
      var i = new ImageNode(t)
      current_line.push(i)
  };


  var _create_spans = function (sub_line) {
      var new_sub_line = [];
      var current_span = undefined;

      for (i in sub_line) {
          var t = sub_line[i];
          if (t instanceof Node) {
              if (current_span) {
                  new_sub_line.push(current_span);
                  current_span = undefined;
              }
              new_sub_line.push(t);
          } else {
              if (! current_span) {
                  current_span = new Node('span');
              }
              current_span.push(t);
          }
      }

      if (current_span) {
          new_sub_line.push(current_span);
      }

      return new_sub_line;
  }


  var _parse_line = function (line) {
      // Parse bold and italic and other balanced items
      var stack = [];
      var finished = [];

      var last_bold_idx = -1;
      var last_ital_idx = -1;

      var leading_space_pad = false;

      var _reduce_balanced = function(name, last_idx, stack) {
          var n = new Node(name);
          // console.debug(stack.slice(last_idx+1));
          var sub_line = _create_spans( stack.slice(last_idx+1) );

          var sl = stack.length;
          for (var i=last_idx; i<sl; i++) {
              stack.pop();
          }

          if (sub_line.length) { // BUG not sure here
              n.extend(sub_line);
              stack.push(n);
          }
      };

      for (var i in line.content) {
          var p = '';
          for (k in stack) {
            p += stack[k].name + '{'+ stack[k].content +'}, '
          }
          var t = line.content[i];
          if (t instanceof URLNode) {
              // URL nodes can go inside balanced syntax
              stack.push(t)
          } else if (t instanceof Node) {
              if (stack.length) {
                  // reduce stack, close out dangling * and _
                  var sub_line = _create_spans(stack);
                  for (var j in sub_line) {
                    finished.push(sub_line[j]);
                  }
                  last_bold_idx = -1;
                  last_ital_idx = -1;
                  stack = [];
              }
              // add node to new_line
              finished.push(t);
          } else if (t instanceof Token) {
              if (t.name == 'UNDERSCORE') {
                  if (last_ital_idx == -1) {
                      last_ital_idx = stack.length;
                      stack.push(t);
                  } else {
                      _reduce_balanced('i', last_ital_idx, stack);
                      if (last_ital_idx <= last_bold_idx) {
                          last_bold_idx = -1;
                      }
                      last_ital_idx = -1;
                  }
              } else if (t.name == 'STAR' || t.name == 'ITEMSTAR') {
                  if (t.name == 'ITEMSTAR') {
                      // Because ITEMSTAR gobbles up following space, we have to space-pad the next (text) token
                      leading_space_pad = true;
                  }
                  if (last_bold_idx == -1) {
                      last_bold_idx = stack.length;
                      stack.push(t);
                  } else {
                      _reduce_balanced('b', last_bold_idx, stack);
                      if (last_bold_idx <= last_ital_idx) {
                          last_ital_idx = -1;
                      }
                      last_bold_idx = -1;
                  }
              } else {
                  if (leading_space_pad) {
                      // Because ITEMSTAR gobbled up the following space, we have to space-pad this (text) token
                      t = new Token(t.name, ' '+t);
                      leading_space_pad = false;
                  }
                  stack.push(t);
              }
          } else {
              console.debug(typeof(t) + ':' + t);
          }
      }

      if (stack.length) {
          // reduce stack, close out dangling * and _
          var sub_line = _create_spans(stack);
          for (var j in sub_line) {
            finished.push(sub_line[j]);
          }
      }

      return finished;
  };


  var _parse_block = function (block) {
      var new_block = new Node(block.name);
      var current_line = undefined;

      var ppll = -1; // previous previous line length
      var pll  = -1; // previous line length

      for (i in block.content) {
          var item = block.content[i];
          // collapse lines together into single lines
          if (item instanceof Node) {
              if (current_line) {
                  // all these lines should be dealt with together
                  var parsed_line = _parse_line(current_line);
                  new_block.extend(parsed_line);
              }
              var parsed_block = _parse_block(item);
              new_block.push(parsed_block);
              current_line = undefined;
              ppll = -1;
              pll  = -1;

          } else if (item instanceof Line) {
              if (current_line) {
                  if (item.length < this.short_line_length) {
                      // Identify short lines
                      if (0 < pll && pll < this.short_line_length) {
                          current_line.push(new Node('BR'));
                      } else if ((block.length > i+1                       ) && // still items on the stack
                                 (block[i+1] instanceof Line               ) && // next item is a line
                                 (0 < block[i+1].length && block[i+1].length < this.short_line_length) ){ // next line is short
                          // the next line is short and so is this one
                          current_line.push(new Node('BR'));
                      }
                  } else if (0 < pll && pll < this.short_line_length && 0 < ppll && ppll < this.short_line_length) {
                      // long line at the end of a sequence of short lines
                      current_line.push(new Node('BR'));
                  }

                  for (var j in item.content) {
                    current_line.push(item.content[j]);
                  }
                  ppll = pll;
                  pll = item.length;
              } else {
                  current_line = item;
                  ppll = -1;
                  pll = item.length;
              }
          } else {
              console.debug("Not expecting item of type: " + typeof(item) + " in block:" + item);
          }
      }

      if (current_line) {
          var parsed_line = _parse_line(current_line);
          new_block.extend(parsed_line);
      }

      return new_block
  };


  var pre_replace = function (s) {
    for (var i in replace_list) {
      var r = replace_list[i];
      s = s.replace(r.pattern, r.replace);
    }
    return s;
  }


  this.parse = function (s) {
    s = pre_replace(s);
    var tokens = tokenize(s);
    var blocks = _find_blocks(tokens);
    var parsed_blocks = new Node('div')
    for (var i in blocks) {
        var nb = _parse_block(blocks[i]);
        parsed_blocks.push(nb);
    }
    return parsed_blocks;
  }


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
  }

})();
