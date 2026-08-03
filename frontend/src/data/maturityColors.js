// Color per maturity level, shared by every chart so the four frozen classes
// read the same everywhere. Follows the reference mockup, except Inicial,
// which uses the institutional red.
export const maturityColors = {
  Inicial: "#B50F19",
  "En Desarrollo": "#1393B2",
  Definido: "#998000",
  Optimizado: "#3FA45B",
};

// Used when a name outside the four frozen classes arrives.
export const unknownLevelColor = "#9AA0A2";
