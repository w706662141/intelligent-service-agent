class QueryRewriteResult:
    def __init__(self, original, rewritten, reason):
        self.original = original
        self.rewritten = rewritten
        self.reason = reason
