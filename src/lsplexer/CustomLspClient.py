import json

import pylspclient
from pylspclient import lsp_structs, LspClient
import pylspclient
import subprocess
import threading

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
        deltaLine = 0
        deltaStart = 0

        #at index 5*i - deltaLine: token line number, relative to the previous token
        #at index 5*i+1 - deltaStart: token start character, relative to the previous token (relative to 0 or the previous token’s start if they are on the same line)
        #at index 5*i+2 - length: the length of the token.
        #at index 5*i+3 - tokenType: will be looked up in SemanticTokensLegend.tokenTypes. We currently ask that tokenType < 65536.
        #at index 5*i+4 - tokenModifiers: each set bit will be looked up in SemanticTokensLegend.tokenModifiers

        i = 0
        while i < len(data):

            # merge set of modifiers
            modifiers = {}
            for b in self.iterate_set_bits( data[5 * i + 4] ):
                modifiers.update( self.tokenModifiers[b] )

            yield ( data[5*i], data[5*i+1], data[5*i+2], self.tokenTypes[data[5*i+3]], modifiers)
            i += 5




class CustomLspClient(LspClient):

    def __init__(self, lsp_endpoint):
        super().__init__(lsp_endpoint)
        self.tokenLegend = None

    def initialize(self, processId, rootUri, rootPath, initializationOptions, capabilities, trace, workspaceFolders):
        result = super().initialize(processId, rootUri, rootPath, initializationOptions, capabilities, trace, workspaceFolders)

        # TODO: if dict element does not exist there is no semantik token support at all! -> error handling!
        self.tokenLegend = to_type(result["capabilities"]["semanticTokensProvider"]["legend"], SemanticTokenLegend)
        return result

    def semantic_token(self, textDocument):
        result = self.lsp_endpoint.call_method("textDocument/semanticTokens/full", textDocument=textDocument)
        if result is None:
            yield from ()

        json.dumps(result)

        return self.tokenLegend.transformTokenInts(result["data"])

