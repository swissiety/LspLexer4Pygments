# LspLexer4Pygments
connects a *Language Server Protocol* (LSP) server with [Pygments](https://github.com/pygments/pygments) for syntax highlighting.
This tool uses the *semantic tokens* feature of LSP (LSP 3.16) and maps them to Pygments tokens, which are then used by Pygments to highlight your input accordingly.
Pygments can colorize input for cli, HTML, LaTeX, ... so you can use Pygments and LspLexer4Pygments for syntax highlighting of a custom LspServer implementation to enhance your web based documentation e.g. via mk_docs, your thesis, scientific paper, etc.

## requirements
- the used language server can communicate via STDIO and needs to support the semantic tokens capability
- Python 3.2

## installation (assumption: you already have python and pip installed)
``` 
pip install git+https://github.com/swissiety/LspLexer4Pygments.git
```

## usage
LspLexer4Pygments options
```
#mandatory; hint: path expansion is disabled!
lspcommand="executable_(command)_to_a_lsp_server"

# optional
filetype="file_extension" (default: txt) 
```

### cli
generic (replace the placeholders) use installed LspLexer4Pygments
```
python3 -m pygments -x -P filetype=%FILETYPE% -P lspcommand="%LSPSERVERBINARY%" -l lspserver %INPUTFILE%

```

generic (replace the placeholders) executed from content-root
```
python3 -m pygments -x -P filetype=%FILETYPE% -P lspcommand=%LSPSERVERBINARY% -l lsplexer/lexer.py:LspLexer %INPUTFILE%
```

cli save to export.html executed from content-root
```
python3 -m pygments -x -f html -O full -P filetype=%FILETYPE% -P lspcommand=%LSPSERVERBINARY% -l lsplexer/lexer.py:LspLexer -o export.html %INPUTFILE%
```

provided example input (executing given **.jar** via java) executed from content-root
```
python3 -m pygments -x -P filetype=jimple -P lspcommand="java -jar examples/jimplelsp-0.0.11.jar" -l lsplexer/lexer.py:LspLexer examples/hello_world.jimple
```

## use in a LaTeX document (config: for **JimpleLSP**)
Command to translate Jimple code from file **code/jimple_listing1.jimple** to a file **pyg_export/jimple_listing1.pyg**
```
 python3 -m pygments -x -P filetype=jimple -P lspcommand="java -jar /path/to/content_root/of/LspLexer4Pygments/examples/jimplelsp-0.0.11.jar" -l lspserver -o pyg_export/jimple_listing1.pyg code/jimple_listing1.jimple
```

Example LaTeX document (subdirectory for the translated results are in **pyg_export/**)
```

\documentclass{article}
\usepackage[utf8x]{inputenc}
\usepackage{texments}
\usestyle{default} 				% Mandatory! other useful styles are: bw, borland, vs

\begin{document}

	\input{pyg_export/jimple_listing1.pyg}

\end{document}

```


### mk_docs config
get your LSP server binary. e.g. download the latest *jimplelsp.jar* release on github to support highlighting for [Soot](https://github.com/soot-oss/soot) s Jimple
```
curl -s https://api.github.com/repos/swissiety/jimpleLsp/releases/latest\
| grep "browser_download_url.*jar"\
| cut -d : -f 2,3\
| tr -d \"\
| wget -q -O jimplelsp.jar -
```

set config for Pygments in your mkdocs.yml (adapt "name: jimple" (1), "filetype: jimple" and the lspcommand accordingly; "lang:" must be lspserver or lsplexer)
```
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

specify your specified language name from (1) directly after the ticks of the surrounding code block
```
   ```jimple
      /* this is not the .jimple file content you're looking for ;-) */
      ...
    ```
```


## development
## todo
- [x] call default/custom lexer via cli
- [x] connect to LspServer (via stdio)
- [x] adapt pylsp for semantic tokens [LSP Reference](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_semanticTokens)
- [x] integrate semantic tokens into a custom pygment lexer
- [x]  allow different types of binary to execute (not just java/jars)
- [ ] nice2have: socket connection to lsp server
- [x] create example config/usage for mk_docs  (filetype of supported lsp language, connection path/url aka lsplocation)
  [see PyMDown config FAQ](https://facelessuser.github.io/PyMdown/user-guide/general-usage/#configuration-file)
- [x] run/test this tool via mk_docs
- [x] create installation script for pip
- [ ] nice2have: semantic token modifiers
- [x] example how to use it in LaTeX