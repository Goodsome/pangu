# 榜单词缀分布查询接口

## 需求

新增查询接口：统计上榜玩家装备词缀的选择分布。

- 过滤条件：职业 `player_class`、装备部位 `slot`、最低层数 `min_tier`
- 词缀分类（互斥）：
  - `temper` 回火词缀（每件装备 1 条）
  - `transfigured` 嬗变词缀（0-n 条，与自带词缀分开统计）
  - `innate` 装备自带词缀（非回火、非嬗变，一般 4 条）
- `masterwork_crit` 精炼单独出一个分布：精炼可以点在任意一条词缀上（含回火），所以不并入上述三类，而是统计所有 `is_masterwork_crit=True` 的词缀。
- 太古 (`is_greater`)、重洗 (`is_rerolled`) 不单独分类（按所属词缀自然计入 innate/temper 等）。

数据基础：`entry_equipments.statlines` JSONB 已存有 `Affix` 的全部布尔标记（`is_temper` / `is_transfigured` / `is_masterwork_crit` 等），无需 schema 变更、无需迁移。

## 变更清单

### 1. `application/dtos/affix_distribution_filter.py`（新建）

```python
class AffixDistributionFilter(BaseModel):
    player_class: PlayerClass | None = None
    slot: EquipmentSlot | None = None      # None = 所有部位合并统计
    min_tier: int = Field(default=1, ge=1, le=150)
```

### 2. `application/dtos/affix_distribution_dto.py`（新建）

```python
class AffixDistributionItem(BaseModel):
    codename: str
    stat_type: str
    count: int
    percentage: float          # 0-100，保留两位

class AffixDistributionDto(BaseModel):
    player_class / slot / min_tier   # 回显过滤条件
    entry_count: int                 # 命中的榜单条目数
    item_count: int                  # 命中的装备件数（分母）
    masterwork_item_count: int       # 带精炼标记的装备件数（精炼分布分母）
    innate: list[AffixDistributionItem]
    temper: list[AffixDistributionItem]
    transfigured: list[AffixDistributionItem]
    masterwork_crit: list[AffixDistributionItem]
```

各列表按 `count` 降序。百分比语义：
- `innate` / `temper` / `transfigured`：`count / item_count`（innate 因每件 4 条，总和可趋近 400%，属正常）
- `masterwork_crit`：`count / masterwork_item_count`

### 3. Port：扩展 `application/ports/entry_query_service.py`

```python
@abstractmethod
async def get_affix_distribution(self, filter: AffixDistributionFilter) -> AffixDistributionDto: ...
```

沿用现有"每个聚合一个查询服务"的模式，不新建端口。

### 4. 实现：`infrastructure/persistence/repositories/sql_alchemy_entry_query_service.py`

PostgreSQL 侧聚合（一条 SQL 展开 JSONB 并分组，避免把全部词缀行拉回 Python）：

```sql
SELECT
  CASE
    WHEN (s.value->'is_temper')::boolean THEN 'temper'
    WHEN (s.value->'is_transfigured')::boolean THEN 'transfigured'
    ELSE 'innate'
  END AS category,
  s.value->>'codename'  AS codename,
  s.value->>'stat_type' AS stat_type,
  count(*)                                        AS count,
  count(*) FILTER (WHERE (s.value->>'is_masterwork_crit')::boolean) AS masterwork_count
FROM entries e
JOIN entry_equipments eq ON eq.entry_id = e.id
CROSS JOIN LATERAL jsonb_array_elements(eq.statlines) AS s(value)
WHERE e.player_class = :class AND e.tier >= :min_tier AND eq.slot = :slot
GROUP BY 1, 2, 3
```

SQLAlchemy 2.0 写法要点：
- `func.jsonb_array_elements(EntryEquipmentModel.statlines).table_valued("value").render_derived()` 生成 LATERAL
- JSONB 取布尔：`stat.c.value["is_temper"].as_boolean()`；取文本：`stat.c.value["codename"].astext`
- 分类用 `sqlalchemy.case(...)`

配套两条 count 查询做分母：
- `entry_count`：符合条件的 `entries` 行数
- `item_count` / `masterwork_item_count`：符合条件的 `entry_equipments` 行数、其中 `statlines` 含 `is_masterwork_crit` 的行数（同样用 `EXISTS (SELECT 1 FROM jsonb_array_elements(...))` 或取回后在 Python 内判断；实现时取简单可靠的写法）

Python 侧组装 DTO：按 category 分桶；`masterwork_crit` 分布直接用聚合结果里 `masterwork_count > 0` 的行（跨类别求和）。

### 5. 路由：`interfaces/http.py`

`GET /entries/affix-distribution?player_class=&slot=&min_tier=`

- Query 参数：`player_class: PlayerClass | None`、`slot: EquipmentSlot | None`、`min_tier: int = 1`
- **必须注册在 `GET /entries/{entry_id}` 之前**：FastAPI 按注册顺序匹配，`/{entry_id}` 声明在前会把非 UUID 路径按 422 拒绝，不会落到后面的静态路由。

### 6. 测试（沿用现有 mock-session 风格）

- `tests/test_sql_alchemy_entry_query_service.py` 增加：`get_affix_distribution` 的 SQL 断言（WHERE 含 class/tier/slot、含 `jsonb_array_elements`、含 `GROUP BY`）；结果分桶/排序/百分比的纯组装断言
- `tests/test_http.py` 增加新路由的参数与响应测试

### 7. 收尾

按项目规范，改动完成后运行 `uv run pytest`，并对改动文件触发 `lint-fix` 技能。

## 不做的事

- 不改 DB schema、不加 alembic 迁移（纯查询接口）
- 不做太古/重洗的独立分布（用户明确不需要）
- 不在 `interfaces/api.py`（D4LeaderboardApi）加方法 —— 该 API 类只包写命令，读路径全部走 query service + HTTP
