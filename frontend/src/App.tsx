import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Newsfeed from "./pages/Newsfeed";
import AITools from "./pages/AITools";
import About from "./pages/About";
import Sources from "./pages/Sources";
import Admin from "./pages/Admin";
import "./styles.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Newsfeed />} />
        <Route path="/ai-tools" element={<AITools />} />
        <Route path="/about" element={<About />} />
        <Route path="/sources" element={<Sources />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Router>
  );
}

export default App;
