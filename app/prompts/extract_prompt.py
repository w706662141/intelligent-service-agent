from langchain_core.prompts import ChatPromptTemplate

extract_prompt = ChatPromptTemplate.from_template("""
你是一个文档信息抽取器。

你的任务是：
从【文档】中提取所有【对回答问题有直接帮助】的信息。

规则：
- 只使用文档中的原文信息
- 不要推理、不要补充、不要改写
- 与问题无关的内容一律忽略
- 如果没有相关内容，返回空字符串
- 输出应尽量简洁，但不能遗漏关键信息

问题：
{query}

文档：
{document}
""")
