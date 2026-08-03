# ÍTACA SmartDiag — Frontend

Aplicación web responsive para el autodiagnóstico empresarial de ÍTACA
SmartDiag. SPA de tres vistas (Formulario → Carga → Dashboard) construida
con React 18, Vite y TailwindCSS.

## Stack

- React 18 + Vite
- TailwindCSS 3.4.7
- React Router DOM (navegación SPA)
- Axios (cliente HTTP)
- Recharts (gráficas)
- Lucide React (iconografía)

## Requisitos

- Node.js 22 (incluye npm)

## Instalación

```bash
npm install
```

## Comandos

| Comando           | Descripción                              |
| ----------------- | ---------------------------------------- |
| `npm run dev`     | Servidor de desarrollo (http://localhost:5173) |
| `npm run build`   | Compilación de producción en `dist/`     |
| `npm run preview` | Previsualiza la build de producción      |
| `npm run lint`    | Ejecuta ESLint sobre `src`               |

## Estructura

```
src/
├── assets/        # imágenes, iconos y logo
├── components/    # componentes reutilizables (Navbar, CompanyForm, charts...)
├── layouts/       # MainLayout (navbar + footer + bottom nav)
├── pages/         # DiagnosisPage, LoadingPage, DashboardPage
├── services/      # api.js (config Axios) + diagnosisService.js
├── store/         # DiagnosisContext (estado global con React Context)
├── hooks/         # useDiagnosis
├── data/          # sectors.js, companySizes.js (listas estáticas)
├── App.jsx        # definición de rutas
├── main.jsx       # punto de entrada
└── styles.css     # Tailwind + estilos base
```

## Backend

La comunicación se hace con Axios en `src/services`. La URL base se toma de la
variable de entorno `VITE_API_URL` (por defecto `http://localhost:8000/api`).
Mientras el backend no esté disponible, el flujo usa datos de ejemplo
(`buildMockResults`) para que la aplicación sea navegable de principio a fin.

Endpoints esperados:

- `POST /diagnosis` → `submitDiagnosis()`
- `GET /diagnosis/:id` → `getDiagnosis()`
- `GET /diagnosis/:id/recommendation` → `getRecommendation()`

## Paleta institucional

| Uso              | HEX       |
| ---------------- | --------- |
| Header / Footer  | `#1393B2` |
| Fondo principal  | `#181A1B` |
| Paneles          | `#25282A` |
| Dorado (acentos) | `#998000` |
| Botones (rojo)   | `#B50F19` |
| Texto principal  | `#F5F5F5` |
| Texto secundario | `#E8E8E8` |
