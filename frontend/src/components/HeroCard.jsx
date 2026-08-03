import { ShieldCheck } from "lucide-react";
import lighthouse from "../assets/lighthouse.svg";
import processIcon from "../assets/process.svg";

// Left-hand presentation card on the diagnosis page.
// Hidden on mobile (only visible from the lg breakpoint up).
function HeroCard() {
  return (
    <aside className="relative hidden flex-col justify-between overflow-hidden rounded-2xl bg-itaca-panel p-7 shadow-card lg:flex">
      {/* Decorative lighthouse watermark, desktop only. */}
      <img
        src={lighthouse}
        alt=""
        aria-hidden="true"
        className="pointer-events-none absolute -right-10 -top-8 w-64 select-none opacity-10"
      />

      <div className="relative">
        <h1 className="text-[32px] font-bold leading-tight text-itaca-text">
          Autodiagnóstico
          <br />
          Empresarial
        </h1>
        <p className="mt-3 text-[15px] leading-relaxed text-itaca-subtext">
          Descubre el nivel de madurez digital de tu empresa en pocos minutos.
        </p>

        {/* Simple decorative illustration built with inline SVG (no assets) */}
        <div className="mt-8 flex items-center justify-center">
          <svg viewBox="0 0 260 170" className="w-full max-w-[260px]">
            <rect x="35" y="30" width="190" height="105" rx="8" fill="#1f2325" />
            <rect x="35" y="30" width="190" height="20" rx="8" fill="#1393B2" opacity="0.35" />
            <circle cx="70" cy="90" r="26" fill="none" stroke="#1393B2" strokeWidth="10" />
            <path d="M70 64 A26 26 0 0 1 96 90 L70 90 Z" fill="#998000" />
            <rect x="120" y="100" width="14" height="24" rx="3" fill="#1393B2" />
            <rect x="140" y="86" width="14" height="38" rx="3" fill="#998000" />
            <rect x="160" y="72" width="14" height="52" rx="3" fill="#B50F19" />
            <rect x="180" y="94" width="14" height="30" rx="3" fill="#1393B2" />
            <rect x="20" y="135" width="220" height="10" rx="5" fill="#2f3335" />
          </svg>
        </div>

        {/* Fills the gap between the chart art and the security note. */}
        <div className="mt-6 flex items-center justify-center gap-3">
          <img
            src={processIcon}
            alt=""
            aria-hidden="true"
            className="h-14 w-14 shrink-0 select-none"
          />
          <p className="max-w-[220px] text-[13px] leading-relaxed text-itaca-subtext">
            Analizamos tus procesos y presupuesto para ubicarte en uno de los
            cuatro niveles de madurez.
          </p>
        </div>
      </div>

      <div className="relative mt-8 rounded-xl border border-white/5 bg-itaca-bg/60 p-4">
        <div className="flex items-center gap-2 text-itaca-blue">
          <ShieldCheck className="h-5 w-5" />
          <span className="text-[15px] font-semibold text-itaca-text">
            Seguro y confidencial
          </span>
        </div>
        <p className="mt-1.5 text-[13px] leading-relaxed text-itaca-subtext">
          Tu información está protegida con los más altos estándares de
          seguridad.
        </p>
      </div>
    </aside>
  );
}

export default HeroCard;
