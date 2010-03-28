$(document).ready(function (){
  test("PottyMouth basic tests", 2, function () {
    equals(true, true, "Testing is working");
    ok(pottymouth, "PottyMouth not found");
  });

  var p = pottymouth;
  p.expose_internals_for_tests();

  test("PottyMouth RegExp tests", 15, function () {
    ok( 'http://'.match(p.protocol_pattern), "protocol_pattern match");
    ok(! 'http//'.match(p.protocol_pattern), "protocol_pattern non-match");
    ok( 'google.de'.match(p.domain_pattern), "domain_pattern match");
    ok(! 'google.d'.match(p.domain_pattern), "domain_pattern non-match");

    ok('http://username:password@theory.org'.match(p.URI_pattern), "URI_pattern w/authentication");
    ok('www.theory.org'.match(p.URI_pattern), "URI_pattern www.");
    ok('http://username:password@theory.org/my/path'.match(p.URI_pattern), "URI_pattern w/authentication and path");
    ok('www.theory.org/py/math'.match(p.URI_pattern), "URI_pattern www. and path");

    ok('http://look.at/my?finger=middle&nail=clipped#cuticle'.match(p.URI_pattern), "URI_pattern w/ query parameters");

    ok('potty.mouth@theory.org'.match(p.email_pattern), "email pattern");
    ok('http://look.at/my/image.jpeg'.match(p.image_pattern), "image pattern");

    ok('http://www.youtube.com/watch?v=KKTDRqQtPO8'.match(p.youtube_pattern), "youtube pattern");
    ok('http://www.youtube.com/v/KKTDRqQtPO8'.match(p.youtube_pattern), "youtube pattern");
    ok('http://youtube.com/watch?v=KKTDRqQtPO8'.match(p.youtube_pattern), "youtube pattern");
    ok('http://youtube.com/v/KKTDRqQtPO8'.match(p.youtube_pattern), "youtube pattern");
  });

  test("PottyMouth replacer tests", 2, function () {
    equals(p.pre_replace('Foo "and" bar and ``baz\'\' or not.'), 'Foo &#8220;and&#8221; bar and &#8220;baz&#8221; or not.');
    equals(p.pre_replace('9\'13"and some arcseconds.'), '9&#8217;13&#34;and some arcseconds.');
  });

  test("PottyMouth tokenizer tests", 10, function () {
    var tstr = p.tokenize('A *BOLD* thing');
    equals(tstr[0].content, 'A ');
    equals(tstr[1].content, '*');
    equals(tstr[2].content, 'BOLD');
    equals(tstr[3].content, '* ');
    equals(tstr[4].content, 'thing');
    equals(tstr[0].name, 'TEXT');
    equals(tstr[1].name, 'STAR');
    equals(tstr[2].name, 'TEXT');
    equals(tstr[3].name, 'ITEMSTAR');
    equals(tstr[4].name, 'TEXT');
  })
})
