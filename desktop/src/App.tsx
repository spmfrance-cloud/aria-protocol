import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import DesignSystem from "./pages/DesignSystem";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/design" element={<DesignSystem />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
