// Static list of business sectors consumed by the form via .map().
// The `value` strings must match the backend `Sector` enum exactly
// (app/schemas/request.py): unaccented and capitalized. Only `label` is
// translated for display.
export const sectors = [
  { value: "Tecnologia", label: "Tecnología" },
  { value: "Manufactura", label: "Manufactura" },
  { value: "Retail", label: "Retail" },
  { value: "Servicios", label: "Servicios" },
];
