import { useState } from "react";
import {
  Building2,
  Network,
  Users,
  FileText,
  DollarSign,
  MessageSquare,
  HeartHandshake,
  RefreshCw,
} from "lucide-react";

import Input from "./Input.jsx";
import Button from "./Button.jsx";
import { useDiagnosis } from "../hooks/useDiagnosis.js";
import { sectors } from "../data/sectors.js";
import { companySizes } from "../data/companySizes.js";

// Centralizes all form logic: state, validation and submit.
function CompanyForm({ onSubmit }) {
  const { formData, updateField } = useDiagnosis();
  const [errors, setErrors] = useState({});

  function handleChange(event) {
    const { name, value } = event.target;
    updateField(name, value);
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  }

  function validate() {
    const nextErrors = {};
    if (!formData.companyName.trim())
      nextErrors.companyName = "Ingresa el nombre de la empresa.";
    if (!formData.companySector)
      nextErrors.companySector = "Selecciona un sector.";
    if (!formData.companySize)
      nextErrors.companySize = "Selecciona el tamaño de la empresa.";

    const processes = Number(formData.documentedProcesses);
    if (formData.documentedProcesses === "")
      nextErrors.documentedProcesses = "Ingresa un valor entre 0.00 y 1.00.";
    else if (Number.isNaN(processes) || processes < 0 || processes > 1)
      nextErrors.documentedProcesses = "Debe estar entre 0.00 y 1.00.";

    // Thousands separators are allowed in the input ("50.000.000").
    const budget = Number(String(formData.annualBudget).replace(/[.\s]/g, ""));
    if (formData.annualBudget === "")
      nextErrors.annualBudget = "Ingresa el presupuesto anual.";
    else if (Number.isNaN(budget))
      nextErrors.annualBudget = "Ingresa un valor numérico.";
    else if (!Number.isInteger(budget))
      nextErrors.annualBudget = "Ingresa un valor entero, sin decimales.";
    else if (budget <= 100000)
      // Mirrors the backend constraint annual_tech_budget > 100000.
      nextErrors.annualBudget = "Debe ser mayor a 100.000.";

    if (!formData.openAnswer.trim())
      nextErrors.openAnswer = "Cuéntanos brevemente sobre tu empresa.";

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  }

  return (
    <div className="rounded-2xl bg-itaca-panel p-6 shadow-card sm:p-7">
      <h2 className="mb-5 text-[20px] font-bold text-itaca-blue">
        Información de tu empresa
      </h2>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <Input
          label="Nombre de la empresa"
          name="companyName"
          value={formData.companyName}
          onChange={handleChange}
          placeholder="Ej. TechSolutions SAS"
          required
          icon={Building2}
          error={errors.companyName}
        />

        <Input
          label="Sector"
          name="companySector"
          as="select"
          value={formData.companySector}
          onChange={handleChange}
          placeholder="Selecciona un sector"
          required
          icon={Network}
          options={sectors}
          error={errors.companySector}
        />

        <Input
          label="Tamaño de la empresa"
          name="companySize"
          as="select"
          value={formData.companySize}
          onChange={handleChange}
          placeholder="Selecciona el tamaño"
          required
          icon={Users}
          options={companySizes}
          error={errors.companySize}
        />

        <Input
          label="Porcentaje de procesos documentados (0.00 - 1.00)"
          name="documentedProcesses"
          value={formData.documentedProcesses}
          onChange={handleChange}
          placeholder="Ej. 0.35"
          required
          icon={FileText}
          helper="Ej: 0.35 = 35%"
          error={errors.documentedProcesses}
        />

        <Input
          label="Presupuesto anual en tecnología (COP)"
          name="annualBudget"
          value={formData.annualBudget}
          onChange={handleChange}
          placeholder="Ej. 50.000.000"
          required
          icon={DollarSign}
          helper="Mínimo sugerido: > 100.000"
          error={errors.annualBudget}
        />

        <Input
          label="Respuesta abierta"
          name="openAnswer"
          as="textarea"
          value={formData.openAnswer}
          onChange={handleChange}
          placeholder="Cuéntanos brevemente cómo maneja tu empresa sus procesos y tecnología..."
          required
          icon={MessageSquare}
          error={errors.openAnswer}
        />

        <Input
          label="Labor social (opcional)"
          name="socialWork"
          as="textarea"
          value={formData.socialWork}
          onChange={handleChange}
          placeholder="Describe las iniciativas o programas sociales que realiza tu empresa..."
          icon={HeartHandshake}
        />

        {/* The LLM layer is billed per call, so it stays opt-in. */}
        <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-white/10 p-3.5 transition-all duration-300 hover:border-itaca-blue/50">
          <input
            type="checkbox"
            name="personalize"
            checked={formData.personalize}
            onChange={(event) => updateField("personalize", event.target.checked)}
            className="mt-0.5 h-4 w-4 shrink-0 accent-itaca-red"
          />
          <span className="text-[14px] leading-relaxed text-itaca-subtext">
            Personalizar la recomendación con IA
            <span className="block text-[13px] text-itaca-subtext/70">
              Adapta la redacción a tu respuesta abierta. Puede tardar unos
              segundos más.
            </span>
          </span>
        </label>

        <Button type="submit" icon={RefreshCw} className="mt-2 w-full">
          DIAGNÓSTICO
        </Button>
      </form>
    </div>
  );
}

export default CompanyForm;
