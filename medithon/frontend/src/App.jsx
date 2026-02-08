import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ChatPage from "./pages/ChatPage";
import DrugExplorer from "./pages/DrugExplorer";
import WebSearch from "./pages/WebSearch";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<ChatPage />} />
        <Route path="/drugs" element={<DrugExplorer />} />
        <Route path="/search" element={<WebSearch />} />
      </Route>
    </Routes>
  );
}
