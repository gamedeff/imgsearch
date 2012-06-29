# -*- coding: utf-8 -*-

import urllib, urllib2
import re, os, sys

lastext = ()
lastfilename = ''

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp,
																 code, msg,
																 headers)
		result.status = code
		result.headers = headers
		return result

def urlget(web_url, referer=''):
	global lastext
	global lastfilename
	res = ""
	try:
		opener = urllib2.build_opener(SmartRedirectHandler())
		opener.addheaders = []
		opener.addheaders.append(('Accept',	'text/html, application/xhtml+xml, */*'))
		opener.addheaders.append(('User-Agent',	'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'))
		if referer:
			opener.addheaders.append(('Referer',	referer))

		pg = opener.open(web_url)
		print pg.headers
		print pg.headers.maintype
		print pg.headers.subtype
		print pg.headers.type
		if pg.headers.maintype == 'image':
			lastext = ((os.path.extsep + 'jpg', os.path.extsep + 'jpeg') if pg.headers.subtype == 'jpeg' else (os.path.extsep + pg.headers.subtype))
		elif pg.headers.maintype in ['jpeg', 'jpg', 'gif', 'png', 'bmp', 'tga', 'dds', 'tiff']:
			lastext = (os.path.extsep + pg.headers.type)
		else:
			lastext = ()
		if pg.headers.has_key('Content-Disposition'): # If the response has Content-Disposition, we take file name from it
			lastfilename = pg.headers['Content-Disposition'].split('filename=')[1]
			if lastfilename[0] == '"' or lastfilename[0] == "'":
				lastfilename = lastfilename[1:-1]
		elif pg.headers.has_key('Location'):
			lastfilename = pg.headers['Location'].split('/')[-1].split('\\')[-1].split('#')[0].split('?')[0].split('&')[0]
		else:
			lastfilename = ''
		print pg.code
		res = pg.read()
	except IOError, e:
		if hasattr(e, 'reason'):
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
		elif hasattr(e, 'code'):
			print 'The server couldn\'t fulfill the request.'
			print 'Error code: ', e.code
	return res

def main():
	if len(sys.argv) < 2:
		print "Usage: %s 'keywords'" % sys.argv[0]
		sys.exit(1)

	search = ' '.join(sys.argv[1:])

	path = os.path.join(os.getcwd(), search)
	print path
	try: os.makedirs(path)
	except: pass
	os.chdir(path)

	sysencoding = sys.getfilesystemencoding() # 'cp1251'

	url = "http://images.google.com/search?tbm=isch&q=%s" % urllib2.quote(search.decode(sysencoding).encode('utf-8'))
	page = urlget(url)
	pglink = re.findall(r'<div style="display:block">(.*?)<a href="http://images.google.com/search.?tbm=isch(.*?)">(.*?)</a>', page)
	if pglink:
		images = True
		pgn = 0
		imgn = 0
		imgng = 0
		furls = open(search + os.path.extsep + "txt", 'w')
		done = []
		while images:
			pgurl = "http://images.google.com/search?tbm=isch%s&start=%d&sa=N&filter=0" % (pglink[0][1], pgn * 20)
			pgn = pgn + 1
			print pgurl
			page = urlget(pgurl, url)
			if 0: # for debuggin'
				f = open("page%d.html" % pgn, 'w')
				f.write(page)
				f.close()
			images = re.findall(r'<a href="/imgres.?imgurl=(.*?)&amp;imgrefurl=(.*?)&amp(.*?)">', page)
			for image in images:
				imgurl = urllib2.unquote(image[0])
				imgrefurl = urllib2.unquote(image[1])
				print imgurl, imgrefurl
				if imgurl not in done:
					imgn = imgn + 1
					img = urlget(imgurl, imgrefurl)
					if len(img):
						filename = urllib2.unquote(imgurl).decode('utf-8').encode(sysencoding).split('/')[-1].split('\\')[-1].split('#')[0].split('?')[0].split('&')[0]
						if not len(lastext):
							if len(lastfilename):
								filename = lastfilename
						elif not filename.lower().endswith(lastext): # os.path.extsep not in filename:
							filename += lastext[0]
						resfilename = "img%d_pg%d_%s" % (imgn, pgn, filename)
						f = open(resfilename, 'wb')
						f.write(img)
						f.close()
						imgng = imgng + 1
						done.append(imgurl)
						furls.write(imgurl + "\n")
		furls.close()
		print "\n%d out of %d images downloaded from %d search pages" % (imgng, imgn, pgn - 1)

if __name__ == '__main__':
	main()