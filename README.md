# LspLexer4Pygments
connects a *Language Server Protocol* (LSP) server with [Pygments](https://github.com/pygments/pygments) for syntax highlighting.
This tool uses *Semantic Tokens* (LSP 3.16) and maps them to Pygment tokens (i.e. the Language Server needs to support the semantic tokens feature)

## usage
### cli
``
python3.8 -m pygments -x -O filetype=jimple,lsplocation=examples/jimplelsp-0.0.11.jar -l src/lsplexer/lexer.py:LspLexer examples/hello_world.jimple
``

### example config for mk_docs (to support jimple/jimplelsp)
Install LspLexer4Pygments.
``` 
pip install git+https://github.com/swissiety/LspLexer4Pygments
```

download the latest *jimplelsp.jar* release on github (analogous: get your LSP server)
```
curl -s https://api.github.com/repos/swissiety/jimpleLsp/releases/latest\
| grep "browser_download_url.*jar"\
| cut -d : -f 2,3\
| tr -d \"\
| wget -q -O jimplelsp.jar -
```

set config for Pygments in mkdocs.yml :
``` 
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
### pygments custom lexer infos/examples
https://www.iamjonas.me/2013/03/custom-syntax-in-pygments.html

## todo
- [x] call default/custom lexer via cli
- [x] connect to LspServer (via stdio)
- [x] adapt pylsp for semantic tokens ( see https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_semanticTokens)
- [ wip ] integrate semantic tokens into a custom pygment lexer
- [ ] run custom pygment via mk_docs
- [ ] create config/doc (usage in mk_docs - test in futuresoot)
  (filetype of supported lsp language, connection path/url aka lsplocation)
  https://facelessuser.github.io/PyMdown/user-guide/general-usage/#configuration-file
- [ ] nice2have: socket connection
