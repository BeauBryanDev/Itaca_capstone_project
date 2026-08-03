import { Loader2 } from "lucide-react";

// Reusable button. The primary variant uses the institutional red (#B50F19).
// Passing `href` renders an <a> with the same styling instead of a <button>.
function Button({
  children,
  variant = "primary",
  type = "button",
  loading = false,
  disabled = false,
  icon: Icon = null,
  href = "",
  className = "",
  ...props
}) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 " +
    "font-semibold text-[15px] transition-all duration-300 focus:outline-none " +
    "focus:ring-2 focus:ring-offset-2 focus:ring-offset-itaca-panel " +
    "disabled:opacity-60 disabled:cursor-not-allowed";

  const variants = {
    primary:
      "bg-itaca-red text-white hover:brightness-110 active:scale-[0.98] " +
      "focus:ring-itaca-red shadow-card",
    outline:
      "border border-itaca-red text-itaca-red hover:bg-itaca-red " +
      "hover:text-white active:scale-[0.98] focus:ring-itaca-red",
    ghost:
      "text-itaca-subtext hover:text-white hover:bg-white/5 focus:ring-white/20",
  };

  const content = (
    <>
      {loading ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : (
        Icon && <Icon className="h-5 w-5" />
      )}
      {children}
    </>
  );

  const classes = `${base} ${variants[variant]} ${className}`;

  if (href) {
    return (
      <a href={href} className={classes} {...props}>
        {content}
      </a>
    );
  }

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={classes}
      {...props}
    >
      {content}
    </button>
  );
}

export default Button;
