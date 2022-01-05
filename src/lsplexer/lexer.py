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
            print('lspPygment: '+line)
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

        # save text to temporary file

        temp_dir = tempfile.TemporaryDirectory()
        fo = open(temp_dir.name+"/sheets_of_empty_canvas.jimple", "x")
        fo.write( text )
        fo.close()

        print('file written to '+ fo.name)

        # initialize lsp connection
        # TODO: incorporate lsplocation/command
        p = subprocess.Popen(['java', '-jar', self.lsplocation], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        read_pipe = ReadPipe(p.stderr)
        read_pipe.start()
        json_rpc_endpoint = pylspclient.JsonRpcEndpoint(p.stdin, p.stdout)
        # To work with socket: sock_fd = sock.makefile()
        lsp_endpoint = CustomLspEndpoint(json_rpc_endpoint)

        lsp_client = CustomLspClient(lsp_endpoint)
        root_uri = 'file://'+temp_dir.name
        workspace_folders = [{'name': 'LspCanvas', 'uri': root_uri}]
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
        lsp_client.initialize(p.pid, root_uri, root_uri, None, capabilities, "off", workspace_folders)
        lsp_client.initialized()
        #print("initialized - let the fun begin")
        time.sleep(1);          # TODO: quickfix/hack for jimplelsp - remove later!

        uri = "file://" + fo.name
        languageId = self.filetype
        version = 1

        #TODO: improvable: config flag: lsp server acccesses the file (ie needs a temporary file on the filesystem) or caches a current file snapshot via the didopen/didcheange notifications - saves hdd/sdd io
        #lsp_client.didOpen(pylspclient.lsp_structs.TextDocumentItem(uri, languageId, version, text))

        data = lsp_client.semantic_token( pylspclient.lsp_structs.TextDocumentIdentifier(uri) );

        lsp_client.shutdown()
        # wait a moment
        lsp_client.exit()
        # cleanup temp dir
        temp_dir.cleanup()


        lastTokenEnd = 0;
        # translate/map response to pygment tokentypes
        # assume the semantic tokens are sorted ascending by startindex
        for startLine, startChar, length, tokenType, tokenModifier in data:
            index = lastTokenEnd+startChar
            token = pygments.token.Name         # TODO be more precise
            lastTokenEnd = index+length
            value = data[index:(lastTokenEnd)]
            # if there is a gap between token and the next token... use Token.Text ?
            yield index, token, value
