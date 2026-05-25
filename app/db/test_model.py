from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# 1. 导入你的基类和刚才修改好的模型
# (请根据你项目的实际目录结构修改导入路径)
from app.db.base import Base
from app.models.conversation import Conversation, Message

# 2. 创建一个内存中的 SQLite 引擎（运行完自动销毁，不污染生成环境）
engine = create_engine("sqlite:///:memory:", echo=True)  # echo=True 会打印出它生成的 SQL 语句

# 3. 创建会话工厂
SessionLocal = sessionmaker(bind=engine)


def test_sqlalchemy_models():
    print("====== 1. 开始测试：在数据库中创建表结构 ======")
    # 这里会测试你的 mapped_column 语法是否能正常翻译成 SQL 建表语句
    Base.metadata.create_all(bind=engine)
    print("🎉 表结构创建成功！\n")

    db = SessionLocal()
    try:
        print("====== 2. 开始测试：插入测试数据 ======")
        # 创建一个对话
        new_conv = Conversation(
            user_id=1,
            session_id="session_abc_123",
            title="AI 助手技术咨询"
        )
        db.add(new_conv)
        db.flush()  # 触发生成 conv 的 id，此时还没提交事务

        # 创建两条属于该对话的消息（验证一对多逻辑关联）
        msg1 = Message(conversation_id=new_conv.id, role="user", content="你好，请问什么是 SQLAlchemy 2.0？")
        msg2 = Message(conversation_id=new_conv.id, role="assistant", content="那是一个非常强大的 Python ORM 框架！")
        db.add_all([msg1, msg2])
        db.commit()
        print("🎉 测试数据插入并提交成功！\n")

        print("====== 3. 开始测试：验证无外键的 relationship 逻辑关联 ======")
        # 清空会话缓存，强迫它必须从数据库重新读取，以验证关系是否真的生效
        db.expire_all()

        # 查询刚才创建的对话
        stmt = select(Conversation).where(Conversation.session_id == "session_abc_123")
        conv = db.execute(stmt).scalar_one()

        print(f"👉 成功查到对话标题: {conv.title}")
        print(f"👉 尝试读取它关联的消息（预期应该有 2 条）:")

        # 🌟 如果你在关系里的 Lambda 写错了，代码在运行到这一行循环时会直接报错
        for idx, message in enumerate(conv.messages, 1):
            print(f"   [{idx}] 角色: {message.role} | 内容: {message.content}")

        assert len(conv.messages) == 2, "❌ 错误：关联的消息数量不对！"
        print("\n🏆 【全部测试通过！】你的 SQLAlchemy 2.0 模型修改完美无误！")

    except Exception as e:
        print(f"\n❌ 【测试失败！】捕捉到异常错误: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    test_sqlalchemy_models()