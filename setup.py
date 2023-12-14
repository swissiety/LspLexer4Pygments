from setuptools import setup, find_packages
setup (
  name='LspLexer4Pygments',
  version='0.2.0',
  description='Connect a Language Server Protocol (LSP) Server with Pygments via a lexer implementation that is fed by the SemanticTokens Request',
  long_description='',
  url='https://github.com/swissiety/LspLexer4Pygments',
  keywords='pygments,highlight,mkdocs',
  author='Markus Schmidt',
  author_email='markus262@web.de',

  python_requires='>=3.2',
  install_requires=[
    'Pygments>=2.9.0',
    'pylspclient=0.0.2'
  ],

  packages=find_packages(),
  entry_points="""
  [pygments.lexers]
  lspLexer = lsplexer.lexer:LspLexer
  """,
)
