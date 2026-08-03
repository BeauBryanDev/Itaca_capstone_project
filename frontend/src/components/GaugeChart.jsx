import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import { maturityColors, unknownLevelColor } from "../data/maturityColors.js";

const MIN = 0;
const MAX = 100;

// Semicircular gauge for the overall score (0-100). Built on Recharts'
// RadialBarChart: a half turn (180 to 0 degrees) with a fixed numeric axis so
// the filled arc is proportional to the value rather than to the data set.
function GaugeChart({ value = 0, level = "" }) {
  const clamped = Math.min(MAX, Math.max(MIN, Number(value) || 0));
  const color = maturityColors[level] || unknownLevelColor;
  const data = [{ name: "score", value: clamped }];

  return (
    <div className="relative">
      <div className="h-44 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            data={data}
            startAngle={180}
            endAngle={0}
            cx="50%"
            cy="92%"
            innerRadius="128%"
            outerRadius="175%"
            barSize={22}
          >
            <PolarAngleAxis
              type="number"
              domain={[MIN, MAX]}
              angleAxisId={0}
              tick={false}
            />
            <RadialBar
              dataKey="value"
              angleAxisId={0}
              fill={color}
              background={{ fill: "#1f2325" }}
              cornerRadius={11}
              isAnimationActive={false}
            />
          </RadialBarChart>
        </ResponsiveContainer>
      </div>

      {/* Value sits over the arc; Recharts has no built-in centered label. */}
      <div className="pointer-events-none absolute inset-x-0 bottom-1 flex flex-col items-center">
        <span className="text-[38px] font-bold leading-none" style={{ color }}>
          {clamped}
        </span>
        <span className="mt-1 text-[13px] text-itaca-subtext">de 100</span>
      </div>

      <div className="mt-1 flex justify-between text-[12px] text-itaca-subtext">
        <span>{MIN}%</span>
        <span>{MAX}%</span>
      </div>
    </div>
  );
}

export default GaugeChart;
