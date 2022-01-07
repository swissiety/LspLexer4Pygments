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
            print('LspLexer4Pygment: '+line)
            line = self.pipe.readline().decode('utf-8')





class LspLexer(Lexer):

    name = 'LspLexer'
    aliases = ['lsp']
    filenames = []
    alias_filenames = []

    def __init__(self, **options):
        self.filetype = options.get('filetype', 'txt')
        self.lspcommand = options.get('lspcommand', '')

        if len(self.lspcommand) == '':
            raise Exception("No LSP Server specified! Please set the option lspcommand to an executable (command).");

        self.filenames = ['*.'+self.filetype ]

        Lexer.__init__(self, **options)


#    def get_tokens(text)
        #This method is the basic interface of a lexer. It is called by the highlight() function. It must process the text and return an iterable of (tokentype, value) pairs from text.
        #        Normally, you don’t need to override this method. The default implementation processes the stripnl, stripall and tabsize options and then yields all tokens from get_tokens_unprocessed(), with the index dropped.


    def map_token(self, semantictoken):
        # built in tokens https://pygments.org/docs/tokens/
        map = {
            'type' : pygments.token.Name.Class,
            'class': pygments.token.Name.Class,
            'enum' : pygments.token.Name.Class ,
            'interface' : pygments.token.Name.Class ,
            'struct' : pygments.token.Name.Class ,
            'typeParameter' : pygments.token.Name.Class ,
            'parameter' : pygments.token.Name ,
            'variable' : pygments.token.Name ,
             'property' : pygments.token.Name ,
             'enumMember' : pygments.token.Name ,
             'event' : pygments.token.Keyword ,
             'function' : pygments.token.Name.Function ,
             'method' : pygments.token.Name.Function ,
             'macro' : pygments.token.Keyword ,
             'keyword' : pygments.token.Keyword ,
             'modifier' : pygments.token.Keyword ,
             'comment' : pygments.token.Comment ,
             'string' : pygments.token.String ,
             'number' : pygments.token.Number ,
             'regexp' : pygments.token.String.Regex ,
             'operator': pygments.token.Operator
        }
        #print(semantictoken + " ->  "+ str(map.get(semantictoken)))
        return map.get(semantictoken)

    def get_tokens_unprocessed(self, text):
        #This method should process the text and return an iterable of (index, tokentype, value) tuples where index is the starting position of the token within the input text.
        #This method must be overridden by subclasses.

        print("prepare lsp connection for pygmentizing "+ self.filetype);

        # initialize lsp connection
        # TODO: incorporate lsplocation/command
        p = subprocess.Popen(self.lspcommand.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

            uri = 'file://' + tempfile.gettempdir() + '/file-does-not-exist-anywhere.'+self.filetype
            languageId = self.filetype
            version = 1
            lsp_client.didOpen(pylspclient.lsp_structs.TextDocumentItem(uri, languageId, version, text))

        else:
            # no sync -> save text to a temporary file
            temp_dir = tempfile.TemporaryDirectory()
            fo = open(temp_dir.name+'/sheet_of_empty_canvas.'+self.filetype, 'w')
            fo.write( text )
            fo.close()
            print('file written to '+ fo.name)
            lsp_client.initialized()
            uri = 'file://' + fo.name

        data, legend = lsp_client.semantic_token( pylspclient.lsp_structs.TextDocumentIdentifier(uri) )

        lsp_client.shutdown()
        lsp_client.exit()

        # cleanup temp dir if used
        if temp_dir is not None:
            temp_dir.cleanup()

        if data is None:    # return whole input as a token
            return 0, pygments.token.Text, data

        lineNo = 0
        firstCharIdx = 0
        printedCharIdx = 0

        # translate/map response to pygment tokentypes
        # assume the semantic tokens are sorted ascending by startindex
        for startLine, startCharInLine, length, tokenType, tokenModifier in legend.transformTokenInts(data):

            #print("\n["+str(startLine)+":"+str(startCharInLine)+"] "+ str(length)+ "   -> "+ tokenType )

            #handle lines between tokens aka token gaps -> move "cursor" to the line of the semantic token
            while lineNo < startLine:
                firstCharIdx = text.find('\n', firstCharIdx)+1    # beginning idx of the newline
                lineNo += 1
                yield printedCharIdx, pygments.token.Text, text[printedCharIdx:firstCharIdx]  # print the line
         #       print("line token"+ str(printedCharIdx) + " to " + str(firstCharIdx));
                printedCharIdx = firstCharIdx

            tokenStart = firstCharIdx+startCharInLine

            # add gaps in the text which have no token as token (from semantic token or lines)
            if printedCharIdx < tokenStart:  # is already on the same line
                yield printedCharIdx, pygments.token.Text, text[ printedCharIdx:tokenStart]
        #        print("gap token" + str(printedCharIdx) + " to " + str(tokenStart));

            if tokenStart >= printedCharIdx:        # filter overlaps which would result in more output than there was input -> skip token then
                printedCharIdx = tokenStart + length
                yield tokenStart, self.map_token( tokenType ), text[tokenStart:printedCharIdx]
          #  print("actual token" + str(tokenStart) + " to " + str(printedCharIdx) );

        # print tail if its not already a token
        if printedCharIdx < len(text):
            yield printedCharIdx, pygments.token.Text, text[printedCharIdx:len(text)]
            #print("tail token"  + str(printedCharIdx) + " to " + str(len(text)) );
