pymd
=========


Description
-------------

pymd is a command line wrapper for [Python Markdown](http://pythonhosted.org/Markdown/) library but having a full HTML file instead of only what it's originally parsed.

pymd can parse a file, a folder or a list of files (in a .list) in their folder or to a specific one using ```-o```. If the folder doesn't exist, it will be created.

It includes all the extensions (extra (abbreviations, attributes lists, definition lists, fenced code blocks, footnotes, tables, smart strong), admonition, codehilite, headerid, meta, nl2br, sane_lists, toc, wikilinks) and you can add your own with ```--extension```.

You can merge the files with the ```--merge``` or ```merge``` flag. This is where the .list is useful because it parses the files in order. If you merge the files but don't specify an ```-o```, the script will take the header parent folder as the filename or where the script runs.

By default, the script embeds the css file in each document, but by using the ```--css```, the documents will link to the specified css. You can switch between sans (default) or serif fonts with the ```--serif``` command

The header file is just a normal (markdown) file that is shared among the "project" or is the header/title of the merged file. Thus it can have, for example, metadata (title, author, date...), the TOC of the merged files (using [TOC_HERE] placeholder), etc. The TOC's depth can be modified using ```--toc``` (by default it shows all the headings).

The header can be specified with the ```--header``` or using a file named ```_header``` in the folder or .list.

You can create a "book" using ```--book``` or ```book```; it just add navigational links in the documents and creates an index files which links to them. There two "styles" of navigation links: "prev & next" (default) and using the titles of the files with ```--nav```. You can also create a custom index file and name it ```_index``` in the folder or .list, or specify one with ```--index```

Usage examples
-------------

In same folder: 

	pymd.py nicefile.md

Process files in folder and create a book with serif font: 

	pymd.py /myfolder book -o /output --serif

Process files in .list, merge them:

	pymd.py nice.list merge -o /output --header im_a_header.md
	
More examples and explanation (with images, yay!) in this [blog post](http://www.intentodeblog.com.ar/posts/pymd/en.html)

Features
-----------

  * Batch process files (in folder or in a .list) with .md, .txt or .markdown extensions
  * Specify an output folder (with automatic creation)
  * Includes all the extensions installed by [Python Markdown](http://pythonhosted.org/Markdown/) and you can even specify your own!
  * Merge files into one big HTML or create a little book with navigation links (NEW! create your own index file)
  * CSSed: leave the no-so-ugly embeded CSS (you can even switch between sans and serif fonts) or link to one of your own if you prefer.
  * Headers for files! So you can share the same metadata (like your beautiful name and the creative title of your work) in all the files or when you merge the files and forgot to include the main title of your project.
  * Wiki links: ```[](path) -> [title linked file](output_path)``` (NEW!)
  * Made with love <3

