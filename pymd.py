
# -*- coding: utf-8 -*-

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
# Config & info
# ---------------------

my_version = "0.5.2"

headerFilename = "_header"

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

def args ():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="""
  Parse markdown to html with python markdown + extensions. Version """ + my_version + """
	
  Extensions: extra (abbreviations, attributes lists, definition lists, fenced code blocks, footnotes, tables, smart strong), admonition, codehilite, headerid, meta, nl2br, sane_lists, toc, wikilinks
	""")

	group_important = parser.add_argument_group('Important')
	group_important.add_argument("input", help="file, folder or a .list which holds the path+files (in order) to parse (mainly used in conjuntion with merge or book)")

	group_optional = parser.add_argument_group('Other Options')
	group_optional.add_argument("-output", "-o", help="Output folder to save processed files")
	group_optional.add_argument("-header", help="Header file, mainly for merged files. Might contain main title, date and toc (as [TOC_HERE]) placement.", default="")
	group_optional.add_argument("-css", help="custom css with path (as included in href). Default: embeded", default="")
	group_optional.add_argument("-serif", help="In embeded css, choose between sans (false) or serif (true). Default: sans", action='store_true')
	group_optional.add_argument("-extensions", "-ext", help="Other installed extensions",nargs='*')
	group_optional.add_argument("-toc", help="Toc max depth (for [TOC_HERE]). Default: 0 (all)", choices=[0, 1, 2, 3, 4, 5], default=0, type=int)


	group_exclusive = group_optional.add_mutually_exclusive_group()
	group_exclusive.add_argument("-merge", "-m", help="Merge files into one.", action='store_true')
	group_exclusive.add_argument("-book", "-b", help="Create a notebook with navigation (next, prev) between files and an index", action='store_true')
	group_exclusive.add_argument("-BOOK", "-B", help="Create a notebook with navigation (file titles) between files and an index", action='store_true')

	return vars(parser.parse_args()) 

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

# make dirs according to tree in path
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# ---------------------
# Methods: HTML
# ---------------------

def cssDefault():
	global isSerif

	returnMe = """
	* 			{ margin: 0; padding: 0; }
	html, body 	{ color: black; }
	
	body {
		padding: 10px 25px; max-width: 700px; margin: 5px auto; 
	"""

	if isSerif:
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

# complete the missing html, including css
def htmlMissing (title):

	part1 = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>'+title+'</title>\n'

	if not css_path:
		part1 += "<style>" + cssDefault() + "</style>"
	else: 
		part1 += '<link rel="stylesheet" href="'+css_path+' type="text/css">'

	part1 += '\n</head>\n<body>\n'

	part2='</body>\n</html>'
	
	return part1, part2

# reformat the text to valid html page
def htmlComplete(title, meta, text):
	document = ""

	tagsBeg, tagsEnd = htmlMissing(title)

	document = tagsBeg + meta + text + tagsEnd

	return document

def htmlBookNavigation(prev, ptitle, next, ntitle):
	navPre = ""
	navNext = ""

	if prev:
		navPre = delExtension(prev)
		if folderOutput:
			navPre = os.path.join(folderOutput,delExtension(getFilename(prev)))
		if bookNavTitles:
			navPre = '<a href="'+navPre+'.html">&lt; '+ptitle+'</a>'
		else:
			navPre = '<a href="'+navPre+'.html">&lt; prev</a>'

	if next:
		navNext = delExtension(next) 
		if folderOutput:
			navNext = os.path.join(folderOutput,delExtension(getFilename(next)))
		if bookNavTitles:
			navNext = '<a href="'+navNext+'.html">'+ntitle+' &gt;</a>'
		else:
			navNext = '<a href="'+navNext+'.html">next &gt;</a>'

	return '<div class="nav">'+navPre+' <a href="index.html">index</a> '+navNext+'</div>'

# ---------------------
# Methods: Parsing
# ---------------------

def findFirstHeader(text):

	if text.find("<h1>"):
		title = text[text.find("<h1>")+4:text.find("</h1>")]
		title = title.split(">")[1] # dirty fix

	return title

def futureTitle(file):
	if file:
		md = markdown.Markdown(extensions=selected_ext, output_format="html5")
		html = md.convert(readFile(file))

		return findFirstHeader(html)

# take meta and convert it to html
def metaParse (dict):

	# holders
	MetaDataHTML = "" 
	title        = ""
	
	# pasamos metadata (importante) a html 
	for a in needed_meta:
		if a[0] in dict:
			if a[0] == "title":
				title = dict[a[0]][0]

			MetaDataHTML = MetaDataHTML + '<' + a[1] + ' class="'+a[0]+'">' + dict[a[0]][0] + '</' + a[1] + '>\n'
			
			del dict[a[0]] # eliminamos del dict
	
	# ahora vemos si quedaron otras cosas, si es asi, pasamos a def list 
	if dict:
		MetaDataHTML = MetaDataHTML + '<dl>\n'
		for item in dict:
			MetaDataHTML = MetaDataHTML + '\t<dt>' + item +'</dt>\n\t<dd>' + dict[item][0] + '</dd>\n'

		MetaDataHTML = MetaDataHTML + '</dl>\n'
	
	return title, MetaDataHTML

def processHeaderFile():
	global headerFile
	global files

	md = markdown.Markdown(extensions=selected_ext, output_format="html5")

	# header processing (first part)
	headerFilePath     = ""
	headerTextHtml     = ""
	headerTitle        = ""
	headerMetaHtml     = ""

	# check for _header in file list
	index = index_containing_substring(files,headerFilename+".")

	if headerFile or index:

		if index and not headerFile:
			index = index - 1 # back to normal list index
			headerFile = files[index]

		if headerFile in files:
			files.remove(headerFile)

		headerFilePath = findPath(headerFile)

		if os.path.exists(headerFilePath):
			# header parsing		
			headerTextHtml = md.convert(readFile(headerFilePath))

			# default header title
			headerTitle = headerFile

			if md.Meta:
				headerTitle, headerMetaHtml = metaParse(md.Meta)

	if headerMetaHtml:
		headerMetaHtml = "\n\r<header>" + headerMetaHtml + "</header>\n\r"

	headerTextHtml = '\n\r<section id="head">' + headerMetaHtml + headerTextHtml + "</section>\n\r"

	return headerTitle, headerTextHtml

# merge multiple TOCs into one
def tocProcess(tocs):
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

def parseProject(elements):

	md = markdown.Markdown(extensions=selected_ext, output_format="html5")

	# header processing (first part)
	headerTitle, headerHtml = processHeaderFile()

	# process files
	projectWhole       = ""
	projectTocs        = ""
	fileOutputName     = ""
	bookIndex 			= "<ul>"
	prevTitle		   = ""
	nextTitle		= ""

	filesTotal = len(files)
	
	for index, file in enumerate(files):	
		fileOutputTextHtml = ""
		fileOutputTitle    = ""
		fileOutputMetaHtml = ""

		if folderOutput:
			fileOutputName = os.path.join(folderOutput,delExtension(getFilename(file))+".html")
		else:
			fileOutputName = delExtension(file) + ".html"

			
		fileOutputTextHtml = md.convert(readFile(file))

		# save toc not especified in document
		try:
		    projectTocs += md.toc
		except AttributeError:
		    pass

		# default title	
		fileOutputTitle = file
		

		if md.Meta:
			fileOutputTitle, fileOutputMetaHtml = metaParse(md.Meta)

			if fileOutputTitle:
				filetitle = fileOutputTitle
		else:
			filetitle = findFirstHeader(fileOutputTextHtml)
			fileOutputTitle = filetitle

		bookIndex += '<li><a href="'+fileOutputName+'">'+filetitle+'</a></li>'

		if not mergeFiles:
			navigation = ""
			if bookit:
				if index > 0:
					prevFile = files[index-1]
				else:
					prevFile = ""

				if (index + 1)== filesTotal:
					nextFile = ""
				else:
					nextFile = files[index+1]

				if bookNavTitles:
					nextTitle = futureTitle(nextFile)

				navigation = htmlBookNavigation(prevFile, prevTitle, nextFile, nextTitle)

			if headerTitle:
				fileOutputTextHtml = htmlComplete(headerTitle + " | " + fileOutputTitle, navigation + headerHtml + "\n\r<article>" + fileOutputMetaHtml , fileOutputTextHtml + "</article>\n\r"+navigation)
			else:	
				# completamos con el missing html 
				fileOutputTextHtml = htmlComplete(fileOutputTitle, "\n\r<header>" + navigation + fileOutputMetaHtml + "</header>\n\r", "\n\r<article>" + fileOutputTextHtml + "</article>\n\r"+navigation)

			saveFile(fileOutputName, fileOutputTextHtml)

		else:
			projectWhole += '\r\n <article>' + fileOutputMetaHtml + fileOutputTextHtml + "</article>\n\r"

		prevTitle = fileOutputTitle

		md.reset()
	
	if bookit:
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


	# Process for merged files
	if mergeFiles:

		# Process toc:
		projectTocs = tocProcess(projectTocs)
		headerHtml = headerHtml.replace('[TOC_HERE]', projectTocs)

		fileOutputTextHtml = htmlComplete(headerTitle, headerHtml, projectWhole)

		fileOutputName = getLastDir(getPath(fileOutputName)) + ".html"

		if folderOutput:
			saveFile(folderOutput + '\\'+ fileOutputName, fileOutputTextHtml)
		else:
			saveFile(os.getcwd() + '\\'+ fileOutputName, fileOutputTextHtml)



# -------------------
# The program
# -------------------

args = args()

file         = args['input']
css_path     = args['css']
isSerif      = args['serif']
mergeFiles   = args['merge']
headerFile   = args['header']
folderOutput = args['output']
bookit 		 = args['book']
bookNavTitles = args['BOOK']
tocDepth 	 = args['toc']

if bookNavTitles:
	bookit = True

if args['extensions']:
	selected_ext = selected_ext + args['extensions']

if not os.path.exists(file):
	print "Source file or folder doesn't exist"
	sys.exit()

files = listFiles(file)

if folderOutput:
	mkdir_p(folderOutput)

# do the magic
parseProject(files)

print "\n    done"
