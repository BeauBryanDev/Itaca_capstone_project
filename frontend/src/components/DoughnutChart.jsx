import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import {
  maturityColors as COLORS,
  unknownLevelColor,
} from "../data/maturityColors.js";

// Doughnut chart for the maturity distribution, with a custom legend that
// lists every level and its percentage (as in the mockups).
function DoughnutChart({ data = [] }) {

  return (
    <div className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between">
      <div className="h-52 w-52 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={58}
              outerRadius={86}
              paddingAngle={2}
              stroke="none"
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={COLORS[entry.name] || unknownLevelColor} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#25282A",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 10,
                color: "#F5F5F5",
                fontSize: 13,
              }}
              formatter={(value, name) => [`${value}%`, name]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Custom legend */}
      <ul className="flex w-full max-w-xs flex-col gap-3">
        {data.map((entry) => (
          <li
            key={entry.name}
            className="flex items-center justify-between text-[15px]"
          >
            <span className="flex items-center gap-2.5 text-itaca-subtext">
              <span
                className="h-3 w-3 rounded-full"
                style={{ background: COLORS[entry.name] || unknownLevelColor }}
              />
              {entry.name}
            </span>
            <span className="font-semibold text-itaca-text">
              {entry.value}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default DoughnutChart;
