"use client";

import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface EChartRendererProps {
  chartType: string;
  data: any;
  title?: string;
  className?: string;
}

export default function EChartRenderer({
  chartType,
  data,
  title,
  className = "w-full h-80"
}: EChartRendererProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, "dark", {
        renderer: "canvas",
      });
    }

    const chart = chartInstance.current;
    const typeUpper = (chartType || "BAR").toUpperCase();

    let option: echarts.EChartsOption = {
      backgroundColor: "transparent",
      title: title
        ? {
            text: title,
            textStyle: { color: "#e2e8f0", fontSize: 14, fontWeight: "normal" },
            left: "center",
            top: 10,
          }
        : undefined,
      tooltip: {
        trigger: typeUpper === "PIE" || typeUpper === "DONUT" ? "item" : "axis",
        backgroundColor: "#1e293b",
        borderColor: "#334155",
        textStyle: { color: "#f8fafc" },
      },
      grid: {
        top: title ? 50 : 25,
        left: "3%",
        right: "4%",
        bottom: "3%",
        containLabel: true,
      },
    };

    if (typeUpper === "BAR" || typeUpper === "LINE" || typeUpper === "AREA") {
      const records = Array.isArray(data) ? data : [];
      const xVals = records.map((r: any) => r.x || r.category || "Item");
      const yVals = records.map((r: any) => r.val || r.value || 0);

      option = {
        ...option,
        xAxis: {
          type: "category",
          data: xVals,
          axisLine: { lineStyle: { color: "#334155" } },
          axisLabel: { color: "#94a3b8", interval: 0, rotate: xVals.length > 6 ? 25 : 0 },
        },
        yAxis: {
          type: "value",
          splitLine: { lineStyle: { color: "#1e293b" } },
          axisLabel: { color: "#94a3b8" },
        },
        series: [
          {
            data: yVals,
            type: typeUpper === "BAR" ? "bar" : "line",
            areaStyle: typeUpper === "AREA" ? { opacity: 0.3 } : undefined,
            smooth: typeUpper !== "BAR",
            itemStyle: {
              color: typeUpper === "BAR" ? "#3b82f6" : "#06b6d4",
              borderRadius: typeUpper === "BAR" ? [4, 4, 0, 0] : 0,
            },
          },
        ],
      };
    } else if (typeUpper === "PIE" || typeUpper === "DONUT") {
      const records = Array.isArray(data) ? data : [];
      const pieData = records.map((r: any) => ({
        name: r.x || r.name || "Item",
        value: r.val || r.value || 0,
      }));

      option = {
        ...option,
        series: [
          {
            type: "pie",
            radius: typeUpper === "DONUT" ? ["45%", "70%"] : "65%",
            center: ["50%", "55%"],
            data: pieData,
            label: { color: "#94a3b8" },
            itemStyle: {
              borderRadius: 4,
              borderColor: "#101623",
              borderWidth: 2,
            },
          },
        ],
      };
    } else if (typeUpper === "SCATTER") {
      const records = Array.isArray(data) ? data : [];
      const scatterPoints = records.map((r: any) => [r.x, r.y]);

      option = {
        ...option,
        xAxis: {
          type: "value",
          splitLine: { lineStyle: { color: "#1e293b" } },
          axisLabel: { color: "#94a3b8" },
        },
        yAxis: {
          type: "value",
          splitLine: { lineStyle: { color: "#1e293b" } },
          axisLabel: { color: "#94a3b8" },
        },
        series: [
          {
            type: "scatter",
            symbolSize: 8,
            data: scatterPoints,
            itemStyle: { color: "#38bdf8", opacity: 0.8 },
          },
        ],
      };
    } else if (typeUpper === "HISTOGRAM") {
      const bins = data?.bins || [];
      const counts = data?.counts || [];
      const categories = bins.map((b: any) => `${b.x0} - ${b.x1}`);

      option = {
        ...option,
        xAxis: {
          type: "category",
          data: categories,
          axisLine: { lineStyle: { color: "#334155" } },
          axisLabel: { color: "#94a3b8", rotate: 30 },
        },
        yAxis: {
          type: "value",
          splitLine: { lineStyle: { color: "#1e293b" } },
          axisLabel: { color: "#94a3b8" },
        },
        series: [
          {
            type: "bar",
            data: counts,
            itemStyle: { color: "#8b5cf6", borderRadius: [4, 4, 0, 0] },
          },
        ],
      };
    } else if (typeUpper === "BOX_PLOT") {
      const records = Array.isArray(data) ? data : [];
      const groups = records.map((r: any) => r.group_name || "All");
      const boxValues = records.map((r: any) => [r.min_val, r.q1, r.median, r.q3, r.max_val]);

      option = {
        ...option,
        xAxis: {
          type: "category",
          data: groups,
          axisLine: { lineStyle: { color: "#334155" } },
          axisLabel: { color: "#94a3b8" },
        },
        yAxis: {
          type: "value",
          splitLine: { lineStyle: { color: "#1e293b" } },
          axisLabel: { color: "#94a3b8" },
        },
        series: [
          {
            type: "boxplot",
            data: boxValues,
            itemStyle: { color: "#10b981", borderColor: "#34d399" },
          },
        ],
      };
    }

    chart.setOption(option, true);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [chartType, data, title]);

  return <div ref={chartRef} className={className} />;
}
