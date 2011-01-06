"""
A script for automatically extracting excerpts from articles. It requires lxml.

Usage::
    
    from lxml_extractor import get_summary
    url = "http://someurl.com/goes/here"
    (title,description) = get_summary(url)


Example and discussion:
http://www.screeley.com/entries/2009/jul/01/faster-python-script-extracting-excerpts-articles/

author: Sean Creeley (http://www.screeley.com)

Original License:
==========================================

Some examples, discussion, and comparison with the Facebook article extractor
are at http://blog.davidziegler.net/post/122176962/a-python-script-to-automatically-extract-excerpts-from

copyright: Copyright 2009 by David Ziegler
license: MIT License
website: http://github.com/dziegler/excerpt_extractor/tree/master 
"""

from lxml.html import fromstring
from lxml.html.clean import Cleaner
import urllib2
import cookielib


def get_summary(url):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    try:
        response = opener.open(url).read()
    except urllib2.URLError:
        return (None, None)

    doc = fromstring(response)

    cleaner = Cleaner(page_structure=False,
                  meta=False,
                  safe_attrs_only=False,
                  remove_tags=['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    #Remove irrelevant content from the document
    doc = cleaner.clean_html(doc)

    description = None
    try:
        description = doc.xpath('/html/head/meta[@content][@name="description"]')[0].get("content")
    except IndexError:
        pass

    title = None
    try:
        title = doc.xpath('/html/head/title')[0].text_content().strip()
    except IndexError:
        pass

    if not description:
        #Get rid of the head element
        doc.head.drop_tree()

        p_texts = [p.strip() for p in doc.text_content().split('\n')]
        description = max((len(p), p) for p in p_texts)[1].strip()[0:255]

    return title, description

"""
if __name__ == "__main__":
    urllist=("http://www.sfgate.com/cgi-bin/article.cgi?f=/c/a/2009/06/04/DD7V1806SV.DTL&type=performance",
              "http://www.chloeveltman.com/blog/2009/05/two-very-different-symphonies.html#links",
              "http://www.chloeveltman.com/blog/2009/06/child-prodigy-at-peabody-essex-museum.html#links",
              "http://www.sfgate.com/cgi-bin/article.cgi?f=/c/a/2009/06/04/NS9617O7JK.DTL&type=performance",
              "http://blogs.mercurynews.com/aei/2009/06/04/ramya-auroprem-joins-cast-of-spelling-bee/",
              "http://www.mercurynews.com/karendsouza/ci_12510394",
			  "http://www.good.is/post/30-places-we-want-to-work",								
              "http://www.reason.com/news/show/134059.html")

    for u in urllist:
        print '%s : %s\n' % get_summary(u)
"""
