# LspLexer4Pygments
connects a *Language Server Protocol* (LSP) server with [Pygments](https://github.com/pygments/pygments) for syntax highlighting.
This tool uses the *semantic tokens* feature of LSP (LSP 3.16) and maps them to Pygments tokens, which are then used by Pygments to highlight your input accordingly.

## requirements
- the language server needs to support the semantic tokens capability
- the language server can communicate via STDIO
- Python 3.2

## usage
adapt LspLexer4Pygments options:
```
# mandatory; path expansion is disabled!
lspcommand="executable_(command)_to_a_lsp_server"

# optional
filetype="file_extension" 
```

### cli
generic (replace the placeholders)
```
python3.8 -m pygments -x -O filetype=%FILETYPE%,lspcommand=%LSPSERVERBINARY% -l lsplexer/lexer.py:LspLexer %INPUTFILE%
```

cli save to export.html
```
python3.8 -m pygments -x -f html -O full,filetype=%FILETYPE%,lspcommand=%LSPSERVERBINARY% -l lsplexer/lexer.py:LspLexer -o export.html %INPUTFILE%
```



provided example input (executing given .jar via java)
```
python3.8 -m pygments -x -O filetype=jimple,lspcommand="java -jar examples/jimplelsp-0.0.11.jar" -l lsplexer/lexer.py:LspLexer examples/hello_world.jimple
```

### mk_docs config
Install LspLexer4Pygments:
``` 
pip install git+https://github.com/swissiety/LspLexer4Pygments.git
```

get your LSP server binary. e.g. download the latest *jimplelsp.jar* release on github to support highlighting for [Soot](https://github.com/soot-oss/soot) s Jimple:
```
curl -s https://api.github.com/repos/swissiety/jimpleLsp/releases/latest\
| grep "browser_download_url.*jar"\
| cut -d : -f 2,3\
| tr -d \"\
| wget -q -O jimplelsp.jar -
```

set config for Pygments in your mkdocs.yml (adapt "name: jimple" (1), "filetype: jimple" and the lspcommand accordingly; "lang:" needs to be lspserver):
```
markdown_extensions:
  - pymdownx.highlight:
      linenums: true    #not necessary but nice
      use_pygments: true
      extend_pygments_lang:
        - name: jimple
          lang: lspserver
          options:
            filetype: jimple
            lspcommand: "java -jar /workspace/LspLexer4Pygments/examples/jimplelsp-0.0.11.jar"
  - pymdownx.superfences
```

specify your specified language name from (1) directly after the ticks of the surrounding code block:
```
   ```jimple
      /* this is not the .jimple file content you're looking for */
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
