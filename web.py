#!/usr/bin/env python
import urllib
import traceback
import StringIO
import smtplib
from mod_python import apache

from PottyMouth import PottyMouth
pm = PottyMouth(url_check_domains=('devsuki.com', 'www.devsuki.com'),
                allow_media=True)

page_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <body>
  %s
  </body>
</html>
"""


def make_page(request):
    output_string = ""
    args = request.args
    if args is not None:
        args = urllib.unquote(args)
        args = args.decode('utf8')
        args = args[:1000]
        p_nodes = pm.parse(args)
        for p in p_nodes:
            output_string += str(p)
    page = page_template % output_string
    return page


def handler(request):
    request.send_http_header()

    try:
        page = make_page(request)
        request.content_type = 'text/html'
        request.write(page)
    except:
        fake_file = StringIO.StringIO()
        traceback.print_exc(file=fake_file)
        error_str = fake_file.getvalue()
        fake_file.close()

        try:
            smtp = smtplib.SMTP('localhost')
            addr = 'matt-pottymouth@theory.org'
            smtp.sendmail(addr, addr, error_str)
            smtp.quit()
        except smtplib.SMTPException:
            pass
        
        request.content_type = 'text/plain'
        request.write(error_str)
    
    return apache.OK
