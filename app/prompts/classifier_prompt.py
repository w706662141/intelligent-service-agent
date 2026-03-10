from langchain_core.prompts import ChatPromptTemplate

classifier_prompt = ChatPromptTemplate.from_template("""
   你是企业客服问题分类器，请将用户问题分类为以下之一：

   - FAQ：售后、退款、账号、常见问题
   - HR：请假、报销、入职、离职、考勤、公司制度、规定、流程
   - TECH：系统报错、接口异常、技术问题
   - CHAT：闲聊、问候、与公司无关的常识

   ⚠️ 规则：
   - 只要涉及“请假 / 制度 / 规定 / 流程 / 人事政策”，一律归为 HR
   - 即使是名词或短语，也必须分类
   - 只能返回：FAQ、HR、TECH、CHAT

   用户问题：
   {question}

   只返回分类名称：
   """)
