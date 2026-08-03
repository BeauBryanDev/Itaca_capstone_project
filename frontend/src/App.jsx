import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./layouts/MainLayout.jsx";
import DiagnosisPage from "./pages/DiagnosisPage.jsx";
import LoadingPage from "./pages/LoadingPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";

function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<DiagnosisPage />} />
        <Route path="/procesando" element={<LoadingPage />} />
        <Route path="/resultados" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
