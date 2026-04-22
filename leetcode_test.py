from app.core.llm import get_model, get_compress_model

compress_llm = get_compress_model()
print(compress_llm.invoke('帮我压缩以下文本：员工发生差旅或业务相关费用后，应在出差或业务结束后 7 个工作日内提交报销申请。报销流程包括：填写报销单；上传合法有效的发票照片；经部门负责人审批'))