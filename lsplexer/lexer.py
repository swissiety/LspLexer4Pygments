import tempfile
import pylspclient
import subprocess
import threading

import pygments.token
from pygments.lexer import Lexer

from lsplexer.CustomLspClient import CustomLspClient
from lsplexer.CustomLspEndpoint import CustomLspEndpoint


class ReadPipe(threading.Thread):
    def __init__(self, pipe):
        threading.Thread.__init__(self, daemon=True)
        self.pipe = pipe

    def run(self):
        line = self.pipe.readline().decode('utf-8')
        while line:
            print('LspLexer4Pygment: ' + line)
            line = self.pipe.readline().decode('utf-8')


class LspLexer(Lexer):
    name = 'LspLexer'
    aliases = ['lspserver', 'lsplexer']
    filenames = []
    alias_filenames = []

    def __init__(self, **options):
        self.filetype = options.get('filetype', 'txt')
        self.lspcommand = options.get('lspcommand', '')
        self.filenames = ['*.' + self.filetype]

        Lexer.__init__(self, **options)

    #    def get_tokens(text)
    # This method is the basic interface of a lexer. It is called by the highlight() function. It must process the text and return an iterable of (tokentype, value) pairs from text.
    #        Normally, you don’t need to override this method. The default implementation processes the stripnl, stripall and tabsize options and then yields all tokens from get_tokens_unprocessed(), with the index dropped.

    def map_token(self, semantictoken):
        # built in tokens https://pygments.org/docs/tokens/
        map = {
            'type': pygments.token.Name.Class,
            'class': pygments.token.Name.Class,
            'enum': pygments.token.Name.Class,
            'interface': pygments.token.Name.Class,
            'struct': pygments.token.Name.Class,
            'typeParameter': pygments.token.Name.Class,
            'parameter': pygments.token.Name.Variable,
            'variable': pygments.token.Name.Variable,
            'property': pygments.token.Name,
            'enumMember': pygments.token.Name,
            'event': pygments.token.Keyword,
            'function': pygments.token.Name.Function,
            'method': pygments.token.Name.Function,
            'macro': pygments.token.Name.Function.Magic,
            'keyword': pygments.token.Keyword,
            'modifier': pygments.token.Keyword,
            'comment': pygments.token.Comment,
            'string': pygments.token.String,
            'number': pygments.token.Number,
            'regexp': pygments.token.String.Regex,
            'operator': pygments.token.Operator
        }
        # print(semantictoken + " ->  "+ str(map.get(semantictoken)))
        return map.get(semantictoken)

    def get_tokens_unprocessed(self, text):
        # This method should process the text and return an iterable of (index, tokentype, value) tuples where index is the starting position of the token within the input text.
        # This method must be overridden by subclasses.

        # print("prepare lsp connection for pygmentizing "+ self.filetype)

        # initialize lsp connection
        try:
            if self.lspcommand == '':
                raise Exception("The mandatory lspcommand is not specified - we don't know where to connect to.")

            p = subprocess.Popen(self.lspcommand.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        except Exception as e:
            if 'p' in vars():
                p.kill()

            print("Running the specified lspcommand '" + self.lspcommand + "' failed.", e)
            yield 0, pygments.token.Text, text
            return

        read_pipe = ReadPipe(p.stderr)
        read_pipe.start()
        json_rpc_endpoint = pylspclient.JsonRpcEndpoint(p.stdin, p.stdout)
        # To work with socket: sock_fd = sock.makefile()
        lsp_endpoint = CustomLspEndpoint(json_rpc_endpoint)

        lsp_client = CustomLspClient(lsp_endpoint)
        root_uri = None
        workspace_folders = []  # {'name': 'LspCanvas', 'uri': root_uri}
        capabilities = {
            'textDocument': {

                'semanticTokens': {
                    'dynamicRegistration': False,
                    'requests': {'range': False, 'full': True},
                    'tokenTypes': ['type', 'class', 'enum', 'interface', 'struct', 'typeParameter', 'parameter',
                                   'variable',
                                   'property', 'enumMember', 'event', 'function', 'method', 'macro', 'keyword',
                                   'modifier', 'comment', 'string', 'number', 'regexp', 'operator'],
                    'tokenModifiers': [],
                    'formats': ['relative'],
                    'overlappingTokenSupport': True,
                    'multilineTokenSupport': True
                }
            },
            'workspace': {}
        }

        try:
            poll = p.poll()
            if poll is not None:
                raise Exception("lspclient: the server process is not running.")

            result = lsp_client.initialize(p.pid, root_uri, root_uri, None, capabilities, "off", workspace_folders)
            # fail early -> check if semantictoken capability is there.
            if 'semanticTokensProvider' not in result['capabilities']:
                raise Exception("lspclient: the specified LSP server has no SemanticToken capability!")

            doSyncFile = False
            if 'textDocumentSync' in result['capabilities']:
                value = result['capabilities']['textDocumentSync']
                if isinstance(value, int):
                    if value > 0:
                        doSyncFile = True
                elif 'openClose' in value:
                    if bool(value['openClose']):
                        doSyncFile = True

            if doSyncFile:
                temp_dir = None
                # synced file contents via didopen
                lsp_client.initialized()

                uri = 'file://' + tempfile.gettempdir() + '/file-does-not-exist-anywhere.' + self.filetype
                languageId = self.filetype
                version = 1
                lsp_client.didOpen(pylspclient.lsp_structs.TextDocumentItem(uri, languageId, version, text))

            else:
                # no sync -> save text to a temporary file
                temp_dir = tempfile.TemporaryDirectory()
                fo = open(temp_dir.name + '/sheet_of_empty_canvas.' + self.filetype, 'w')
                fo.write(text)
                fo.close()
                print('file written to ' + fo.name)
                lsp_client.initialized()
                uri = 'file://' + fo.name

            tokenResult, legend = lsp_client.semantic_token(pylspclient.lsp_structs.TextDocumentIdentifier(uri))

            lsp_client.shutdown()
            lsp_client.exit()

        except Exception as e:
            print(e)
            yield 0, pygments.token.Text, text
            return
        finally:
            p.kill()


        # cleanup temp dir if used
        if temp_dir is not None:
            temp_dir.cleanup()

        if result is None:  # return whole input as a token
            p.kill()
            yield 0, pygments.token.Text, text
            return

        lineNo = 0
        lineOffsetIdx = 0

        # translate/map response to pygment tokentypes
        # we cannot assume the semantic tokens are sorted ascending by startindex
        result = []
        for startLine, startCharInLine, length, tokenType, tokenModifier in legend.transformTokenInts(tokenResult['data']):

            # move "cursor" to the line of the token to convert from linenumber+column to the index position in the file
            while lineNo < startLine:
                lineOffsetIdx = text.find('\n', lineOffsetIdx) + 1  # beginning idx of the newline
                lineNo += 1

            tokenStartIdx = lineOffsetIdx + startCharInLine

            endIdx = tokenStartIdx + length
            result.append([tokenStartIdx, self.map_token(tokenType), endIdx])
            # update lineNo if token goes across multiple lines!
            lineNo += text.count('\n', tokenStartIdx, endIdx);


        # sort all tokens that have now absolute indices which are sortable
        result.sort(key=lambda x: x[0])
        printedIdx = 0
        for tokenStartIdx, tokenType, tokenEndIdx in result:
            # skip possible overlapping tokens
            if tokenStartIdx <= printedIdx:
                if tokenEndIdx > printedIdx:
                    # add rest of token
                    yield printedIdx, tokenType, text[printedIdx:tokenEndIdx]
                    printedIdx = tokenEndIdx
                continue

            # fill gap
            if printedIdx < tokenStartIdx:
                yield printedIdx, pygments.token.Text, text[printedIdx:tokenStartIdx]

            # add token
            yield tokenStartIdx, tokenType, text[tokenStartIdx:tokenEndIdx]
            printedIdx = tokenEndIdx

        # print tail token if its not already a token
        if printedIdx < len(text):
            yield printedIdx, pygments.token.Text, text[printedIdx:len(text)]

