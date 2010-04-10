#!/usr/bin/env ruby1.9
if RUBY_VERSION < '1.9'
  puts "Ruby 1.9 or greater required. You are using Ruby #{RUBY_VERSION}."
  exit()
end
$KCODE = 'UTF-8'

module PottyMouth

  ShortLineLength = 50

  class TokenMatcher
    attr_reader :replace, :name

    def initialize(name, pattern, replace=nil)
      @name = name
      @pattern = pattern
      @replace = replace
    end


    def match(string)
      @pattern.match(string)
    end

  end

  ProtocolPattern = /^\w+:\/\//i

  domain_pattern = '([-\w]+\.)+\w\w+'

  base_uri_pattern = ('(('                                    + 
		      '(https?|webcal|feed|ftp|news|nntp)://' + # protocol
		      '([-\w]+(:[-\w]+)?@)?'                  + # authentication
		      ')|www\.)'                              + # or just www.
		      domain_pattern                          + # domain
		      '(/[-\w$\.+!*\'(),;:@%&=?/~#]*)?'       ) # path

  uri_end_punctuation = '(?<![\]\.}>\)\s,?!;:"\'])'  # end punctuation

  URIPattern = Regexp.new('^(' + base_uri_pattern + uri_end_punctuation + ')', 
			  Regexp::IGNORECASE)

  EmailPattern = Regexp.new('^([^()<>@,;:"\[\]\s]+@' + domain_pattern + ')')

  ImagePattern = Regexp.new('^(' + base_uri_pattern + 
			    '\.(jpe?g|png|gif)' + uri_end_punctuation + ')', 
			    Regexp::IGNORECASE)

  # YouTubePattern matches:
  #  http://www.youtube.com/watch?v=KKTDRqQtPO8 and
  #  http://www.youtube.com/v/KKTDRqQtPO8       and
  #  http://youtube.com/watch?v=KKTDRqQtPO8     and
  #  http://youtube.com/v/KKTDRqQtPO8
  YouTubePattern = /^(http:\/\/(?:www\.)?youtube.com\/(?:watch\?)?v=?\/?([\w\-]{11}))/i


  TokenList = [
    TokenMatcher.new(:NEW_LINE    , /^(\r?\n)/), #fuck you, Microsoft!
    TokenMatcher.new(:YOUTUBE     , YouTubePattern),
    TokenMatcher.new(:IMAGE       , ImagePattern  ),
    TokenMatcher.new(:URL         , URIPattern    ),
    TokenMatcher.new(:EMAIL       , EmailPattern  ),

    TokenMatcher.new(:HASH        , /^([\t ]*#[\t ]+)/     ),
    TokenMatcher.new(:DASH        , /^([\t ]*-[\t ]+)/     ),
    TokenMatcher.new(:NUMBERDOT   , /^([\t ]*\d+\.[\t ]+)/ ),
    TokenMatcher.new(:ITEMSTAR    , /^([\t ]*\*[\t ]+)/    ),
    TokenMatcher.new(:BULLET      , /^([\t ]*•[\t ]+)/     ),

    TokenMatcher.new(:UNDERSCORE  , /^(_)/ ),
    TokenMatcher.new(:STAR        , /^(\*)/),

    TokenMatcher.new(:RIGHT_ANGLE , /^(>[\t ]*(?:>[\t ]*)*)/),

    # The following are simple, context-independent replacement tokens
    TokenMatcher.new(:EMDASH, /^(--)/, '—'),
    # No way to reliably distinguish Endash from Hyphen, Dash & Minus, 
    # so we don't.  See: http://www.alistapart.com/articles/emen/

    TokenMatcher.new(:ELLIPSIS , /^(\.\.\.)/, '…'),
    #TokenMatcher.new(:SMILEY  , /^(:\))/   , '?'), # smiley face, not in HTML 4.01, doesn't work in IE
  ]


  # The "Replacers" are context sensitive replacements, therefore they
  # must be applied in-line to the string as a whole before tokenizing.
  # Another option would be to keep track of previous context when
  # applying tokens.
  class Replacer

    def initialize(pattern, replace)
      @pattern = pattern
      @replace = replace
    end


    def sub(string)
      return string.gsub!(@pattern, @replace)
    end

  end


  ReplaceList = [
    Replacer.new(/(``)/, '“'),
    Replacer.new(/('')/, '”'),

    # First we look for inter-word " and ' 
    Replacer.new(/(\b"\b)/, '"'), #' double prime
    Replacer.new(/(\b'\b)/, '’'),  #' apostrophe
    # Then we look for opening or closing " and ' 
    Replacer.new(/(\b"\B)/, '”'), #" close double quote
    Replacer.new(/(\B"\b)/, '“'), #" open double quote
    Replacer.new(/(\b'\B)/, '’'), #' close single quote
    Replacer.new(/(\B'\b)/, '‘'), #' open double quote

    # Then we look for space-padded opening or closing " and ' 
    Replacer.new(/(")(\s)/, '”\2'), #" close single quote
    Replacer.new(/(\s)(")/, '\1“'), #" open double quote
    Replacer.new(/(')(\s)/, '’\2'), #' close single quote
    Replacer.new(/(\s)(')/, '\1‘'), #' open double quote

    # Then we gobble up stand-alone ones
    Replacer.new(/(`)/, '‘'), #`
    #Replacer.new(/(")/, '”'),
    #Replacer.new(/(')/, '’'),
  ]


  class Token < String
    attr_reader :name

    def initialize(name, obj='')
      super(obj)
      @name = name
    end


    def to_s 
      # For debugging
      super() + '{' + @name.to_s + '}'
    end


    def +(extra)
      Token.new(@name, super(extra))
    end

  end


  def Token::escape(string)
    string.gsub!('&', '&amp;')
    string.gsub!('<', '&lt;' )
    string.gsub!('>', '&gt;' )
    # I prefer Python's .encode('ascii', 'xmlcharrefreplace'). 
    # Call me traditional.
    string.unpack("U*").collect {|s| (s > 127 ? "&##{s};" : s.chr) }.join("")
  end


  class Line < Array
    attr_accessor :depth

    def initialize(obj=[])
      super(obj)
      @depth = 0
    end


    def to_s
      # For debugging:
      'Line[' + self.join('') + '(' + @depth.to_s + ')]'
    end


    def length
      inject(0) do |sum, x|
	sum += x.length
      end
    end

  end



  class Node < Array
    attr_reader :name

    def initialize(name, children=[], hashlist={})
      super(children)
      @name = name.downcase
      @attributes = hashlist
    end


    def node_children?
      each do |n|
	return true if n.is_a? Node
      end
      return false
    end


    def to_str
      if @name == :br # hr too
	return "<#{@name} />"
      else
	content = (map {|x| x.to_str}).join("\n")
	content.gsub!("\n", "\n  ")

	if node_children?
	  return "<#{@name}#{attribute_string()}>\n  #{content}\n</#{@name}>"
	else
	  return "<#{@name}#{attribute_string()}>#{content}</#{@name}>"
	end
      end
    end


    protected 
    def attribute_string
      x = ""  
      if @attributes
	@attributes.each {|k,v| x+=" #{k}=\"#{v}\""}
      end
      x
    end

  end



  class URLNode < Node

    attr_reader :internal

    def initialize(content, internal=false)
      super(:a, [content,])
      @internal = internal
    end

  end



  class LinkNode < URLNode

    def to_str
      class_attribute = @internal ? '' : ' class="external"'

      displayed_url = self[0]
      if self[0...7] == 'http://'
	displayed_url = self[0][7..-1]
      end

      return "<#{@name} href=\"#{Token.escape(self[0])}\"#{class_attribute}>#{Token.escape(displayed_url)}</#{@name}>"
    end

  end



  class EmailNode < URLNode

    def to_str
      return "<#{@name} href=\"mailto:#{Token.escape(self[0])}\">#{Token.escape(self[0])}</#{@name}>"
    end

  end



  class ImageNode < Node

    def initialize(content='')
      super(:img, [content,])
    end


    def to_str
      return "<#{@name} src=\"#{Token.escape(self[0])}\"/>"
    end

  end



  class YouTubeNode < Node

    def initialize(url)
      super(:object, [], {:width=>'425',:height=>'350'})

      ytid = YouTubePattern.match(url)[2]
      url = 'http://www.youtube.com/v/'+ytid

      push(Node.new(:param, [], {:name=>'movie', :value=>url          }))
      push(Node.new(:param, [], {:name=>'wmode', :value=>'transparent'}))
      push(Node.new(:embed, [], {
		      :type  =>'application/x-shockwave-flash',
		      :wmode =>'transparent',
		      :src   =>url,
		      :width =>'425',
		      :height=>'350',
		    }))
    end

  end



  class PottyMouth

    def initialize(url_check_domains=[], url_white_lists=[], allow_media=false)
      @url_check_domain = nil
      if url_check_domains and url_check_domains.length > 0
	@url_check_domain = Regexp.new("(\w:+//)?((" + 
				       url_check_domains.join(")|(") + 
				       "))",
				       Regexp::IGNORECASE)
      end
      @url_white_lists = url_white_lists
      @allow_media = allow_media
    end


    def to_s
      # For debugging
      s = "allow_media=#{@allow_media};"
      if @url_check_domain
	s += "\nchecking: #{@url_check_domain.source}\nallowed URLs:\n\t#{(@url_white_lists.collect {|w| w.source}).join('\n\t')}"
      else
	s += "\nWARNING: hyperlinking ALL URLs."
      end
      s
    end


    protected 
    def debug(*strings)
      puts strings.join(' ')
    end


    def tokenize(string)
      p = 0
      found_tokens = []
      unmatched_collection = ''
      while p < string.length
	#debug(string[p..-1])
	found_token = false
	for tm in TokenList
	  m = tm.match(string[p..-1])
	  if m and m.offset(0)[0] == 0
	    # GIANT HACK ^^^^^^^^^^^^^ Ruby regexes are always in
	    # multiline mode, so you have to do that to ensure you're
	    # matching at the beginning. WTF.
	    found_token = true
	    content = m[0]
	    #debug("Found ", tm.name, " at ", p, ":", content, " against:", string[p..-1])
	    p += content.length

	    if tm.replace != nil 
	      unmatched_collection += tm.replace
	      break
	    end

	    if unmatched_collection.length > 0
	      # BUG what if this isn't unicode? the python version decodes from UTF-8
	      found_tokens.push(Token.new(:TEXT, unmatched_collection)) 
	      #debug("adding token " + found_tokens[-1].to_s)
	    end

	    unmatched_collection = ''

	    if tm.name == :NEW_LINE
	      if found_tokens.length > 0 and found_tokens[-1].name == :TEXT
		found_tokens[-1] += ' '
	      end
	      content=' '
	    end

	    found_tokens.push(Token.new(tm.name, content))
	    #debug("adding token " + found_tokens[-1].to_s)
	    break
	  end
	end

	if not found_token
	  # Pull one character off the string and continue looking for tokens
	  unmatched_collection += string[p]
	  #debug(unmatched_collection)
	  p += 1
	end
      end

      if unmatched_collection.length > 0
	found_tokens.push(Token.new(:TEXT, unmatched_collection))
      end

      #debug(found_tokens)
      return found_tokens
    end


    def find_blocks(tokens)
      finished = []

      current_line = Line.new()

      stack = []

      old_depth = 0

      for t in tokens
	#debug(t)

	if t.name == :NEW_LINE
	  if current_line.length > 0
	    #debug("current_line.depth ", current_line.depth, "; old_depth ", old_depth)
	    if current_line.depth == 0 and old_depth != 0
	      # figure out whether we're closing >> or * here and collapse the stack accordingly
	      #debug('need to collapse the stack by' + old_depth.to_s)
	      top = nil
	      for i in 0...old_depth
		if stack.length > 0 and stack[-1].name == :p
		  top = stack.pop()
		end
		if stack.length > 0 and stack[-1].name == :blockquote
		  top = stack.pop()
		end
	      end

	      if stack.length == 0
		if top != nil
		  finished.push(top)
		end
		stack.push(Node.new(:p))
		#debug("added ", stack[-1].to_str)
	      end
	      #debug('closing out the stack')
	      old_depth = 0
	    end
	    #debug('appending line to top of stack')
	    if stack.length == 0
	      stack.push(Node.new(:p))
	      #debug("added ", stack[-1].to_str)
	    end
	    stack[-1].push( current_line )
	    current_line = Line.new()

	  elsif stack.length > 0
	    if [:p,:li].index(stack[-1].name)
	      top = stack.pop() # the p or li
	      #debug('\tpopped off because saw a blank line')

	      while stack.length > 0
		if [:blockquote,:ul,:ol,:li].index(stack[-1].name)
		  top = stack.pop()
		else
		  break
		end
	      end
	      if stack.length == 0
		finished.push(top)
	      end
	    end
	  end
	elsif [:HASH,:NUMBERDOT,:ITEMSTAR,:BULLET,:DASH].index(t.name) and current_line.length == 0
	  if stack.length > 0 and stack[-1].name == :p
	    top = stack.pop()
	    if current_line.depth < old_depth
	      # pop off <blockquote> and <li> or <p>so we can apppend the new <li> in the right node
	      for i in 0...(old_depth - current_line.depth)
		top = stack.pop() # the <blockquote>
		top = stack.pop() # the previous <li> or <p>
	      end
	    end
	    if stack.length == 0
	      finished.push(top)
	    end
	  end

	  if stack.length > 0 and stack[-1].name == :li
	    stack.pop() # the previous li
	  elsif stack.length > 0 and [:ul,:ol].index(stack[-1].name)
	    # do nothing
	  else
	    if [:HASH,:NUMBERDOT].index(t.name)
	      newl = Node.new(:ol)
	    elsif [:ITEMSTAR,:BULLET,:DASH].index(t.name)
	      newl = Node.new(:ul)
	    end
	    if stack.length > 0
	      stack[-1].push(newl)
	    end
	    stack.push(newl)
	    #debug("added ", stack[-1].to_str)
	  end

	  newli = Node.new(:li)
	  stack[-1].push(newli)
	  stack.push(newli)
	  #debug("added ", stack[-1].to_str)

	elsif t.name == :RIGHT_ANGLE and current_line.length == 0
	  new_depth = t.count('>')
	  old_depth = 0

	  for n in stack.reverse
	    if n.name == :blockquote
	      old_depth += 1
	    elsif [:p,:li,:ul,:ol].index(n.name)
	      # do nothing
	    else
	      break
	    end
	  end
	  #debug("nd:", new_depth, "; od:", old_depth)
	  current_line.depth = new_depth
	  if new_depth == old_depth
	    # same level, do nothing
	    #debug('\tsame level, do nothing')

	  elsif new_depth > old_depth
	    # current_line is empty, so we just make some new nodes
	    for i in 0...new_depth - old_depth
	      if stack.length == 0
		newp = Node.new(:p)
		stack.push(newp)
		#debug("added ", stack[-1].to_str)
	      elsif not [:p,:li].index(stack[-1].name)
		newp = Node.new(:p)
		stack[-1].push(newp)
		stack.push(newp)
		#debug("added ", stack[-1].to_str)
	      end
	      newq = Node.new(:blockquote)
	      stack[-1].push(newq)
	      stack.push(newq)
	      #debug("added ", stack[-1].to_str)
	    end

	  elsif new_depth < old_depth
	    # current line is empty, so we just pop off the existing nodes
	    for i in 0...old_depth - new_depth
	      stack.pop() # the p
	      stack.pop() # the blockquote
	    end
	  end
	  old_depth = new_depth

	else
	  if stack.length > 0 and stack[-1].name == :blockquote
	    newp = Node.new(:p)
	    stack[-1].push(newp)
	    stack.push(newp)
	    #debug("added ", stack[-1].to_str)
	  end

	  if t.name == :URL
	    handle_url(t, current_line)
	  elsif t.name == :YOUTUBE
	    if @allow_media
	      handle_youtube(t, current_line)
	    else
	      handle_url(t, current_line)
	    end
	  elsif t.name == :IMAGE
	    if @allow_media
	      handle_image(t, current_line)
	    else
	      handle_url(t, current_line)
	    end
	  elsif t.name == :EMAIL
	    handle_email(t, current_line)
	  elsif current_line.length > 0 and t.strip.length > 0
	    #debug('\tadding (possibly empty space) text token to current line')
	    current_line.push(t)
	  elsif t.strip().length > 0
	    #debug('\tadding non-empty text token to current line')
	    current_line.push(t)
	  end
	end
      end

      if current_line.length > 0
	if stack.length == 0
	  stack.push(Node.new(:p))
	  #debug("added ", stack[-1].to_str)
	end
	stack[-1].push(current_line)
      end

      while stack.length > 0
	top = stack.pop()
	if stack.length > 0 and stack[-1].index(top)
	  # skip
	else
	  finished.push(top)
	end
      end
      
      return finished
    end


    def handle_email(email, current_line)
      current_line.push(EmailNode.new(email))
    end


    def handle_url(anchor, current_line)
      if not ProtocolPattern.match(anchor)
	anchor = Token.new(anchor.name, 'http://' + anchor)
      end

      if @url_check_domain and @url_check_domain.match(anchor)
	#debug(anchor + " in check domains")
	for w in @url_white_lists
	  #debug("checking " + anchor + " against " + w.source)
	  if w.match(anchor)
	    a = handle_link(anchor, internal=true)
	    current_line.push(a)
	    return
	  end
	end
	#debug(anchor + " did not match any URL whitelists")
	current_line.push(anchor)
      else
	a = handle_link(anchor, internal=false)
	current_line.push(a)
      end
    end


    def handle_link(anchor, internal=false)
      return LinkNode.new(anchor, internal)
    end


    def handle_youtube(youtube, current_line)
      ytn = YouTubeNode.new(youtube)
      current_line.push(ytn)
    end


    def handle_image(image, current_line)
      i = ImageNode.new(image)
      current_line.push(i)
    end


    def create_spans(sub_line)
      new_sub_line = []
      current_span = nil
      sub_line.each do |t|
	if t.is_a? Node
	  if current_span != nil
	    new_sub_line.push(current_span)
	    current_span = nil
	  end
	  new_sub_line.push(t)
	else
	  if current_span == nil
	    current_span = Node.new(:span)
	  end
	  et = Token.escape(t)
	  current_span.push(et)
	end
      end
      if current_span != nil
	new_sub_line.push(current_span)
      end

      return new_sub_line
    end


    def reduce_balanced(name, last_idx, stack)
      n = Node.new(name)
      sub_line = create_spans(stack[last_idx+1..-1])

      (last_idx...stack.length).each do |i|
	stack.pop()
      end

      if sub_line.length > 0
	n.push(*sub_line)
	stack.push(n)
      end
    end


    def parse_line(line)
      # Parse bold and italic and other balanced items
      stack = []
      finished = []
      
      last_bold_idx = -1
      last_ital_idx = -1

      leading_space_pad = false

      (0...line.length).each do |i|
	t = line[i]
	if t.is_a? URLNode
	  # URL nodes can go inside balanced syntax
	  #debug("pushing", t.to_s, "onto", stack.length)
	  stack.push(t)
	elsif t.is_a? Node
	  if stack.length > 0
	    # reduce stack, close out dangling * and _
	    sub_line = create_spans(stack)
	    finished += sub_line
	    last_bold_idx = -1
	    last_ital_idx = -1
	    stack = []
	  end
	  # add node to new_line
	  #debug("appending ", t.to_s, " to ", finished.to_s)
	  finished.push(t)
	elsif t.is_a? Token
	  if t.name == :UNDERSCORE
	    if last_ital_idx == -1
	      last_ital_idx = stack.length
	      #debug("pushing", t.to_s, "onto", stack.to_s)
	      stack.push(t)
	    else
	      reduce_balanced(:i, last_ital_idx, stack)
	      if last_ital_idx <= last_bold_idx
		last_bold_idx = -1
	      end
	      last_ital_idx = -1
	    end
	  elsif [:STAR, :ITEMSTAR].index(t.name)
	    if t.name == :ITEMSTAR
	      # Because ITEMSTAR gobbles up following space, we have to space-pad the next (text) token
	      leading_space_pad = true
	    end
	    if last_bold_idx == -1
	      last_bold_idx = stack.length
	      #debug("pushing", t.to_s, "onto", stack.to_s)
	      stack.push(t)
	    else
	      reduce_balanced(:b, last_bold_idx, stack)
	      if last_bold_idx <= last_ital_idx
		last_ital_idx = -1
	      end
	      last_bold_idx = -1
	    end
	  else
	    if leading_space_pad
	      # Because ITEMSTAR gobbled up the following space, we have to space-pad this (text) token
	      t = Token.new(t.name, ' '+t)
	      leading_space_pad = false
	    end
	    #debug("pushing", t.to_s, "onto", stack.to_s)
	    stack.push(t)
	  end
	elsif t == nil
	  # skip it
	else
	  raise "Unknown object in Line: " + t.class.to_s + ':' + t.to_s
	end
      end

      if stack.length > 0
	# reduce stack, close out dangling * and _
	#debug("stack: ", stack.length)
	sub_line = create_spans(stack)
	#debug("sub_line: ", sub_line.length)
	finished += sub_line
      end
      #debug(finished.collect {|x| x.name })
      return finished
    end


    def parse_block(block)
      new_block = Node.new(block.name)
      current_line = nil

      ppll = -1 # previous previous line length
      pll  = -1 # previous line length

      (0...block.length).each do |i|
	item = block[i]
	# collapse lines together into single lines
	if item.is_a? Node
	  if current_line != nil
	    # all these lines should be dealt with together
	    parsed_line = parse_line(current_line)
	    new_block.push(*parsed_line)
	  end

	  parsed_block = parse_block(item)
	  new_block.push(parsed_block)
	  current_line = nil
	  ppll = -1
	  pll  = -1

	elsif item.is_a? Line
	  if current_line != nil
	    if item.length < ShortLineLength
	      # Identify short lines
	      if 0 < pll and pll < ShortLineLength
		current_line.push(Node.new(:br))
	      elsif (block.length > i+1                  and   # still items on the stack
		     block[i+1].is_a? Line               and   # next item is a line
		     0 < block[i+1].length and block[i+1].length < ShortLineLength) # next line is short
		# the next line is short and so is this one
		current_line.push(Node.new(:br))
	      end
	    elsif 0 < pll and pll < ShortLineLength and 0 < ppll and ppll < ShortLineLength
	      # long line at the end of a sequence of short lines
	      current_line.push(Node.new(:br))
	    end
	    current_line.push(*item)
	    ppll = pll
	    pll = item.length
	  else
	    current_line = item
	    ppll = -1
	    pll = item.length
	  end
	end
      end

      if current_line != nil
	parsed_line = parse_line(current_line)
	new_block.push(*parsed_line)
      end

      return new_block
    end


    def pre_replace(string)
      ReplaceList.each do |r|
	r.sub(string)
      end
    end


    public
    def parse(string)
      pre_replace(string)
      tokens = tokenize(string)
      blocks = find_blocks(tokens)
      parsed_blocks = Node.new(:div)
      blocks.each do |b|
	nb = parse_block(b)
	parsed_blocks.push(nb)
      end
      return parsed_blocks
    end

  end

end

if __FILE__ == $0
  pm = PottyMouth.new(url_check_domains=["www.mysite.com", "mysite.com"],
		      url_white_lists=[/https?:\/\/www\.mysite\.com\/allowed\/url\?id=\d+/,],
		      allow_media=true)

  puts pm.to_s
  while true
    puts "input (end with Ctrl-D)>>"
    text = $stdin.read
    next if not text

    blocks = pm.parse(text)
    puts blocks.to_str
    puts '=' * 70
  end
end
