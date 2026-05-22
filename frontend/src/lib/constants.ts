export const BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"] as const;
export const STEMS   = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"] as const;

export const PALACE_NAMES = [
  "命宮","兄弟宮","夫妻宮","子女宮","財帛宮","疾厄宮",
  "遷移宮","交友宮","官祿宮","田宅宮","福德宮","父母宮",
] as const;

export const WU_XING_JU_LABELS: Record<number, string> = {
  2: "水二局",
  3: "木三局",
  4: "金四局",
  5: "土五局",
  6: "火六局",
};

// Branch index → [gridRow, gridCol] (1-indexed, for a 4×4 CSS grid)
export const BRANCH_GRID: Record<number, [number, number]> = {
  5: [1, 1],  // 巳
  6: [1, 2],  // 午
  7: [1, 3],  // 未
  8: [1, 4],  // 申
  4: [2, 1],  // 辰
  9: [2, 4],  // 酉
  3: [3, 1],  // 卯
  10: [3, 4], // 戌
  2: [4, 1],  // 寅
  1: [4, 2],  // 丑
  0: [4, 3],  // 子
  11: [4, 4], // 亥
};

// 紫微 group stars (rendered in violet)
export const ZIWEI_GROUP = new Set(["紫微","天機","太陽","武曲","天同","廉貞"]);
// 天府 group stars (rendered in amber)
export const TIANFU_GROUP = new Set(["天府","太陰","貪狼","巨門","天相","天梁","七殺","破軍"]);

export const READING_TYPE_LABELS: Record<string, string> = {
  core:         "Core Personality",
  relationship: "Relationship Patterns",
  career:       "Career & Purpose",
  annual:       "Current Period",
};
