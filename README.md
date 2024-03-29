# LspLexer4Pygments
connects [Pygments](https://github.com/pygments/pygments) with a [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) (LSP) server for syntax highlighting purposes.

This tool uses the *semantic tokens* feature of LSP (LSP 3.16) and maps the retrieved information to Pygments tokens, which are then used by Pygments to highlight your input accordingly.

Pygments can colorize input for cli, HTML, LaTeX, ... so you can use Pygments and LspLexer4Pygments for syntax highlighting of a custom LspServer implementation to enhance your web based documentation e.g. via [MkDocs](https://github.com/mkdocs/mkdocs), your thesis, a scientific paper, etc.

## Requirements
- the used language server can communicate via STDIO and needs to support the semantic tokens capability
- Python 3.2

## Installation
(assumption: you already have python and pip installed)
```Shell
pip install git+https://github.com/swissiety/LspLexer4Pygments.git
```

## Configuration options

mandatory: *(hint: path expansion is disabled! So no environment vars etc.)*
> lspcommand="path/to/a/lsp_server/executable_or_command"

optional:
> filetype="file_extension" (default: txt) 



## Usage Examples
### LaTeX document (config: for **JimpleLSP**)
Command to translate Jimple code from file **code/jimple_listing1.jimple** to a file **pyg_export/jimple_listing1.pyg**
```Shell
 python3 -m pygments -x -P filetype=jimple \
 	-P lspcommand="java -jar /path/to/content_root/of/LspLexer4Pygments/examples/jimplelsp-0.0.11.jar" \
	-l lspserver -o pyg_export/jimple_listing1.pyg code/jimple_listing1.jimple
```

Example LaTeX document (subdirectory for the translated results are in **pyg_export/**)
```latex

\documentclass{article}
\usepackage[utf8x]{inputenc}
\usepackage{texments}
\usestyle{default} 		% Mandatory! other useful styles are: bw, borland, vs

\begin{document}

	\input{pyg_export/jimple_listing1.pyg}

\end{document}

```


### Web based documentation (via MkDocs)
get your LSP server binary. e.g. download the latest *jimplelsp.jar* release on github to support highlighting for [Soot](https://github.com/soot-oss/soot)s Jimple
```Shell
curl -s -L -o ./jimplelsp.jar \
	$(curl -s https://api.github.com/repos/swissiety/jimpleLsp/releases/latest | \
		grep 'browser_download_url".*jar"' | cut -d ':' -f 2,3 | tr -d \")
```

set config for Pygments in your mkdocs.yml (adapt "name: jimple" **(1)**, "filetype: jimple" and the lspcommand accordingly; "lang:" must be lspserver or lsplexer)
```Dockerfile
markdown_extensions:
  - pymdownx.highlight:
      linenums: true            # not necessary but nice
      use_pygments: true
      extend_pygments_lang:
        - name: jimple          # name for your language config
          lang: lspserver
          options:
            filetype: jimple    # adapt here if necessary
            lspcommand: "java -jar /workspace/LspLexer4Pygments/examples/jimplelsp-0.0.11.jar"  #adapt here 
  - pymdownx.superfences
```

specify your specified language name from **(1)** directly after the ticks of the surrounding code block
```
   ```jimple
      /* this is not the .jimple file content you're looking for ;-) */
      ...
    ```
```


### Command line interface / cli
generic (replace the placeholders) use installed LspLexer4Pygments
```Shell
python3 -m pygments -x \
	-P filetype=%FILETYPE% -P lspcommand="%LSPSERVERBINARY%" \
	-l lspserver %INPUTFILE%
```

generic (replace the placeholders) executed from content-root
```Shell
python3 -m pygments -x \
	-P filetype=%FILETYPE%-P lspcommand=%LSPSERVERBINARY% \
	-l lsplexer/lexer.py:LspLexer %INPUTFILE%
```

cli save to export.html executed from content-root
```Shell
python3 -m pygments -x -f html -O full \
	-P filetype=%FILETYPE% -P lspcommand=%LSPSERVERBINARY% \
	-l lsplexer/lexer.py:LspLexer -o export.html %INPUTFILE%
```

use the provided example as input (executing the given **.jar** via java) executed from content-root
```Shell
python3 -m pygments -x \
	-P filetype=jimple \
	-P lspcommand="java -jar examples/jimplelsp-0.0.11.jar" \
	-l lsplexer/lexer.py:LspLexer examples/hello_world.jimple
```
