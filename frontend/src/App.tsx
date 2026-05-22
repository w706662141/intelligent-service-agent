import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  time: string;
}

interface Session {
  id: string;
  name: string;
  messages: Message[];
}

interface User {
  id: string;
  token: string;
  sessions: Session[];
  activeSessionId: string | null;
}

export default function App() {
  const [users, setUsers] = useState<User[]>([]);
  const [activeUserId, setActiveUserId] = useState<string | null>(null);
  const [newUserId, setNewUserId] = useState("");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [tokenStatus, setTokenStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const chatEndRef = useRef<HTMLDivElement>(null);

  const activeUser = users.find((u) => u.id === activeUserId) || null;
  const activeSession = activeUser
    ? activeUser.sessions.find((s) => s.id === activeUser.activeSessionId) || null
    : null;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeSession?.messages.length, activeSession?.messages[activeSession.messages.length - 1]?.content]);

  const addUser = async () => {
    const uid = newUserId.trim();
    if (!uid || users.some((u) => u.id === uid)) return;
    try {
      setTokenStatus("loading");
      const res = await fetch(`/token?user_id=${encodeURIComponent(uid)}`, {
        method: "POST",
      });
      const data = await res.json();
      const newUser: User = {
        id: uid,
        token: data.token,
        sessions: [],
        activeSessionId: null,
      };
      setUsers((prev) => [...prev, newUser]);
      setActiveUserId(uid);
      setNewUserId("");
      setTokenStatus("ok");
    } catch {
      setTokenStatus("error");
    }
  };

  const removeUser = (uid: string) => {
    setUsers((prev) => prev.filter((u) => u.id !== uid));
    if (activeUserId === uid) {
      setActiveUserId(null);
    }
  };

  const createSession = () => {
    if (!activeUserId) return;
    const id = `session-${Date.now()}`;
    const newSession: Session = { id, name: `会话`, messages: [] };
    setUsers((prev) =>
      prev.map((u) =>
        u.id === activeUserId
          ? {
              ...u,
              sessions: [...u.sessions, newSession],
              activeSessionId: id,
            }
          : u
      )
    );
  };

  const deleteSession = async (sessionId: string) => {
    if (!activeUser) return;
    try {
      await fetch("/session", {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${activeUser.token}`,
          "X-Session-Id": sessionId,
        },
      });
    } catch {
      // ignore
    }
    setUsers((prev) =>
      prev.map((u) =>
        u.id === activeUserId
          ? {
              ...u,
              sessions: u.sessions.filter((s) => s.id !== sessionId),
              activeSessionId:
                u.activeSessionId === sessionId ? null : u.activeSessionId,
            }
          : u
      )
    );
  };

  const sendMessage = async () => {
    if (!input.trim() || !activeSession || !activeUser || loading) return;

    const now = new Date().toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });

    const userMsg: Message = { role: "user", content: input, time: now };
    const sessionId = activeSession.id;
    setUsers((prev) =>
      prev.map((u) =>
        u.id === activeUserId
          ? {
              ...u,
              sessions: u.sessions.map((s) =>
                s.id === sessionId
                  ? { ...s, messages: [...s.messages, userMsg] }
                  : s
              ),
            }
          : u
      )
    );
    const question = input;
    setInput("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("question", question);

      const res = await fetch("/chat/stream", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${activeUser.token}`,
          "X-Session-Id": sessionId,
        },
        body: formData,
      });

      if (res.status === 401) {
        const botMsg: Message = {
          role: "assistant",
          content: "Token 已过期，请删除该用户后重新添加",
          time: new Date().toLocaleTimeString("zh-CN", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        };
        setUsers((prev) =>
          prev.map((u) =>
            u.id === activeUserId
              ? {
                  ...u,
                  sessions: u.sessions.map((s) =>
                    s.id === sessionId
                      ? { ...s, messages: [...s.messages, botMsg] }
                      : s
                  ),
                }
              : u
          )
        );
        return;
      }

      // 先插入一条空的 assistant 消息，后续逐块填充
      const time = new Date().toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
      });
      setUsers((prev) =>
        prev.map((u) =>
          u.id === activeUserId
            ? {
                ...u,
                sessions: u.sessions.map((s) =>
                  s.id === sessionId
                    ? { ...s, messages: [...s.messages, { role: "assistant", content: "", time }] }
                    : s
                ),
              }
            : u
        )
      );

      // 逐块读取 SSE 流
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop()!;

        for (const part of parts) {
          if (!part.startsWith("data: ")) continue;
          const payload = part.slice(6);
          if (payload === "[DONE]") continue;

          const { content } = JSON.parse(payload);

          setUsers((prev) =>
            prev.map((u) =>
              u.id === activeUserId
                ? {
                    ...u,
                    sessions: u.sessions.map((s) => {
                      if (s.id !== sessionId) return s;
                      const msgs = [...s.messages];
                      const last = msgs[msgs.length - 1];
                      if (last && last.role === "assistant") {
                        msgs[msgs.length - 1] = {
                          ...last,
                          content: last.content + content,
                        };
                      }
                      return { ...s, messages: msgs };
                    }),
                  }
                : u
            )
          );
        }
      }
    } catch {
      const errMsg: Message = {
        role: "assistant",
        content: "请求失败，请检查后端服务是否启动",
        time: new Date().toLocaleTimeString("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setUsers((prev) =>
        prev.map((u) =>
          u.id === activeUserId
            ? {
                ...u,
                sessions: u.sessions.map((s) =>
                  s.id === sessionId
                    ? { ...s, messages: [...s.messages, errMsg] }
                    : s
                ),
              }
            : u
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* 左侧栏 */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>智能客服 Agent</h1>
        </div>

        {/* 添加用户 */}
        <div className="token-section">
          <label>添加用户</label>
          <input
            value={newUserId}
            onChange={(e) => setNewUserId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addUser()}
            placeholder="输入用户ID"
          />
          <button className="btn-token" onClick={addUser} disabled={tokenStatus === "loading"}>
            {tokenStatus === "loading" ? "连接中..." : "登录"}
          </button>
          {tokenStatus === "ok" && <span className="token-ok">已添加</span>}
          {tokenStatus === "error" && <span className="token-error">失败</span>}
        </div>

        {/* 用户列表 */}
        <div className="user-section">
          <div className="session-header">
            <span>用户列表 ({users.length})</span>
          </div>
          <div className="session-list">
            {users.length === 0 && (
              <div className="session-empty">暂无用户</div>
            )}
            {users.map((u) => (
              <div
                key={u.id}
                className={`session-item ${u.id === activeUserId ? "active" : ""}`}
                onClick={() => setActiveUserId(u.id)}
              >
                <div className="session-info">
                  <span className="session-name">{u.id}</span>
                  <span className="session-count">{u.sessions.length} 个会话</span>
                </div>
                <button
                  className="btn-delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeUser(u.id);
                  }}
                >
                  x
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* 会话列表 */}
        {activeUser && (
          <div className="session-section">
            <div className="session-header">
              <span>{activeUser.id} 的会话</span>
              <button className="btn-new" onClick={createSession}>
                + 新建
              </button>
            </div>
            <div className="session-list">
              {activeUser.sessions.length === 0 && (
                <div className="session-empty">暂无会话</div>
              )}
              {activeUser.sessions.map((s) => (
                <div
                  key={s.id}
                  className={`session-item ${s.id === activeUser.activeSessionId ? "active" : ""}`}
                  onClick={() =>
                    setUsers((prev) =>
                      prev.map((u) =>
                        u.id === activeUserId
                          ? { ...u, activeSessionId: s.id }
                          : u
                      )
                    )
                  }
                >
                  <div className="session-info">
                    <span className="session-name">{s.name}</span>
                    <span className="session-count">{s.messages.length} 条</span>
                  </div>
                  <button
                    className="btn-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(s.id);
                    }}
                  >
                    x
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </aside>

      {/* 右侧对话区 */}
      <main className="chat-area">
        {!activeSession ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>
            <p>{activeUser ? "新建一个会话开始对话" : "请先添加用户"}</p>
          </div>
        ) : (
          <>
            <div className="chat-header">
              <h2>{activeSession.name}</h2>
              <span className="session-id">用户: {activeUserId} | {activeSession.id}</span>
            </div>

            <div className="chat-messages">
              {activeSession.messages.length === 0 && (
                <div className="message-hint">开始对话吧...</div>
              )}
              {activeSession.messages.map((msg, i) => (
                <div key={i} className={`message-row ${msg.role}`}>
                  <div className="message-bubble">
                    <div className="message-content">{msg.content}</div>
                    <div className="message-time">{msg.time}</div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message-row assistant">
                  <div className="message-bubble loading">
                    <span className="dot-typing"></span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="chat-input">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="输入问题..."
                disabled={loading}
              />
              <button
                className="btn-send"
                onClick={sendMessage}
                disabled={loading || !input.trim()}
              >
                发送
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
