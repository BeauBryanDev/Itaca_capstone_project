// Reusable field supporting text inputs, selects and textareas, all sharing
// the same dark styling, label, optional icon, helper text and error state.
function Input({
  label,
  name,
  value,
  onChange,
  type = "text",
  as = "input",
  placeholder = "",
  required = false,
  helper = "",
  error = "",
  icon: Icon = null,
  options = [],
  rows = 3,
}) {
  const fieldBase =
    "w-full rounded-xl bg-itaca-bg text-itaca-text placeholder-gray-500 " +
    "border transition-all duration-300 focus:outline-none focus:ring-2 " +
    "focus:ring-itaca-red/60 focus:border-itaca-red " +
    (Icon ? "pl-11 pr-4 " : "px-4 ") +
    (error ? "border-itaca-red " : "border-white/10 ");

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={name}
          className="mb-1.5 block text-[13px] font-medium text-itaca-subtext"
        >
          {label}
          {required && <span className="ml-1 text-itaca-red">*</span>}
        </label>
      )}

      <div className="relative">
        {Icon && (
          <Icon className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-itaca-blue" />
        )}

        {as === "select" && (
          <select
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            className={`${fieldBase} h-11 appearance-none pr-10`}
          >
            <option value="" disabled>
              {placeholder || "Selecciona una opción"}
            </option>
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )}

        {as === "textarea" && (
          <textarea
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            rows={rows}
            className={`${fieldBase} resize-none py-2.5`}
          />
        )}

        {as === "input" && (
          <input
            id={name}
            name={name}
            type={type}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            className={`${fieldBase} h-11`}
          />
        )}

        {/* Chevron for selects */}
        {as === "select" && (
          <svg
            className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-itaca-subtext"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M5.23 7.21a.75.75 0 011.06.02L10 11.17l3.71-3.94a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </div>

      {helper && !error && (
        <p className="mt-1 text-[12px] text-gray-500">{helper}</p>
      )}
      {error && <p className="mt-1 text-[12px] text-itaca-red">{error}</p>}
    </div>
  );
}

export default Input;
