// Reusable indicator card (Nivel de madurez, Puntaje, Percentil...).
// Supports an optional gold badge, a numeric value with a suffix,
// a description and arbitrary children (e.g. a small chart).
function StatCard({ label, badge, value, suffix, description, children }) {
  return (
    <div className="flex flex-col rounded-2xl bg-itaca-panel p-5 shadow-card">
      <span className="text-[13px] font-medium text-itaca-subtext">
        {label}
      </span>

      {badge && (
        <span className="mt-2 inline-flex w-fit items-center rounded-lg bg-itaca-gold px-4 py-1.5 text-[15px] font-bold uppercase tracking-wide text-black/85">
          {badge}
        </span>
      )}

      {value !== undefined && (
        <div className="mt-1 flex items-baseline gap-1">
          <span className="text-[30px] font-bold leading-none text-itaca-text">
            {value}
          </span>
          {suffix && (
            <span className="text-[16px] font-medium text-itaca-subtext">
              {suffix}
            </span>
          )}
        </div>
      )}

      {children && <div className="mt-2">{children}</div>}

      {description && (
        <p className="mt-2 text-[13px] leading-relaxed text-itaca-subtext">
          {description}
        </p>
      )}
    </div>
  );
}

export default StatCard;
