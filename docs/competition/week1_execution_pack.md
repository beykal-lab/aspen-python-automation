# 第1周执行包说明

本文档说明第一周需要维护的配置和模板文件。它服务于总实施方案中的P0阶段：项目启动与赛题结构化。

## 1. 本周产物

| 文件 | 用途 | 维护人 |
|---|---|---|
| `config/project.yml` | 项目总配置、推荐路线、规模场景、自动化导出要求 | 项目总控 |
| `config/routes.yml` | 候选工艺路线库和评分权重 | 工艺负责人 |
| `config/economics.yml` | 任务书经济参数和经济评价输出项 | 经济负责人 |
| `config/report_outline.yml` | 可研、初设、设备计算书、HAZOP目录结构 | 文档负责人 |
| `data/task/task_requirements.yml` | 任务书要求的机器可读矩阵 | 项目总控 |
| `data/literature/literature_search_keywords.yml` | 文献检索关键词库 | 文献负责人 |
| `data/literature/evidence_table_template.csv` | 文献证据表模板 | 文献负责人 |
| `data/route_selection/route_score_matrix_template.csv` | 路线评分表模板 | 工艺负责人 |
| `data/market/market_research_template.csv` | 市场、价格、政策调研表模板 | 经济负责人 |
| `docs/weekly_reviews/week_01_review_template.md` | 第一周周报模板 | 项目总控 |
| `scripts/validate_week1_pack.py` | 第一周执行包结构化校验脚本 | 自动化负责人 |

## 2. 本周验收步骤

1. 打开总实施方案，确认P0阶段目标。
2. 检查 `data/task/task_requirements.yml` 是否覆盖任务书必交材料。
3. 检查 `config/routes.yml` 是否至少包含R1、R2、R3三条核心路线。
4. 检查 `config/economics.yml` 是否包含任务书给定价格。
5. 检查文献证据表是否能支撑后续路线冻结。
6. 用周报模板填写本周状态。
7. 运行 `python scripts/validate_week1_pack.py`，确认配置和模板仍可解析。

## 3. 第2周入口条件

满足以下条件即可进入第2周文献和路线论证：

1. 任务书要求矩阵已建立。
2. 路线库和评分权重已建立。
3. 文献关键词库已建立。
4. 市场调研表已建立。
5. 至少明确R1保底路线和R2推荐主路线。
6. `python scripts/validate_week1_pack.py` 输出校验通过。
