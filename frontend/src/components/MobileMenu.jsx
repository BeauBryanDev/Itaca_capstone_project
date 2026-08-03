import { NavLink } from "react-router-dom";

const linkBase =
  "rounded-lg px-3 py-2.5 text-[15px] font-medium transition-colors";

// Dropdown menu shown on mobile when the hamburger button is toggled.
// Items carrying `href` render as external links (see Navbar navItems).
function MobileMenu({ open, items, onClose }) {
  if (!open) return null;

  return (
    <div className="border-t border-white/10 bg-itaca-blue lg:hidden">
      <nav className="flex flex-col px-6 py-3">
        {items.map((item) =>
          item.href ? (
            <a
              key={item.label}
              href={item.href}
              target="_blank"
              rel="noopener noreferrer"
              onClick={onClose}
              className={`${linkBase} text-white/90 hover:bg-white/10`}
            >
              {item.label}
            </a>
          ) : (
            <NavLink
              key={item.label}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                linkBase +
                (isActive && item.exact
                  ? " bg-white/15 text-white"
                  : " text-white/90 hover:bg-white/10")
              }
              end={item.exact}
            >
              {item.label}
            </NavLink>
          )
        )}
      </nav>
    </div>
  );
}

export default MobileMenu;
