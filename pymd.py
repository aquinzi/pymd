# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

try:
	import markdown
except Exception:
	print "Markdown library not installed"
	sys.exit()

import os
import codecs
import argparse
import errno

# ---------------------
# info
# ---------------------

my_version = "0.5.3"
my_usage = """ %(prog)s SOURCE [--output FOLDER [--flat]] [--header FILE ] [--exts LIST ]
                   [ --css FILE | --serif ] 
                   [ book [--index FILE --nav] | merge [--toc(0, 1, 2, 3, 4, 5)] ] 
  
 	Note: book is the same as --book, as well as merge is the same as --merge. """
my_description = """
 Human readable example: 
    %(prog)s /path/to/nice_folder book --nav --serif -o /path/to/nice_output_folder

 Description: 
 	Parse markdown to html with python markdown + all extensions. Extensions being: extra (abbreviations, attributes lists, definition lists, fenced code blocks, footnotes, tables, smart strong), admonition, codehilite, headerid, meta, nl2br, sane_lists, toc, wikilinks

"""
my_epilog = "  Using %(prog)s version " + my_version

# ---------------------
# Config
# ---------------------

headerFilename = "_header"
indexFilename = "_index"

# must be list
selected_ext = [
		'extra', 
		'admonition', 'codehilite','headerid', 'meta', 'nl2br', 'sane_lists', 'toc', 'wikilinks'
	]

needed_meta = (
		('title',   'h1'),
		('author',  'h2'),
		('date',    'h3'),
		('summary', 'p'),
		('comment', 'p')
	)

extensions_accepted = ("txt","md","markdown")
pyVer = sys.version_info[0]

# ---------------------
# Methods: Other
# ---------------------

# find substring in list and return it's index +1
def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i + 1 # if it's in the first, add 1 so doesn't go to false
    return False

class OptionsBelong(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if option_string == "--toc" and namespace.merge is False:
        	parser.error('--toc belongs to --merge')
        
        if option_string in ["--index", "--nav"] and namespace.book is False:
        	parser.error(option_string + ' belongs to --book')

        if option_string == "--nav" or option_string == "-n":
        	values = True
        setattr(namespace, self.dest, values)

class InputExist(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		if not os.path.exists(values):
			parser.error('Source file or folder doesn\'t exist')
		setattr(namespace, self.dest, values)

def args():
	# to allow --merge to be merge and still being optional
	subcat_args=('merge','book')
	arguments=['--'+arg if arg in subcat_args else arg for arg in sys.argv[1:]]

	# definitions:
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, add_help=False, usage=my_usage, description=my_description, epilog=my_epilog)

	group_required = parser.add_argument_group(' Required')

	group_required.add_argument("source"
								, help="File, folder or a .list which holds the path+files (in order) to parse (mainly used with merge or book)"
								, action=InputExist)

	group_options = parser.add_argument_group(' Options')
	
	group_options.add_argument("--output", "-o" 
								, help="Output folder to save processed files"
								, metavar='FOLDER')
	group_options.add_argument("--flat"
								, help="Saves all the files in a single directory depth (not using source dir tree)"
								, action="store_true")
	group_options.add_argument("--header"
								, help="Header file, mainly for merged files. Might contain main title, date and toc (as [TOC_HERE]) placement."
								, metavar='FILE')
	group_options.add_argument("--extensions"
								, help="List of other installed extensions"
								, nargs='*', metavar='ext')

	exclusive_css = group_options.add_mutually_exclusive_group()
	exclusive_css.add_argument("--css"
								, help="Custom css with path (as included in href). Default: embeded"
								, metavar='FILE')
	exclusive_css.add_argument("--serif"
								, help="In embeded css, choose between sans (false) or serif (true). Default: sans"
								, action='store_true')	

	group_special = parser.add_argument_group(' Specific')

	exclusive_style = group_special.add_mutually_exclusive_group()
	exclusive_style.add_argument("--merge"
								, help="Merge files into one."
								, action="store_true")
	group_special.add_argument  ("--toc"
								, help="Toc max depth (for [TOC_HERE]). Default: %(default)s (all)"
								, choices=[0, 1, 2, 3, 4, 5] , default=0 , type=int, action=OptionsBelong)
	exclusive_style.add_argument("--book"
								, help="Create a notebook with navigation (next, prev) between files and an index"
								, action="store_true")
	group_special.add_argument  ("--index"
								, help="Custom index for book"
								, action=OptionsBelong , metavar='FILE')
	group_special.add_argument  ("--nav", "-n"
								, help='Use file titles as the navigation links instead of "prev/next"'
								, default=False , nargs=0 , action=OptionsBelong )

	group_other = parser.add_argument_group(' Last but not least')
	group_other.add_argument("--help", "-h", help="show this help message and exit", action="help") 


	return parser.parse_args(arguments)

# ---------------------
# Methods: OS
# ---------------------

def getPath(file):

	return os.path.dirname(file)

def getLastDir(path):

	return os.path.split(path)[1]

def findPath(file):

	return os.path.abspath(file)

def getFilename(file):

	return os.path.basename(file)

def delExtension(file):

	path, ext = os.path.splitext(file)
	return path

def getFiles (elements):
	theFiles = list()

	if os.path.isfile(elements):
		if elements.endswith(extensions_accepted):
			theFiles.append(elements)
	else:
		for root, subFolders, files in os.walk(elements):
			for filename in files:
				filePath = os.path.join(root, filename)

				if os.path.exists(filePath) and filePath.endswith(extensions_accepted):
					theFiles.append(filePath)

	return theFiles	

def saveFile(name, content):

	# create output tree folders if doesnt exist
	mkdir_p(getPath(name))

	if pyVer == 3:
		cmd = open(name, 'w',encoding="utf-8-sig")
	else:
		cmd = codecs.open(name, "w", encoding="utf-8-sig")

	with cmd as outputFile:
		outputFile.write(content)	

def listFiles(path):
	if path.endswith(".list"):
		fileList = list()
		
		if pyVer == 3:
			cmd = open(path,"r", encoding='utf-8-sig')
		else:
			cmd = codecs.open(path,"r", encoding='utf-8-sig')
		
		with cmd as listFiles:
			for line in listFiles:
				line = line.strip()
				if line.endswith(extensions_accepted) and os.path.exists(line):
					fileList.append(line)
		return fileList
	
	return getFiles(path)

def readFile(file):

	if pyVer == 3:
		cmd = open(file,"r", encoding='utf-8-sig')
	else:
		cmd = codecs.open(file,"r", encoding='utf-8-sig')

	with cmd as input:
		textfile = input.read()
		input.seek(0)
		
		# Check if there's real meta or just title with :; if that's the case, add
		# line breaks so it doesn't parse as meta
		line1, line2 = next(input), next(input)

		if line2.startswith('==') or line2.startswith('--'):
			textfile = "\n\r " + textfile

	return textfile

def mkdir_p(path):
	""" make dirs according to tree in path """
	try:
		os.makedirs(path)
	except OSError as exc:
		if exc.errno != errno.EEXIST:
			raise 

def getOutputPath(filepath):
	if folderOutput:
		if not settings.flat:
			if filepath == sourcePath:
				newPath = os.path.join(folderOutput,delExtension(getFilename(filepath))+".html")
			else:
				newPath = os.path.join(folderOutput,delExtension(filepath)[len(sourcePath)+1:]+".html") # remove first \, otherwise join doesnt work

		else:
			newPath = os.path.join(folderOutput,delExtension(getFilename(filepath))+".html")

		return newPath
	
	return delExtension(filepath) + ".html"

def pagesSpecial():
	global allFiles, headerFile, indexFile

	# existance of header or index in files
	headerList = index_containing_substring(allFiles, headerFilename+".")
	indexList  = index_containing_substring(allFiles, indexFilename+".")

	if headerFile or headerList:
		if headerList and not headerFile:
			headerFile = allFiles[headerList -1]

		headerFile = findPath(headerFile)

		if headerFile in allFiles:
			allFiles.remove(headerFile)

	if indexFile or indexList:
		if indexList and not indexFile:
			indexList = allFiles[indexList -1]

		indexFile = findPath(indexFile)

		if indexFile in allFiles:
			allFiles.remove(indexFile)

def absolutePath(file_path):
	return delExtension(file_path)[len(sourcePath)+2:]+".html" #remove a letter and \

# ---------------------
# Methods: HTML
# ---------------------

def cssDefault():

	returnMe = """
	* 			{ margin: 0; padding: 0; }
	html, body 	{ color: black; }
	
	body {
		padding: 10px 25px; max-width: 700px; margin: 5px auto; 
	"""

	if settings.serif:
		returnMe += "	font: normal 14px 'Droid Serif', Georgia, serif;"
	else:
		returnMe += "	font: 14px helvetica,arial,freesans,clean,sans-serif;"

	returnMe += """
	    line-height: 1.6em;
		color: #3A3A3A;
		background-color: #f2f2f2;
	}

	p { margin: 1em 0; }

	a 				  {text-decoration: none; border-bottom: 1px dotted; color: #4183c4; }
	a:hover, a:active { color: #75A837; }

	blockquote {
		margin: 	14px 0; padding: 	0.7em 11px;
		color: 		#555;
		font-style: italic;
		border-left: 10px solid #838383;
	}

	img {
		display: 		  block;
		background-color: #F3F3F2;
		border: 		  1px solid #D9D9D7;
		margin: 		  0px auto;   padding: 		  5px;
	}

	ins { color:#008000; }
	del { color:#ACACAC; }

	hr { border: 0; height: 1px; background: #333; }

	sup, sub, a.footnote-ref {
	    height: 		0;
	    line-height: 	1;
	    vertical-align: super;
	    position: 		relative;
	}

	sub 			{vertical-align: sub; top: -1px; }
	a.footnote-ref { font-size: 1em; }

	abbr { border-bottom: 1px dotted }

	h1,h2,h3,h4,h5,h6 { margin: 15px 0; padding: 4px 0; border-bottom: 1px solid #e0e0e0; }
	h1 { font-size: 2em;}
	h2 { font-size: 1.571em; }
	h3 { font-size: 1.429em; }
	h4 { font-size: 1.286em; }
	h5 { font-size: 1.143em; color: #4d4d4d;}
	h6 { font-size: 1em; color: #666; }
	h1.title { margin:0 }

	ul, ol 	{ margin: 21px 0 0px 30px; list-style-position: outside; }
	li 		{ margin: 7px 0 }
	ul 		{ list-style-type: disc; }
	ol 		{ list-style-type: decimal-leading-zero; }

	dl, dt, dd { margin: 0; }
	dl { padding: 0px 1em 10px; }
	dt { padding: 5px 0 5px; font-weight: bold; line-height: normal; }
	dd { padding: 0 10px 20px 3em; font-style: italic; }
	
	table {
	    padding: 		0;
	    margin: 		0 auto 2em auto;
	    border-spacing: 0;
	    border-collapse: collapse;
	    width: 			70%;
	    border: 		1px solid;
	}
	tbody 		  { display: table-row-group; }
	tfoot 		  { display: table-footer-group; }
	th, td 		  { padding: 10px 10px 9px; line-height: 18px; border: 1px solid; }
	table, th, td { border-color:#607692; }
	th {
	    padding-top: 	  9px;
	    font-size: 		  18px;
	    font-weight:  	  bold !important;
	    vertical-align:   middle;
		color: 			  #fff;
		background-color: #007399; 
	}
	tr 		{ vertical-align: top;}
	tr.odd  { background-color: #CCDAFF; }
	table p { margin:0; }

	pre, code {
	    border: 		1px solid #ccc;
	    font-size: 		12px;
		font-family: 	Consolas, "Liberation Mono", Courier, monospace;
		background-color:#eee;
	}

	pre  { margin: 5px 0 0; padding: 6px 5px; white-space: pre; overflow: auto; }
	code { margin: 0 2px; padding: 2px 5px; white-space: nowrap; }

	.codehilite, .highlight { margin: 0 20px; overflow: auto; padding: 0 10px; }

	/* 			Code highlight: Perldoc  ------------------ */
	.hll { background-color: #ffffcc }
	.c { color: #228B22 } /* Comment */
	.err { color: #a61717; background-color: #e3d2d2 } /* Error */
	.k { color: #8B008B; font-weight: bold } /* Keyword */
	.cm { color: #228B22 } /* Comment.Multiline */
	.cp { color: #1e889b } /* Comment.Preproc */
	.c1 { color: #228B22 } /* Comment.Single */
	.cs { color: #8B008B; font-weight: bold } /* Comment.Special */
	.gd { color: #aa0000 } /* Generic.Deleted */
	.ge { font-style: italic } /* Generic.Emph */
	.gr { color: #aa0000 } /* Generic.Error */
	.gh { color: #000080; font-weight: bold } /* Generic.Heading */
	.gi { color: #00aa00 } /* Generic.Inserted */
	.go { color: #888888 } /* Generic.Output */
	.gp { color: #555555 } /* Generic.Prompt */
	.gs { font-weight: bold } /* Generic.Strong */
	.gu { color: #800080; font-weight: bold } /* Generic.Subheading */
	.gt { color: #aa0000 } /* Generic.Traceback */
	.kc { color: #8B008B; font-weight: bold } /* Keyword.Constant */
	.kd { color: #8B008B; font-weight: bold } /* Keyword.Declaration */
	.kn { color: #8B008B; font-weight: bold } /* Keyword.Namespace */
	.kp { color: #8B008B; font-weight: bold } /* Keyword.Pseudo */
	.kr { color: #8B008B; font-weight: bold } /* Keyword.Reserved */
	.kt { color: #a7a7a7; font-weight: bold } /* Keyword.Type */
	.m { color: #B452CD } /* Literal.Number */
	.s { color: #CD5555 } /* Literal.String */
	.na { color: #658b00 } /* Name.Attribute */
	.nb { color: #658b00 } /* Name.Builtin */
	.nc { color: #008b45; font-weight: bold } /* Name.Class */
	.no { color: #00688B } /* Name.Constant */
	.nd { color: #707a7c } /* Name.Decorator */
	.ne { color: #008b45; font-weight: bold } /* Name.Exception */
	.nf { color: #008b45 } /* Name.Function */
	.nn { color: #008b45; text-decoration: underline } /* Name.Namespace */
	.nt { color: #8B008B; font-weight: bold } /* Name.Tag */
	.nv { color: #00688B } /* Name.Variable */
	.ow { color: #8B008B } /* Operator.Word */
	.w  { color: #bbbbbb } /* Text.Whitespace */
	.mf { color: #B452CD } /* Literal.Number.Float */
	.mh { color: #B452CD } /* Literal.Number.Hex */
	.mi { color: #B452CD } /* Literal.Number.Integer */
	.mo { color: #B452CD } /* Literal.Number.Oct */
	.sb { color: #CD5555 } /* Literal.String.Backtick */
	.sc { color: #CD5555 } /* Literal.String.Char */
	.sd { color: #CD5555 } /* Literal.String.Doc */
	.s2 { color: #CD5555 } /* Literal.String.Double */
	.se { color: #CD5555 } /* Literal.String.Escape */
	.sh { color: #1c7e71; font-style: italic } /* Literal.String.Heredoc */
	.si { color: #CD5555 } /* Literal.String.Interpol */
	.sx { color: #cb6c20 } /* Literal.String.Other */
	.sr { color: #1c7e71 } /* Literal.String.Regex */
	.s1 { color: #CD5555 } /* Literal.String.Single */
	.ss { color: #CD5555 } /* Literal.String.Symbol */
	.bp { color: #658b00 } /* Name.Builtin.Pseudo */
	.vc { color: #00688B } /* Name.Variable.Class */
	.vg { color: #00688B } /* Name.Variable.Global */
	.vi { color: #00688B } /* Name.Variable.Instance */
	.il { color: #B452CD } /* Literal.Number.Integer.Long */

	.toc 	{ margin-top: 30px; }
	.toc a  { margin: 0 15px !important; }
	.toc ul {
	    margin: 1px 0 0 15px !important;    
	    padding: 0 0 0 1px !important;
	    display: block;
		line-height: 20px;
		list-style: none;
	}
	.toc ul li  { border-left: 1px solid; position: relative; margin:0 !important; }
	.toc ul > .toc li { padding-bottom: 10px !important;}
	.toc ul li:before {
	    content: '';
	    width: 14px;
	    position: absolute;
	    border-bottom: 1px solid;
	    left: 0px;
	    top: 10px;
	}
	.toc ul li:last-child {border-left:none;}
	.toc ul li:last-child:before {border-left:1px solid; height: 10px; margin-top:-10px !important; }
	#.toc ul li, .toc ul li:before, .toc ul li:last-child:before {border-color: #28484D ; }
	.toc ul li, .toc ul li:before, .toc ul li:last-child:before {border-color: #7A7A7A; }
	.admonition p   { margin: 0.5em 1em 0.5em 1em; padding: 0;}
	.admonition pre { margin: 0.4em 1em 0.4em 1em;}
	.admonition ul, .admonition ol { margin: 0.1em 0.5em 0.5em 3em;   padding: 0;}

	.admonition {
		margin: 		  2em;
		padding: 		  0;
		font-size: 		  0.9em;
	    border: 		  1px solid #c2c2c2;
	    background-color: #e9e9e9;
	}

	.admonition p.admonition-title {
		margin: 	0;
		padding: 	0.1em 0 0.1em 0.5em;
		font-size: 	1.1em;
		font-weight: bold;
		color: 		#fff;
	    border-bottom: 1px solid #c2c2c2;
		background-color: #999; 
	}

	.admonition.error, .admonition.caution, .admonition.danger
	{border-color: #900000; background-color: #ffe9e9;}

	.error p.admonition-title, .caution p.admonition-title, .danger p.admonition-title
	{background-color: #b04040; border-color: #900000;}

	.admonition.hint, .admonition.download 
	{background-color: #ECFAE3;  border-color: #609060;}

	.hint p.admonition-title, .download p.admonition-title 
	{background-color: #70A070; border-color: #609060;}

	.admonition.note, .admonition.tip, .admonition.warning
	{border-color:#e2ba54; background-color:#fcfce1;}

	.note p.admonition-title, .tip p.admonition-title, .warning p.admonition-title
	{background-color: #f1d170; border-color:#e2ba54;}

	.admonition.info, .admonition.attention, .admonition.important
	{background-color: #e8edfc; border-color: #94A7BF;}

	.info p.admonition-title, .attention p.admonition-title, .important p.admonition-title
	{background-color: #7088A0; border-color: #94A7BF;}

	.nav   { text-align: center; font-size: 1.2em; }
	.nav a { margin-left: 2em; display: inline-block; }
	.nav:first-of-type{ margin-bottom: 2em; }
	.nav:last-of-type { margin-top: 2em; }
	"""
	
	return returnMe

def htmlMissing (title):
	"""Complete the missing HTML, including CSS """

	begining = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>'+title+'</title>\n'

	if not settings.css:
		begining += "<style>" + cssDefault() + "</style>"
	else: 
		begining += '<link rel="stylesheet" href="'+settings.css+' type="text/css">'

	begining += '\n</head>\n<body>\n'

	ending='</body>\n</html>'
	
	return begining, ending

def htmlComplete(title, meta, text):
	""" reformat the text to valid html page """

	document = ""

	tagsBeg, tagsEnd = htmlMissing(title)
	document = tagsBeg + meta + text + tagsEnd

	return document

def bookNavigation(prev, ptitle, next, ntitle):
	navPre = ""
	navNext = ""

	if prev:
		prev = absolutePath(prev)
		if settings.nav:
			navPre = '<a href="'+prev+'">&lt; '+ptitle+'</a>'
		else:
			navPre = '<a href="'+prev+'">&lt; prev</a>'

	if next:
		next = absolutePath(next)
		if settings.nav:
			navNext = '<a href="'+next+'">'+ntitle+' &gt;</a>'
		else:
			navNext = '<a href="'+next+'">next &gt;</a>'

	return '<div class="nav">'+navPre+' <a href="index.html">index</a> '+navNext+'</div>'

def makeTextFinal(data_dict, navigation=""):

	title = ""
	meta  = ""
	body  = ""

	if headerHTML or headerTitle:
		title = headerTitle + " | " + data_dict['title']
		meta = navigation + headerHTML + "\n\r<article>" + data_dict['meta']
		body = data_dict['html'] + "</article>\n\r"+navigation
	else:
		title = data_dict['title']
		meta = "\n\r<header>" + navigation + data_dict['meta'] + "</header>\n\r"
		body = "\n\r<article>" + data_dict['html'] + "</article>\n\r"+navigation

	return htmlComplete(title, meta, body)

# ---------------------
# Methods: Parsing
# ---------------------

def findH1(text):

	if text.find("<h1 ")>-1: # because of extensions
		title = text[text.find("<h1 ")+4:text.find("</h1>")]
		title = title.split(">")[1] # dirty fix

		return title

	return None

def futureTitle(file):
	md = markdown.Markdown(extensions=selected_ext, output_format="html5")
	html = md.convert(readFile(file))

	return findH1(html)

def metaParse (dict):
	"""Take meta dict and convert it to HTML """

	MetaDataHTML = "" 
	title        = ""
	
	# pasamos metadata (importante) a html 
	for a in needed_meta:
		if a[0] in dict:
			if a[0] == "title":
				title = dict[a[0]][0]

			MetaDataHTML = MetaDataHTML + '<' + a[1] + ' class="'+a[0]+'">' + dict[a[0]][0] + '</' + a[1] + '>\n'
			
			del dict[a[0]]
	
	# ahora vemos si quedaron otras cosas, si es asi, pasamos a def list 
	if dict:
		MetaDataHTML = MetaDataHTML + '<dl>\n'
		for item in dict:
			MetaDataHTML = MetaDataHTML + '\t<dt>' + item +'</dt>\n\t<dd>' + dict[item][0] + '</dd>\n'

		MetaDataHTML = MetaDataHTML + '</dl>\n'
	
	return title, MetaDataHTML

def fileData(filepath):
	md    = markdown.Markdown(extensions=selected_ext, output_format="html5")
	meta  = ""
	title = ""

	html = md.convert(readFile(filepath))

	# save toc not especified in document
	try:
	    toc = md.toc
	except AttributeError:
	    toc   = ""

	if md.Meta:
		title, meta = metaParse(md.Meta)

	if not title:
		h1 = findH1(html)

		if h1 is not None:
			title = h1
		else:
			title = filepath
		
	data = {
		'html' : html,
		'path_output' : getOutputPath(filepath),
		'toc' : toc,
		'meta' : meta,
		'title' : title
	}

	return data 

def tocMerge(tocs):
	"""Merge multiple TOCs (HTML) into one """

	tocFinal = tocs.replace('\n</ul>\n</div>', "")

	if tocDepth == 0:
		tocFinal = tocFinal.replace('<div class="toc">\n<ul>\n', "") # dont touch
		
		# remove blank lines
		tocFinal = os.linesep.join([s for s in tocFinal.splitlines() if s])
	else:
		allTocs = tocFinal.split('<div class="toc">\n<ul>')[1:] # remove first as it's blank

		tocBuilding = ""

		for toc in allTocs:
			toc = toc.replace('<ul>','\n<ul>')
			tocSplitted = toc.split("\n")[1:]

			if tocDepth == 1:
				tocBuilding += tocSplitted[0] + "</li>"
			else:
				ulCount = 1
				doPrint = True

				for item in tocSplitted:
					if item == "<ul>":
						ulCount = ulCount + 1
					if item == "</ul>":
						ulCount = ulCount - 1

					if ulCount <= tocDepth:
						doPrint = True
					else:
						if item == "<ul>": # dirty fix
							tocBuilding += item 
						doPrint = False

					if doPrint:
						tocBuilding += item

		tocFinal = tocBuilding

	return '<div class="toc"><ul>'+tocFinal+'</ul></div>' 

def wikiLinks(text):
	"""
	Process "wiki" links: [](file.md) to [file title](newpath.html).
	It must be a markdown file, opened before
	"""

	textNew = list()
	
	for index, line in enumerate(text):
		if line.find("[](") > -1: # some bug going on...
			linkedFileName = line[line.find("[](")+3:line.find(")")]

			if os.path.exists(linkedFileName):
				title = futureTitle(linkedFileName)
				if title: 
					line = line.replace("[](","["+title+"](")
			else:
				line = line.replace("[](","["+linkedFileName+"](")

			outputPath = getFilename(getOutputPath(linkedFileName))

			line = line.replace(linkedFileName,outputPath)
		textNew.append(line)

	return textNew

def getHeader():
	headerText  = ""
	headerTitle = ""

	if headerFile and os.path.exists(headerFile):
		data_header = fileData(headerFile)
		headerTitle = data_header['title']
		
		if data_header['meta']:
			data_header['meta'] = "\n\r<header>" + data_header['meta'] + "</header>\n\r"

		headerText = '\n\r<section id="head">' + data_header['meta'] + data_header['html'] + "</section>\n\r"

	return headerTitle, headerText

def getIndex():
	if indexFile and os.path.exists(indexFile):
		parsedIndex = readFile(indexFile).split("\n")

		parsedIndex = wikiLinks(parsedIndex)

		# back to text
		parsedIndex = '\n'.join(n for n in parsedIndex)

		md = markdown.Markdown(extensions=selected_ext, output_format="html5")
		parsedIndex = md.convert(parsedIndex)

		outputPath = getOutputPath("index.html")

		output = htmlComplete("Index", "", parsedIndex)

		saveFile(outputPath, output)

def makeFiles():
	projectWhole = ""
	projectTocs = ""
	
	for file in allFiles:
		data_current = fileData(file)

		if not settings.merge:
			outputText = makeTextFinal(data_current)

			saveFile(data_current['path_output'], outputText)
		else:
			projectTocs += data_current['toc']
			projectWhole += '\r\n <article>' + data_current['meta'] + data_current['html'] + "</article>\n\r"

	if settings.merge:
		outputName = getLastDir(getPath(data_current['path_output'])) + ".html"

		projectTocs = tocMerge(projectTocs)
		headerReplaced = headerHTML.replace('[TOC_HERE]', projectTocs)

		outputText = htmlComplete(headerTitle, headerReplaced, projectWhole)

		if folderOutput:
			saveFile(folderOutput + '\\'+ outputName, outputText)
		else:
			saveFile(os.getcwd() + '\\'+ outputName, outputText)

def makeBook():
	
	bookIndex = "<ul>"
	filesTotal 	 = len(allFiles) - 1 # we process first one here
	
	data_first = fileData(allFiles[0])
	absPath = absolutePath(data_first['path_output'])
	bookIndex += '<li><a href="'+absPath+'">'+data_first['title']+'</a></li>'

	data_next = fileData(allFiles[1])
	navigation = bookNavigation("", "", data_next['path_output'], data_next['title'])

	outputText = makeTextFinal(data_first, navigation)

	saveFile(data_first['path_output'], outputText)

	data_prev    = data_first
	data_current = data_next
	data_next = {'path_output':"", 'title':""}
	
	for index, file in enumerate(allFiles[1:]):
		absPath = absolutePath(data_current['path_output'])
		bookIndex += '<li><a href="'+absPath+'">'+data_current['title']+'</a></li>'

		if index+1 < filesTotal:
			data_next = fileData(allFiles[index+1])

		navigation = bookNavigation(data_prev['path_output'], data_prev['title'], data_next['path_output'], data_next['title'])

		outputText = makeTextFinal(data_current, navigation)

		saveFile(data_current['path_output'], outputText)

		data_prev = data_current
		data_current = data_next
		data_next = {'path_output':"", 'title':""}

	if indexFile:
		getIndex()
	else:
		bookTitle = ""

		if headerTitle:
			bookTitle = headerTitle
		else:
			bookTitle = folderOutput
		
		bookIndex = htmlComplete(bookTitle, "", bookIndex+"</ul>")

		if folderOutput:
			saveFile(folderOutput+'\\index.html', bookIndex)
		else:
			saveFile(os.getcwd()+'\\index.html', bookIndex)
 

# -------------------
# The program
# -------------------

settings = args()

sourcePath   = settings.source
headerFile   = settings.header
folderOutput = settings.output
tocDepth     = settings.toc
indexFile    = settings.index

if settings.extensions:
	selected_ext = selected_ext + settings.extensions

allFiles = listFiles(sourcePath)

if folderOutput:
	mkdir_p(folderOutput)

pagesSpecial()

# do the magic
headerTitle, headerHTML = getHeader()

if settings.book:
	if len(allFiles) < 2:
		print "sorry, you can't"
		sys.exit()
	makeBook()
else:
	makeFiles()

print "\n    done"
