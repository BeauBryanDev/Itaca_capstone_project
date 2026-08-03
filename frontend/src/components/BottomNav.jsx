import { NavLink } from "react-router-dom";
import { ClipboardList, Home, Mail } from "lucide-react";

// Mirrors the Navbar items: `href` tabs leave for the client's public site.
const tabs = [
  { label: "Diagnóstico", to: "/", icon: ClipboardList, active: true },
  {
    label: "Inicio",
    href: "https://proyectoitaca.co/quienes-somos/",
    icon: Home,
    active: false,
  },
  {
    label: "Contacto",
    href: "https://proyectoitaca.co/contactanos-en-nuestra-oficina/",
    icon: Mail,
    active: false,
  },
];

// Bottom tab navigation shown only on mobile, matching the reference mockups.
function BottomNav() {
  return (
    <nav className="border-t border-white/10 bg-itaca-blue lg:hidden">
      <div className="flex items-stretch justify-around">
        {tabs.map((tab) => {
          const className =
            "flex flex-1 flex-col items-center gap-1 py-2.5 text-[12px] font-medium transition-colors " +
            (tab.active ? "text-white" : "text-white/70 hover:text-white");

          return tab.href ? (
            <a
              key={tab.label}
              href={tab.href}
              target="_blank"
              rel="noopener noreferrer"
              className={className}
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </a>
          ) : (
            <NavLink key={tab.label} to={tab.to} className={className}>
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}

export default BottomNav;
