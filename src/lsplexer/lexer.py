import json
import re
import time
import pygments.token
from pygments.lexer import Lexer
import tempfile
import pylspclient
import subprocess
import threading
from src.lsplexer.CustomLspEndpoint import CustomLspEndpoint
from src.lsplexer.CustomLspClient import CustomLspClient


class ReadPipe(threading.Thread):
    def __init__(self, pipe):
        threading.Thread.__init__(self, daemon=True)
        self.pipe = pipe

    def run(self):
        line = self.pipe.readline().decode('utf-8')
        while line:
            print('LspLexer4Pygment: '+line)
            line = self.pipe.readline().decode('utf-8')

# built in tokens https://pygments.org/docs/tokens/




class LspLexer(Lexer):

    def __init__(self, **options):
        self.filetype = options.get('filetype', '')
        self.lsplocation = options.get('lsplocation', '')

        self.name = 'LspLexer'
        self.aliases = ['lsp']
        self.filenames = ['*.'+self.filetype ]
#       self.alias_filenames = [];

        Lexer.__init__(self, **options)

#    def get_tokens(text)
        #This method is the basic interface of a lexer. It is called by the highlight() function. It must process the text and return an iterable of (tokentype, value) pairs from text.
        #        Normally, you don’t need to override this method. The default implementation processes the stripnl, stripall and tabsize options and then yields all tokens from get_tokens_unprocessed(), with the index dropped.


    def get_tokens_unprocessed(self, text):
        #This method should process the text and return an iterable of (index, tokentype, value) tuples where index is the starting position of the token within the input text.
        #This method must be overridden by subclasses.

        print("prepare lsp connection for pygmentizing "+ self.filetype);

        # initialize lsp connection
        # TODO: incorporate lsplocation/command
        p = subprocess.Popen(['java', '-jar', self.lsplocation], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        read_pipe = ReadPipe(p.stderr)
        read_pipe.start()
        json_rpc_endpoint = pylspclient.JsonRpcEndpoint(p.stdin, p.stdout)
        # To work with socket: sock_fd = sock.makefile()
        lsp_endpoint = CustomLspEndpoint(json_rpc_endpoint)

        lsp_client = CustomLspClient(lsp_endpoint)
        root_uri = None
        workspace_folders = []  #{'name': 'LspCanvas', 'uri': root_uri}
        capabilities = {
            'textDocument': {

                'semanticTokens': {
                    'dynamicRegistration': False,
                    'requests': { 'range': False, 'full': True },
                    'tokenTypes': ['type', 'class', 'enum', 'interface','struct','typeParameter','parameter','variable',
                                   'property','enumMember','event','function','method','macro','keyword',
                                   'modifier','comment','string','number','regexp','operator'],
                    'tokenModifiers': [],
                    'formats': ['relative'],
                    'overlappingTokenSupport': False,
                    'multilineTokenSupport': True
                }
            },
            'workspace': {}
        }

        result = lsp_client.initialize(p.pid, root_uri, root_uri, None, capabilities, "off", workspace_folders)

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

            uri = "file://" + tempfile.gettempdir() + "/file-does-not-exist-anywhere.jimple"
            languageId = self.filetype
            version = 1
            lsp_client.didOpen(pylspclient.lsp_structs.TextDocumentItem(uri, languageId, version, text))

        else:
            # no sync -> save text to a temporary file
            temp_dir = tempfile.TemporaryDirectory()
            fo = open(temp_dir.name+"/sheets_of_empty_canvas.jimple", "w")
            fo.write( text )
            fo.close()
            print('file written to '+ fo.name)
            lsp_client.initialized()
            uri = "file://" + fo.name


        time.sleep(1);          # TODO: quickfix/hack for jimplelsp.initialized() and asynchronous file access in - remove line with new release!


        data, legend = lsp_client.semantic_token( pylspclient.lsp_structs.TextDocumentIdentifier(uri) )

        lsp_client.shutdown()
        # wait a moment
        lsp_client.exit()
        # cleanup temp dir if used
        if temp_dir is not None:
            temp_dir.cleanup()

        if data is None:    # return whole input as a token
            return 0, None, data

        lineNo = 0
        firstCharIdx = -1
        printedCharIdx = 0

        # translate/map response to pygment tokentypes
        # assume the semantic tokens are sorted ascending by startindex
        for startLine, startChar, length, tokenType, tokenModifier in legend.transformTokenInts(data):

            #print("\n["+str(startLine)+":"+str(startChar)+"] "+ str(length)+ "   -> "+ tokenType )

            #handle lines between tokens aka token gaps
            while lineNo < startLine:
                firstCharIdx = text.find('\n', firstCharIdx)    # beginning idx of the newline
                lineNo += 1
                #print("line token");
                yield printedCharIdx, None, text[printedCharIdx:firstCharIdx]  # print the line
                printedCharIdx = firstCharIdx;

            # add gaps in the text which have no token as token (from semantic token or lines)
            if printedCharIdx < startChar:  # is already on the same line
                #print("gap token");
                yield printedCharIdx, None, text[ printedCharIdx:startChar-1]

            tokenStart = firstCharIdx+startChar
            printedCharIdx = tokenStart + length


            token = pygments.token.Name         # TODO map more precise/diverse

            #print("actual token");
            yield tokenStart, token, text[tokenStart:printedCharIdx]

        # FIXME print tail if its not a token
        if printedCharIdx < len(text):
            #print("tail token");
            yield firstCharIdx, None, text[firstCharIdx:len(text)]