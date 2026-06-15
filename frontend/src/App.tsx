import { useState } from "react";
import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { Button, Space } from "antd";
import { LogoutOutlined, MessageOutlined, SettingOutlined } from "@ant-design/icons";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import AdminLayout from "./pages/admin/Layout";
import Users from "./pages/admin/Users";
import Roles from "./pages/admin/Roles";
import Permissions from "./pages/admin/Permissions";

interface AuthState {
  token: string;
  userId: number;
  username: string;
  roles: string[];
}

export default function App() {
  const [auth, setAuth] = useState<AuthState | null>(null);
  const navigate = useNavigate();

  const handleLogin = (token: string, userId: number, username: string, roles: string[]) => {
    setAuth({ token, userId, username, roles });
  };

  const handleLogout = () => {
    setAuth(null);
    navigate("/login");
  };

  const isAdmin = auth?.roles.includes("admin");

  if (!auth) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <>
      {/* Top navigation bar */}
      <div style={{
        position: "fixed",
        top: 0,
        right: 12,
        zIndex: 1000,
        padding: "6px 14px",
        background: "rgba(255,255,255,0.95)",
        backdropFilter: "blur(8px)",
        borderRadius: "8px",
        boxShadow: "0 1px 6px rgba(0,0,0,0.08)",
      }}>
        <Space size="small">
          <span style={{ fontSize: 13, color: "#555" }}>{auth.username}</span>
          {isAdmin && <span style={{ fontSize: 11, color: "#faad14", background: "#fffbe6", padding: "1px 6px", borderRadius: 4 }}>管理员</span>}
          <Link to="/chat">
            <Button size="small" icon={<MessageOutlined />}>聊天</Button>
          </Link>
          {isAdmin && (
            <Link to="/admin/users">
              <Button size="small" icon={<SettingOutlined />}>管理</Button>
            </Link>
          )}
          <Button size="small" danger icon={<LogoutOutlined />} onClick={handleLogout}>退出</Button>
        </Space>
      </div>
      <div style={{ paddingTop: 8 }}>
        <Routes>
          <Route path="/login" element={<Navigate to="/chat" />} />
          <Route path="/chat" element={<Chat token={auth.token} userId={auth.userId} username={auth.username} />} />
          <Route path="/admin" element={isAdmin ? <AdminLayout /> : <Navigate to="/chat" />}>
            <Route index element={<Navigate to="users" />} />
            <Route path="users" element={<Users token={auth.token} />} />
            <Route path="roles" element={<Roles token={auth.token} />} />
            <Route path="permissions" element={<Permissions token={auth.token} />} />
          </Route>
          <Route path="*" element={<Navigate to="/chat" />} />
        </Routes>
      </div>
    </>
  );
}
