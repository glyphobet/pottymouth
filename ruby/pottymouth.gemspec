Gem::Specification.new do |spec|
  spec.name = "PottyMouth"
  spec.version = "1.0.2.1"
  spec.homepage = "http://devsuki.com/pottymouth"
  spec.author = "Matt Chisholm"
  spec.email = "matt@mosuki.com"
  spec.summary = "transform unstructured, untrusted text to safe, valid XHTML"
  spec.description = <<-EOF
PottyMouth transforms completely unstructured and untrusted text to valid, nice-looking, completely safe XHTML.

PottyMouth is designed to handle input text from non-technical, potentially careless or malicious users. It produces HTML that is completely safe, programmatically and visually, to include on any web page. And you don't need to make your users read any instructions before they start typing. They don't even need to know that PottyMouth is being used.
EOF

  spec.files = ["PottyMouth.rb",]
  spec.test_file = "test.rb"
  spec.extra_rdoc_files = ['readme.html', 'LICENSE.txt']
  spec.required_ruby_version = '>= 1.9.0' 
end