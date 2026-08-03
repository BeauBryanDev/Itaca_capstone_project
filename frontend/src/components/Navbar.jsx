import { useState } from "react";
import { NavLink } from "react-router-dom";
import { BarChart3, Menu, X, User, ClipboardList, Home, Mail } from "lucide-react";
import MobileMenu from "./MobileMenu.jsx";

// Items with `href` point at the client's public site and open in a new tab;
// items with `to` are internal router links.
const navItems = [
  {
    label: "Inicio",
    href: "https://proyectoitaca.co/quienes-somos/",
    icon: Home,
  },
  { label: "Diagnóstico", to: "/", exact: true, icon: ClipboardList },
  {
    label: "Contacto",
    href: "https://proyectoitaca.co/contactanos-en-nuestra-oficina/",
    icon: Mail,
  },
];

const linkBase =
  "relative text-[15px] font-medium text-white/90 transition-colors hover:text-white";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40">
      <div className="bg-itaca-blue">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6 lg:px-8">
          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-2 text-white">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15">
              <BarChart3 className="h-5 w-5" />
            </span>
            <span className="text-[17px] font-bold tracking-tight">
              ÍTACA SmartDiag
            </span>
          </NavLink>

          {/* Desktop navigation */}
          <nav className="hidden items-center gap-8 lg:flex">
            {navItems.map((item) =>
              item.href ? (
                <a
                  key={item.label}
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={linkBase}
                >
                  {item.label}
                </a>
              ) : (
                <NavLink
                  key={item.label}
                  to={item.to}
                  end={item.exact}
                  className={({ isActive }) =>
                    linkBase +
                    (isActive && item.label === "Diagnóstico"
                      ? " text-white after:absolute after:-bottom-1.5 after:left-0 after:h-0.5 after:w-full after:rounded-full after:bg-white"
                      : "")
                  }
                >
                  {item.label}
                </NavLink>
              )
            )}
          </nav>

          {/* Avatar + hamburger */}
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15 text-white">
              <User className="h-5 w-5" />
            </span>
            <button
              type="button"
              aria-label="Abrir menú"
              onClick={() => setMenuOpen((v) => !v)}
              className="flex h-9 w-9 items-center justify-center rounded-lg text-white hover:bg-white/10 lg:hidden"
            >
              {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        <MobileMenu
          open={menuOpen}
          items={navItems}
          onClose={() => setMenuOpen(false)}
        />
      </div>
    </header>
  );
}

export default Navbar;
