from app.query.QueryRewriteResult import QueryRewriteResult
# from app.query.prompts import QUERY_REWRITE_PROMPT
from app.prompts.task.rewrite import QUERY_REWRITE_PROMPT


class QueryRewriter:
    def __init__(self, llm):
        self.llm = llm

    def rewrite(self, question: str) -> QueryRewriteResult:
        prompt = QUERY_REWRITE_PROMPT.format(question=question)

        try:
            resp = self.llm.invoke(prompt)
            rewritten = resp.content.strip()
        except Exception as e:
            return QueryRewriteResult(
                original=question,
                rewritten=question,
                reason=f"llm_error:_{e}"
            )

        # 安全兜底：太短 / 空 / 和原始差异过大

        if not rewritten or len(rewritten) < 5:
            rewritten = question
            reason = 'rewrite_invalid'
        else:
            reason = "rewrite_success"

        return QueryRewriteResult(
            original=question,
            rewritten=rewritten,
            reason=reason
        )
