# LspLexer4Pygments
connects a *Language Server Protocol* (LSP) server with [Pygments](https://github.com/pygments/pygments) for syntax highlighting.
This tool uses the *semantic tokens* feature of LSP (LSP 3.16) and maps them to Pygments tokens (i.e. the Language Server needs to support the semantic tokens feature).

## usage
### cli
generic (replace placeholder)
```
python3.8 -m pygments -x -O filetype=jimple,lsplocation=%SERVERBINARY% -l src/lsplexer/lexer.py:LspLexer %INPUTFILE%
```

provided example input
```
python3.8 -m pygments -x -O filetype=jimple,lsplocation=examples/jimplelsp-0.0.11.jar -l src/lsplexer/lexer.py:LspLexer examples/hello_world.jimple
```

### example mk_docs config
Install LspLexer4Pygments.
``` 
**WIP!**
pip install git+https://github.com/swissiety/LspLexer4Pygments
```

get your LSP server binary. e.g. download the latest *jimplelsp.jar* release on github to support highlighting fpr [Soot](https://github.com/soot-oss/soot) s Jimple.
```
curl -s https://api.github.com/repos/swissiety/jimpleLsp/releases/latest\
| grep "browser_download_url.*jar"\
| cut -d : -f 2,3\
| tr -d \"\
| wget -q -O jimplelsp.jar -
```

set config for Pygments in mkdocs.yml (adapt **jimple** and the path to your binary with accordingly):
```
**WIP!**
markdown_extensions:
    - pymdownx.highlight:
        use_pygments: true
        extend_pygments_lang:
            {"name": "jimple", "lang": "lsp", "options": {"filetype": "jimple", "lsplocation:": "./jimplelsp.jar"}}
    - codehilite
```
(check: maybe codehilite is not necessary)
(see [pymdown-extensions doc](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/), [extension config](https://facelessuser.github.io/pymdown-extensions/faq/))

## development
## todo
- [x] call default/custom lexer via cli
- [x] connect to LspServer (via stdio)
- [x] adapt pylsp for semantic tokens [LSP Reference](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_semanticTokens)
- [x] integrate semantic tokens into a custom pygment lexer [see](https://www.iamjonas.me/2013/03/custom-syntax-in-pygments.html)
- [ ] create example config/usage for mk_docs  (filetype of supported lsp language, connection path/url aka lsplocation)
  [see PyMDown config FAQ](https://facelessuser.github.io/PyMdown/user-guide/general-usage/#configuration-file)
- [ ] run/test this tool via mk_docs
- [ ] create installation script for pip [blog post](https://www.iamjonas.me/2013/03/custom-syntax-in-pygments.html)
- [ ] nice2have: socket connection to lsp server
- [ ] nice2have: semantic token modifiers

## 