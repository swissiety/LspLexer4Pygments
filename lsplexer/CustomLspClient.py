from pylspclient import LspClient
from pylspclient.lsp_structs import to_type


class SemanticTokenLegend(object):
    def __init__(self, tokenTypes, tokenModifiers):
        self.tokenTypes = tokenTypes
        self.tokenModifiers = tokenModifiers

    @staticmethod
    def iterate_set_bits(n):
        while n:
            b = n & (~n+1)
            yield b
            n ^= b

    def transformTokenInts(self, data):

        #at index 5*i - deltaLine: token line number, relative to the previous token
        #at index 5*i+1 - deltaStart: token start character, relative to the previous token (relative to 0 or the previous token’s start if they are on the same line)
        #at index 5*i+2 - length: the length of the token.
        #at index 5*i+3 - tokenType: will be looked up in SemanticTokensLegend.tokenTypes. We currently ask that tokenType < 65536.
        #at index 5*i+4 - tokenModifiers: each set bit will be looked up in SemanticTokensLegend.tokenModifiers

        lineIdx = 0
        charIdx = 0

        i = 0
        while i < len(data):

            if data[i] < 0 or data[i+1] < 0:
                #print("skip negative relation i.e. unordered tokens.")
                i+=5
                continue

            if data[i] == 0 and data[i+1] == 0:
                #print("skip overlapping token starts")
                i+=5
                continue

            # merge set of modifiers
            modifiers = {}
            for b in self.iterate_set_bits(data[i + 4]):
                modifiers.update(self.tokenModifiers[b])

            lineIdx += data[i]

            if data[i] == 0:   # token on same line as the last token
                charIdx += data[i+1]
            else:
                charIdx = data[i+1]

            yield lineIdx, charIdx, data[i + 2], self.tokenTypes[data[i + 3]], modifiers
            i += 5



class CustomLspClient(LspClient):

    def __init__(self, lsp_endpoint):
        super().__init__(lsp_endpoint)
        self.tokenLegend = None

    def initialize(self, processId, rootUri, rootPath, initializationOptions, capabilities, trace, workspaceFolders):
        result = super().initialize(processId, rootUri, rootPath, initializationOptions, capabilities, trace, workspaceFolders)

        if 'semanticTokensProvider' not in result['capabilities']:
            print('Semantic tokens are not supported by the given LSP server.')
            return result

        self.tokenLegend = to_type(result['capabilities']['semanticTokensProvider']['legend'], SemanticTokenLegend)
        return result

    def semantic_token(self, textDocument):
        if self.tokenLegend == None:
            return None, None

        result = self.lsp_endpoint.call_method('textDocument/semanticTokens/full', textDocument=textDocument)
        return result, self.tokenLegend
