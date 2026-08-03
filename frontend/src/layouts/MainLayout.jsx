import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import Footer from "../components/Footer.jsx";
import BottomNav from "../components/BottomNav.jsx";

// Shared shell: navbar on top, routed page in the middle, footer at the
// bottom, plus the mobile bottom tab bar.
function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-itaca-bg">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <BottomNav />
    </div>
  );
}

export default MainLayout;
