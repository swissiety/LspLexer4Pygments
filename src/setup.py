from setuptools import setup, find_packages

setup (
  name='LspLexer',
  packages=find_packages(),
  entry_points =
  """
  [pygments.lexers]
  lsplexer = lsplexer.lexer:LspLexer
  """,
)