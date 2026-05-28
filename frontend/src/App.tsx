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
      {/* 顶部导航栏 */}
      <div style={{ position: "fixed", top: 0, right: 0, zIndex: 1000, padding: "8px 16px", background: "rgba(255,255,255,0.9)", backdropFilter: "blur(4px)", borderRadius: "0 0 0 8px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}>
        <Space>
          <span style={{ fontWeight: 600 }}>{auth.username}</span>
          {isAdmin && <span style={{ color: "#faad14", fontSize: 12 }}>[管理员]</span>}
          <Link to="/chat"><Button size="small" icon={<MessageOutlined />}>聊天</Button></Link>
          {isAdmin && <Link to="/admin/users"><Button size="small" icon={<SettingOutlined />}>管理</Button></Link>}
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
