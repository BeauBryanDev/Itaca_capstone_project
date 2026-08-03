// Static list of company sizes consumed by the form via .map().
// The `value` strings must match the backend `CompanySize` enum exactly
// (app/schemas/request.py). Note "Pequena" without the tilde: the enum value
// is unaccented even though the label shown to the user is not.
export const companySizes = [
  { value: "Micro", label: "Microempresa (1-10 empleados)" },
  { value: "Pequena", label: "Pequeña (11-50 empleados)" },
  { value: "Mediana", label: "Mediana (51-200 empleados)" },
  { value: "Grande", label: "Grande (200+ empleados)" },
];
