---
name: unity-interview-drill
description: Unity 面试每日刷题。当用户说"Unity刷题""Unity每日一题""出N道Unity[类型]题""今天来2道数学、2道计算机基础、1道算法""出一道渲染题""出一道插件题""出一道数据结构题""出一道场景题""出一道决策题""只出错题""查看错题本""清空错题""重置历史""同步""统计"时使用。支持算法、八股、设计、数学考察、计算机基础（含数据结构）、渲染/TA、第三方插件（HybridCLR/xLua/YooAsset/UniTask）七类题目，含故障场景题与决策场景题、间隔重复、错题本、难度筛选、自动验证与多设备同步。
---

# Unity Interview Daily Drill

Unity 面试每日刷题。七类题目：算法、八股、设计、数学、计算机基础、渲染/TA、第三方插件。
按用户指定类型和题数随机出题，不出已出过的题，优先企业真题。

## 数据文件

均位于项目根目录 `E:\Unity就业面试`：

- `config/config.json` — 配置（默认题数、类型、难度、联网开关）
- `bank/{algorithm,bagu,design,math,cs_basics,rendering,plugins}.json` — 题库
- `history/history.json` — 出题与答题状态（**个人数据，不入库**，仓库只有 `history.template.json`）
- `knowledge/knowledge.json` — 概念知识库（同上，仓库只有 `knowledge.template.json`）
- `answers/` — 答题区；`tools/make_answers.py` — 答题区生成/解析脚本

**首次使用**（运行时文件不存在时）：先从 `*.template.*` 复制出运行时文件，`history` 的 `start_date` 设为今天。涉及三类：`history/history.json`、`knowledge/knowledge.json`、以及答题区三件套（`answers/Algorithm.cs`、`answers/AlgorithmTests.cs`、`answers/答题区.docx` 从同名 `.template` 文件复制）。用户说过「清空重来」时也走这条路，但**先确认**，别擅自重置已积累的进度。

**答题区是个人数据，不入库**（`.gitignore` 已忽略），仓库只留 `*.template.*` 空模板。工程文件 `AlgorithmDrill.csproj`/`.sln` 仍跟踪。⚠️ csproj 里有 `<Compile Remove="*.template.cs" />` —— 否则模板会被 SDK 默认 glob 编译，与运行时文件重复定义 `Program` 类。

## 类型与 id

| type | 中文 | id 前缀 | 子类（subtype） |
|---|---|---|---|
| `algorithm` | 算法题 | `algo_` | 数组/链表/树/图/DP 等 |
| `bagu` | Unity/C# 八股 | `bagu_` | `ugui`（Unity UI）及 Unity/C# 基础子类 |
| `design` | 设计题 | `design_` | `design_pattern`（设计模式）、系统设计子类 |
| `math` | 数学考察 | `math_` | — |
| `cs_basics` | 计算机基础 | `cs_basics_` | `data_structure`（数据结构）、`operating_system`、`memory`、`network`、`network_sync`、`database`、`cpp`、`algorithms`、`math_foundation` |
| `rendering` | 渲染/TA | `rendering_` | — |
| `plugins` | 第三方插件 | `plugins_` | `hybridclr` / `xlua` / `yooasset` / `unitask` / `scenario_design` / `scenario_decision` |

id 格式 `<type>_<三位序号>`。难度：`easy` / `medium` / `hard` / `all`。

## Workflow

1. 读 `config/config.json` 与 `history/history.json`。
2. **检查 `start_date`**：若今天早于该日期，**不出题**，只回复"距离开始刷题还有 N 天"。
3. 解析指令得到 `{type: count}` 与 difficulty，未指定时用 config 默认值。算法题形式默认 `leetcode`。
4. 构建候选池（同一 id 只出现一次），按「出题优先级」合并：**间隔重复到期题** > **错题重练** > **新题**（不在 `asked_ids` 且匹配难度）。到期题和错题**不受 `asked_ids` 排除限制** —— 这是复习能出回来的原因。
5. 候选不足时联网补题（见「真题来源」），或退化为本地题并如实标 `source_tier`。
6. 组内排序后 Fisher-Yates 随机抽取，按「记录规则」写回 `history.json`。
7. **把题目写入答题区**（见下节）。
8. 对话里输出题目概览 + 答题区路径，提示用户去文件作答；答案用 `<details>` 折叠备用。

## 答题区

出题时必须把题目写进答题区文件，用户在那里作答，读回后验证。

| 题型 | 文件 |
|---|---|
| `algorithm` | `answers/Algorithm.cs`（用户实现）+ `answers/AlgorithmTests.cs`（测试与入口，自动生成，用户不改） |
| 其他六类 | `answers/答题区.docx`（题目 + 「作答：」空白） |

**算法题两种形式**：`leetcode`（默认，给方法签名 + 测试用例）或 `acm`（给 `Solve()`，用户自己处理输入输出）。题库的 `ret`/`method`/`params`/`testcases` 字段供生成用；`testcases` 可引用 `ListNode`/`TreeNode`，脚本会按签名自动注入节点类。

**脚本接口**（`tools/make_answers.py`）：

```python
import sys; sys.path.insert(0, "tools")
from make_answers import write_cs, write_docx, parse_answers, read_cs
write_cs(algo_problems, mode="leetcode", date="YYYY-MM-DD")  # 每题可用 form 字段覆盖形式
write_docx(other_problems, date="YYYY-MM-DD")
parse_answers()   # → {qid: 作答文本}，读 docx
read_cs()         # → {qid: {'code','solved'}}，读 Algorithm.cs
```

**用户怎么跑**：VS 2022 双击 `answers/AlgorithmDrill.sln` 按 F5；VS Code 打开 `answers/` 按 F5；命令行 `cd answers && dotnet run`。

**验证方式**：算法题看 `read_cs()` 的 `solved`（方法体仍是 `throw new NotImplementedException()` 则未作答），否则提取代码真编译跑测试；非算法题用 `parse_answers()` 拿文本对照答案判对错。本机有 VS 2022 + VS Code + .NET 9/10 SDK，可真正 `dotnet build` + `dotnet run`。
⚠️ 编译验证时把 `answers/` 的三个文件复制到临时目录跑，不要在项目目录生成 bin/obj。
⚠️ **`.csproj` 的 `TargetFramework` 必须是 `net9.0`** —— VS 2022 17.14 只认到 .NET 9，用 `net10.0` 会报 `NETSDK1045` 让 VS 无法加载项目。改框架要同步改 `tools/make_answers.py` 的 `TARGET_FRAMEWORK` 常量。
⚠️ docx 读回只能拿段落文本（批注/修订/图片读不到）。用户改了文件结构导致读不到时，**如实说"无法验证，因为 X"**，不要猜。

## 记录规则

**出题时**：`asked_ids[id] = "YYYY-MM-DD"`（**仅首次**，已存在则保留原日期）；`daily_count["YYYY-MM-DD"][type] += 1`；题目正文写入 `bank/<type>.json`。

**答题后**追加一条到 `answered_log`（**唯一的答题事实来源**）：`{date, id, type, difficulty, result: correct|wrong|skipped, note}`，再派生更新：

- **答对**：SM-2 更新 `spaced_repetition[id]`。`repetitions += 1`；interval 依次为 1、6、`round(interval * ease)`；`next_review = 今天 + interval`。自评 `again/hard/good/easy` 时 `ease` 分别 `-0.2/-0.15/0/+0.15`，下限 1.3。
- **答错**：`wrong_book[id].wrong_count += 1`、`last_wrong_at = 今天`、`note` 记错因；`spaced_repetition[id]` 重置为 `interval=1`、`repetitions=0`、`next_review=明天`；并更新知识库。
- **`stats` 不落盘**：从 `answered_log` 实时聚合。`correct_rate` = correct / (correct + wrong)，`skipped` 不计入分母。

**State Schema（v2）**：`start_date`（早于该日期不出题）/ `asked_ids`（`{id: 首次出题日期}`）/ `daily_count`（`{日期: {类型: 出题数}}`）/ `spaced_repetition`（SM-2 状态）/ `wrong_book`（错题及次数）/ `answered_log`（答题流水，stats 唯一来源）/ `legacy_stats`（v1 手填汇总，只读冻结）。

**`asked_ids` 只管「首次出题」，不阻止复习** —— 判断出新题用 `asked_ids`，判断该复习用 `next_review`。

## 知识库

`knowledge/knowledge.json` 按**概念**组织（不是按题），随错题生长。目的是把反复考、反复错的概念串起来 —— 单题答案里没有这层聚合。

答错时：判断属于哪个**跨题概念组**（如"GC"涵盖 bagu 与 cs_basics 的多道题）→ 不存在则新建（含 `summary`/`key_points`/`pitfalls`）→ 追加错误记录 `{date, question_id, category, detail}`。`category` 六选一：`boundary`（边界/退化）/ `concept`（理解偏差）/ `derivation`（推不出）/ `application`（不知用在哪）/ `detail`（细节遗漏）/ `unfamiliar`（没接触过）。同一概念再错时**追加并把反复出现的错因合并进 `pitfalls`**。插件题按**插件 + 机制**命名概念组（如"HybridCLR 的 AOT 泛型"），不要把四类插件混成一个。

**不要做**：❌ 抄单题答案原文 ❌ 为每道题都建概念组（要能多题共用才有意义）。✅ 只写答案里没有的：跨题聚合、错因归类、前驱后继关系。

## Commands

- `只出错题` / `查看错题本` — 从 `wrong_book` 出题 / 列出错题
- `查看知识库` / `查 <概念名>` — 概念组统计 / 该概念下全部题目与错因
- `出一道插件题` / `只出 yooasset 的题` — 插件题，按 `subtype` 筛
- `出一道数据结构题` / `只出数据结构` — 走 `cs_basics` 的 `data_structure` 子类（可说 `只出树和图的` 再筛）
- `出一道场景题` / `出一道故障场景题` / `出一道决策题` — 场景类题（故障根因用 `scenario_design`；约束下做选择用 `scenario_decision`）
- `算法题用 acm 形式` — 指定算法题形式（默认 leetcode）
- `算法题做完了` / `已作答` — 读回答题区，验证并记录结果
- `清空错题` — 清空 `wrong_book`（`answered_log` 与知识库保留）
- `重置历史` — 清空 `asked_ids` 与 `daily_count`（二次确认；**不动 `answered_log`**）
- `同步` — 手动 pull + push。当前 `sync.enabled = false`，先提示填 `gist_id`
- `统计` — 从 `answered_log` 聚合，输出各类型正确率、错题数、待复习数

## 出题侧重

**`math` / `cs_basics`** —— 标准只有一条：**出游戏开发面试会问的题**。想象一个 Unity 客户端岗位的面试官会不会问这道题：不会让人手算投影向量、不会考跟引擎无关的纯数学、不会要求现场证明公式。答案要写出**方法或原理**并说清怎么用。`cs_basics` 子类以 `data_structure` 为主（19 题，覆盖数组/链表、栈队列、哈希、树、图），还有 `operating_system` / `memory` / `network` / `network_sync` / `database` / `cpp`。

数据结构子类要和 `algorithm` 分开：**`algorithm` 考「手写实现 + 复杂度」，`cs_basics.data_structure` 考「为什么这样设计、工程上怎么选、游戏里用在哪」**。「反转链表」属 `algorithm`，「栈和队列的区别与游戏应用」属 `cs_basics`。

**`rendering`（渲染/TA）** —— 与 `math` 的区别：`math` 考数学方法本身，`rendering` 考渲染管线的实现与原理。范围：管线各阶段、坐标空间、混合与透明、贴图、光照模型、阴影、抗锯齿、后处理、剔除与性能、管线选型、Shader 编程。**只收有标准答案的技术题** —— "你对 TA 的理解""职业规划"这类开放题不收。

**`bagu.ugui`（uGUI）** —— 纳入 Unity 客户端岗位的固定考察范围。覆盖 Canvas 渲染模式与 CanvasScaler、RectTransform 和屏幕/世界坐标转换、EventSystem/Raycaster/事件冒泡、Graphic 与 Canvas rebuild、合批与 Overdraw、LayoutGroup/ContentSizeFitter、ScrollRect 虚拟化、Mask/RectMask2D、TextMeshPro 图集与字体回退。重点考机制、性能定位和取舍：回答应说明“为什么会重建/为什么点不到/为什么不同分辨率错位”，而不是只背组件属性；涉及版本差异时按目标 Unity 版本核对。

**`plugins`（第三方插件）** —— 四个插件的考察范围：`hybridclr`（热更路线、AOT 泛型与补充元数据、程序集划分与裁剪、官方不支持的特性）、`xlua`（C#⇄C⇄Lua 交互与虚拟栈、元表/闭包/require、跨语言 GC 与性能）、`yooasset`（运行模式、句柄与引用计数、分包与零冗余、版本与差量下载）、`unitask`（为什么不用协程/Task、状态机与零 GC、CancellationToken 与生命周期、与 Unity 6 `Awaitable` 的选型）。

两档场景题型（`source_tier: generated` 且 `verified: false`，答案不是唯一解）：
- `scenario_design` **故障场景题**：给线上故障现象，要根因 + 方案。答对标准是根因定位链路与方案完整性。
- `scenario_decision` **决策场景题**：给一组约束与多个候选方案，问「你会怎么做」。答对标准是**先结论、再理由、再说代价与回退成本**，并说清「什么条件下结论会反过来」。

出题原则：**考机制与取舍，不考 API 背诵**。答案必须区分**官方文档明说的**与**工程经验的**，版本差异（YooAsset 3.0 移除弱引用句柄、HybridCLR v8.0 支持 extern、Unity 6 提供 `Awaitable`）要写清版本号。**决策题判分看「有没有给判断依据」而非结论** —— 用户的结论与参考答案不同，只要约束分析、代价评估、回退成本说得通就算对；只报方案名不说理由的，即使与参考答案一致也判「不完整」。

**与其他题型的分工**：`design` 是从零设计一个系统（给需求，给类结构、数据流）；`scenario_design` 是从故障反推原因（给现象，给根因、方案、验证）；`scenario_decision` 是在约束下做选择（给候选与死线，给结论、代价、回退）。`algorithm` 侧重思路与复杂度；`bagu` 侧重原理与版本差异。三者不要互相重复。

**设计模式纳入考察**：`design_pattern` 不是背 GoF 定义，而是考察候选人能否识别变化点、选择合适的协作方式并说明代价。覆盖策略（Strategy）、观察者（Observer）、状态（State）、命令（Command）、工厂/抽象工厂（Factory）、装饰器（Decorator）、适配器/外观（Adapter/Facade）以及对象池等 Unity 常见变体。题目至少要落到一个真实场景（技能效果、输入回放、UI/事件、对象生成、资源接口等），回答需包含接口或类结构、调用/生命周期、扩展方式、线程/GC/性能或调试方面的取舍；只写“使用某某模式”而没有判断依据，判为不完整。出设计题时优先保证 `design_pattern` 有覆盖，并与系统设计题交叉考察。

## 真题来源

优先企业真题（大厂游戏岗：腾讯、网易、米哈游、字节、莉莉丝、叠纸），其次本地种子题，最后自拟。来源按牛客面经 > GitHub 题库仓库 > 技术社区排序。

**抓取方式（本环境实测）**：`WebSearch` 可用但只返回标题+URL；**`WebFetch` 不可用**（域名校验失败）；**`curl` 可用**。流程是 **WebSearch 找链接 → curl 抓正文**，`-o` 写到项目内 `.fetch/`（不要写 `/tmp`，Git Bash 的 `/tmp` 与 python 看到的不是同一个路径）：

```bash
curl -sL -m 20 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36" "<URL>" -o .fetch/page.html
```

去标签取正文：`re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)` 再 `re.sub(r'(?s)<[^>]+>', '\n', s)`。搜索用带企业名的查询词提高命中率。**搜不到真题时不要编造** —— 退化并如实标注，绝不伪造企业出处。抓取的中间文件放 `.fetch/`，不要提交或留在根目录。

**已知的网络现状**（别重复踩）：
- 牛客讨论页正文已改为客户端渲染 + 登录墙，`curl` 只能拿到 `<meta name="description">` 摘要（`/discuss/<id>` 与 `/feed/main/detail/<id>` 均如此）——**插件题因此拿不到可核实的公司真题**，只标 `community` / `generated`；
- 可访问的核对源：`hybridclr.cn/docs/...`、`yooasset.com/docs/...`、`docs.unity.cn`、`learn.microsoft.com`、`cloud.tencent.cn`、`cnblogs.com`、`gitee.com/<repo>`（只给仓库描述，HybridCLR 有镜像可作备用）；
- 不通的域名：`github.com`、`raw.githubusercontent.com`、`cdn.jsdelivr.net`（301 到 raw）、`gitcode.com`（418）、`blog.csdn.net`（521 时好时坏）。
- 本机直连 `github.com:443` 被重置，需要时挂本地代理 `http://127.0.0.1:7890`；git 操作走 SSH（见项目记忆）。

### source_tier

| tier | 含义 |
|---|---|
| `company_verified` | 明确企业真题，有可访问 URL，且核对通过 —— 最优先出 |
| `company_unverified` | 面经提及企业但无法核实，或答案未核对通过 —— 标注「回忆版，未核实」 |
| `community` | 社区/仓库整理，未指明企业 |
| `seed` | 本地种子题，`source_url: null`，已验证 |
| `seed_unverified` | 本地种子题且 `verified: false` —— 可出但必须显示争议警告 |
| `generated` | Agent 自拟 —— 最后兜底，必须显式标注 |

三条硬约束：① `company_verified` 的前提是**真有可访问 URL**；② **`verified: false` 的题一律不得标 `company_verified`**；③ `source` 与 `source_url` 必须互相印证，不允许编造 URL。

### 答案验证

**入库即验证**。依据顺序：官方文档（Unity Docs / Microsoft Learn）> MDN / 语言规范 > 权威教材 > 高赞社区答案。核对通过 → `verified: true` 并在 `verify_note` 写明依据；不通过或有版本差异/工程争议 → `verified: false` 并写明**争议点是什么、两种立场分别是什么**。**面经答案本身可能是错的**，不能因为"这是大厂真题"跳过核对。

## 出题优先级

同类型内按此顺序抽取：① 间隔重复到期题（最高）② 错题重练 ③ 企业真题（`company_verified` > `company_unverified`）④ 本地种子题 / 社区题 ⑤ Agent 自拟题（仅以上都不足时）。

`config.prefer_real_questions` 为 `false` 时只用本地题库，不出网。

## Output Format

按类型分组，每组标注：类型 / 子类型 / 难度；来源（企业名 + URL + `source_tier`，`seed`/`generated` 要显式说明）；是否错题重练 / 间隔重复；题目（答案用 `<details>` 折叠）；验证状态（`verified: false` 必须写出争议点）。
