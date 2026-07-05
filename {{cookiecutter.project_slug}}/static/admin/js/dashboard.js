(function () {
  "use strict";

  function renderDashboard() {
    var source = document.getElementById("admin-dashboard-data");
    if (!source || typeof window.echarts === "undefined") return;
    var data = JSON.parse(source.textContent);
    var axisColor = "#8b95a7";
    var gridColor = "#edf0f5";

    var growthNode = document.getElementById("user-growth-chart");
    var statusNode = document.getElementById("user-status-chart");
    var growth = window.echarts.init(growthNode);
    var status = window.echarts.init(statusNode);
    growth.setOption({
      tooltip: { trigger: "axis" },
      grid: { top: 26, right: 18, bottom: 28, left: 42 },
      xAxis: { type: "category", boundaryGap: false, data: data.monthly.labels, axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: axisColor } },
      yAxis: { type: "value", minInterval: 1, splitLine: { lineStyle: { color: gridColor } }, axisLabel: { color: axisColor } },
      series: [{
        name: "新增用户", type: "line", smooth: true, symbolSize: 8,
        data: data.monthly.values, lineStyle: { width: 3, color: "#3559e0" }, itemStyle: { color: "#3559e0" },
        areaStyle: { color: new window.echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(53,89,224,.26)" }, { offset: 1, color: "rgba(53,89,224,.02)" }]) }
      }]
    });
    status.setOption({
      tooltip: { trigger: "item" }, legend: { bottom: 0, icon: "circle" },
      series: [{ type: "pie", radius: ["58%", "78%"], center: ["50%", "44%"], label: { show: false },
        data: [{ value: data.status.active, name: "正常", itemStyle: { color: "#19a974" } }, { value: data.status.inactive, name: "停用", itemStyle: { color: "#d9dee8" } }]
      }]
    });
    window.addEventListener("resize", function () { growth.resize(); status.resize(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", renderDashboard);
  else renderDashboard();
})();
