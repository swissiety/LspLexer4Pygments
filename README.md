# LspLexer4Pygments
enable lsp protocols' semantic tokens into syntax highlighting by pygments

## example usage
### cli
``
python3.8 -m pygments -x -O filetype=jimple,lsplocation=examples/jimplelsp-0.0.11.jar -l src/lsplexer/lexer.py:LspLexer examples/hello_world.jimple
``

###example config for jimple/jimplelsp for mk_docs in futuresoot
download latest jimplelsp.jar:

```
curl -s https://api.github.com/repos/swissiety/jimpleLsp/releases/latest\
| grep "browser_download_url.*jar"\
| cut -d : -f 2,3\
| tr -d \"\
| wget -q -O jimplelsp.jar -
```

set mk_docs config for lspPygments:
``` 
markdown_extensions:
    - pymdownx.highlight:
        use_pygments: true
        extend_pygments_lang:
            {"name": "php-inline", "lang": "php", "options": {"filetype": "jimple", "lsplocation:": "./examples/jimplelsp-0.0.11.jar"}}
    - codehilite
``` (check: maybe codehilite is not necessary!)
(see [pymdown-extensions doc](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/), [extension config](https://facelessuser.github.io/pymdown-extensions/faq/))

## development
### pygments custom lexer infos/examples
https://www.iamjonas.me/2013/03/custom-syntax-in-pygments.html

## todo
- [x] call default/custom lexer via cli
- [x] connect to LspServer (via stdio)
- [ wip ] adapt pylsp for semantic tokens ( see https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_semanticTokens)
- [ ] integrate semantic tokens into custom pygment
- [ ] run custom pygment via mk_docs
- [ ] create config/doc (usage in mk_docs - test in futuresoot)
  (filetype of supported lsp language, connection path/url aka lsplocation)
  https://facelessuser.github.io/PyMdown/user-guide/general-usage/#configuration-file
- [ ] nice2have: socket connection
