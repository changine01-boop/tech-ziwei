"use client";

import type { ChartResponse } from "@/lib/types";
import {
  BRANCHES, STEMS, PALACE_NAMES, BRANCH_GRID, WU_XING_JU_LABELS,
  ZIWEI_GROUP, TIANFU_GROUP,
} from "@/lib/constants";

interface Props {
  chart: ChartResponse;
}

function palaceName(mingBranch: number, branch: number): string {
  const offset = (mingBranch - branch + 12) % 12;
  return PALACE_NAMES[offset];
}

function starsForBranch(chart: ChartResponse, branch: number): string[] {
  return Object.entries(chart.star_placements)
    .filter(([, b]) => b === branch)
    .map(([s]) => s);
}

function PalaceCell({
  chart,
  branch,
}: {
  chart: ChartResponse;
  branch: number;
}) {
  const isMing = branch === chart.ming_branch;
  const name = palaceName(chart.ming_branch, branch);
  const stars = starsForBranch(chart, branch);
  const branchChar = BRANCHES[branch];
  const stemChar = STEMS[
    (STEMS.length + ((chart.year_stem + ((branch - 2 + 12) % 12)) % 10)) % 10
  ];

  return (
    <div
      className={[
        "palace-cell",
        isMing ? "palace-cell--ming" : "",
      ].join(" ")}
    >
      {/* Header: palace name + ganzhi */}
      <div className="flex items-start justify-between gap-1">
        <span className={`text-xs font-semibold leading-tight ${isMing ? "text-violet-700" : "text-slate-600"}`}>
          {name}
        </span>
        <span className="text-[10px] text-slate-400 shrink-0">
          {stemChar}{branchChar}
        </span>
      </div>

      {/* Stars */}
      <div className="flex flex-wrap gap-0.5 mt-auto">
        {stars.map(star => (
          <span
            key={star}
            className={`text-[9px] px-1 py-0.5 rounded font-medium leading-none ${
              ZIWEI_GROUP.has(star)
                ? "bg-violet-100 text-violet-700"
                : TIANFU_GROUP.has(star)
                ? "bg-amber-50 text-amber-700"
                : "bg-slate-100 text-slate-600"
            }`}
          >
            {star}
          </span>
        ))}
      </div>
    </div>
  );
}

export function PalaceGrid({ chart }: Props) {
  const yearGanzhi = `${STEMS[chart.year_stem]}${BRANCHES[chart.year_branch]}`;
  const lunarDateStr = `${chart.lunar_year}/${chart.lunar_month}/${chart.lunar_day}${chart.is_leap_month ? " 閏" : ""}`;
  const juLabel = WU_XING_JU_LABELS[chart.wu_xing_ju] ?? `${chart.wu_xing_ju}局`;

  return (
    <div className="overflow-x-auto">
      {/*
        CSS Grid 4×4:
          Row 1: 巳 午 未 申  (branches 5 6 7 8)
          Row 2: 辰  [center] 酉  (4, 9)
          Row 3: 卯  [center] 戌  (3, 10)
          Row 4: 寅 丑 子 亥  (2 1 0 11)
      */}
      <div
        className="grid gap-px bg-slate-200 border border-slate-200 rounded-xl overflow-hidden w-full"
        style={{ gridTemplateColumns: "repeat(4, 1fr)", gridTemplateRows: "repeat(4, 1fr)" }}
      >
        {/* 12 palace cells */}
        {(Object.entries(BRANCH_GRID) as [string, [number, number]][]).map(
          ([branchStr, [row, col]]) => {
            const branch = Number(branchStr);
            return (
              <div
                key={branch}
                style={{ gridRow: row, gridColumn: col }}
              >
                <PalaceCell chart={chart} branch={branch} />
              </div>
            );
          }
        )}

        {/* Center cell (rows 2–3, cols 2–3) */}
        <div
          style={{ gridRow: "2 / 4", gridColumn: "2 / 4" }}
          className="bg-slate-50 flex flex-col items-center justify-center gap-2 p-3 text-center"
        >
          <div className="text-violet-600 font-bold text-lg leading-none">✦</div>
          <div className="text-sm font-semibold text-slate-700">{yearGanzhi} 年</div>
          <div className="text-xs text-slate-500">農曆 {lunarDateStr}</div>
          <div className="text-xs text-slate-500">{chart.is_male ? "男命" : "女命"}</div>
          <div className="text-xs font-medium text-violet-600 mt-1">{juLabel}</div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-3 text-xs text-slate-500 justify-center">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-violet-200 inline-block" /> 紫微星系
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-amber-100 inline-block" /> 天府星系
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded border-2 border-violet-500 inline-block" /> 命宮
        </span>
      </div>
    </div>
  );
}
