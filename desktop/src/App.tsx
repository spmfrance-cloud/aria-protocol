import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import DesignSystem from "./pages/DesignSystem";
import Models from "./pages/Models";
import Chat from "./pages/Chat";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/models" element={<Models />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/design" element={<DesignSystem />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
