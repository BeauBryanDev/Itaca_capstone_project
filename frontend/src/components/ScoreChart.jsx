import {
  LineChart as ReLineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// Trend line for the overall score. Compact by default (used as a sparkline
// inside the score StatCard); pass showAxes to render labelled axes.
function ScoreChart({ data = [], showAxes = false, height = 60 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ReLineChart data={data} margin={{ top: 6, right: 6, bottom: 0, left: 0 }}>
        {showAxes && (
          <XAxis
            dataKey="period"
            stroke="#7a7f81"
            tick={{ fontSize: 12, fill: "#E8E8E8" }}
            axisLine={false}
            tickLine={false}
          />
        )}
        {showAxes && (
          <YAxis
            stroke="#7a7f81"
            tick={{ fontSize: 12, fill: "#E8E8E8" }}
            axisLine={false}
            tickLine={false}
            width={28}
          />
        )}
        <Tooltip
          contentStyle={{
            background: "#25282A",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 10,
            color: "#F5F5F5",
            fontSize: 13,
          }}
          labelStyle={{ color: "#E8E8E8" }}
          cursor={{ stroke: "#1393B2", strokeWidth: 1 }}
        />
        <Line
          type="monotone"
          dataKey="score"
          stroke="#998000"
          strokeWidth={3}
          dot={false}
          activeDot={{ r: 4, fill: "#998000" }}
        />
      </ReLineChart>
    </ResponsiveContainer>
  );
}

export default ScoreChart;
