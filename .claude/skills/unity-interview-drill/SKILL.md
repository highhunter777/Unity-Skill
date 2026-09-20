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
- `history/history.json` — 出题与答题状态
- `knowledge/knowledge.json` — 概念知识库（按概念组织，随错题生长）
- `answers/` — 答题区（见下节）
- `tools/make_answers.py` — 答题区生成/解析脚本

## 类型与 id

| type | 中文 | id 前缀 |
|---|---|---|
| `algorithm` | 算法题 | `algo_` |
| `bagu` | Unity/C# 八股 | `bagu_` |
| `design` | 设计题 | `design_` |
| `math` | 数学考察 | `math_` |
| `cs_basics` | 计算机基础 | `cs_basics_` |
| `rendering` | 渲染/TA | `rendering_` |
| `plugins` | 第三方插件（HybridCLR / xLua / YooAsset / UniTask） | `plugins_` |

id 格式 `<type>_<三位序号>`，前缀与 type 名一致。难度：`easy` / `medium` / `hard` / `all`。

## Workflow

1. 读 `config/config.json` 与 `history/history.json`。
2. **检查 `start_date`**：若今天早于该日期，**不出题**，只回复"距离开始刷题还有 N 天"。
3. 解析指令得到 `{type: count}` 与 difficulty，未指定时用 config 默认值。算法题形式默认 `leetcode`。
4. 构建候选池（同一 id 只出现一次），按优先级合并：
   **间隔重复到期题**（`next_review <= 今天`）> **错题重练** > **新题**（不在 `asked_ids` 且匹配难度）。
   到期题和错题**不受 `asked_ids` 排除限制** —— 这是复习能出回来的原因。
5. 候选不足时联网补题（见「真题来源」），或退化为本地题并如实标 `source_tier`。
6. 组内按「出题优先级」排序后 Fisher-Yates 随机抽取。
7. 按「记录规则」写回 `history.json`。
8. **把题目写入答题区**（见下节）。
9. 对话里输出题目概览 + 答题区路径，提示用户去文件作答；答案用 `<details>` 折叠备用。

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

**验证方式**：算法题看 `read_cs()` 的 `solved`（方法体仍是 `throw new NotImplementedException()` 则未作答），否则提取代码真编译跑测试；非算法题用 `parse_answers()` 拿文本对照答案判对错。本机有 VS 2022 + VS Code + .NET 9/10 SDK，可真正 `dotnet build` + `dotnet run`，不只是静态检查。
⚠️ 编译验证时把 `answers/` 的三个文件复制到临时目录跑，不要在项目目录生成 bin/obj。
⚠️ **`.csproj` 的 `TargetFramework` 必须是 `net9.0`** —— VS 2022 17.14 内置 MSBuild 只认到 .NET 9，用 `net10.0` 会报 `NETSDK1045` 导致 VS 无法加载项目（命令行 `dotnet` 却能过，所以别只用命令行验证）。改框架要同步改 `tools/make_answers.py` 的 `TARGET_FRAMEWORK` 常量。

**限制**：docx 读回只能拿段落文本 —— 批注、修订、图片读不到。用户若改了文件结构导致 `read_cs()` 读不到某题，要**如实说"无法验证，因为 X"**，不要猜。

## 记录规则

**出题时**：`asked_ids[id] = "YYYY-MM-DD"`（**仅首次**，已存在则保留原日期）；`daily_count["YYYY-MM-DD"][type] += 1`；题目正文写入 `bank/<type>.json`。

**答题后**追加一条到 `answered_log`（**唯一的答题事实来源**）：

```json
{ "date": "2026-09-20", "id": "math_001", "type": "math",
  "difficulty": "medium", "result": "correct | wrong | skipped", "note": "" }
```

再派生更新：

- **答对**：SM-2 更新 `spaced_repetition[id]`。`repetitions += 1`；interval 依次为 1、6、`round(interval * ease)`；`next_review = 今天 + interval`。自评 `again/hard/good/easy` 时 `ease` 分别 `-0.2/-0.15/0/+0.15`，下限 1.3。
- **答错**：`wrong_book[id].wrong_count += 1`、`last_wrong_at = 今天`、`note` 记错因；`spaced_repetition[id]` 重置为 `interval=1`、`repetitions=0`、`next_review=明天`；并更新知识库。
- **`stats` 不落盘**：统计时从 `answered_log` 实时聚合。`correct_rate` = correct / (correct + wrong)，`skipped` 不计入分母。

## State Schema（v2）

| 字段 | 用途 |
|---|---|
| `start_date` | 首次开始刷题的日期，早于该日期不出题 |
| `asked_ids` | `{id: 首次出题日期}` |
| `daily_count` | `{日期: {类型: 出题数}}` |
| `spaced_repetition` | SM-2 状态 |
| `wrong_book` | 错题及错误次数 |
| `answered_log` | 答题明细流水，stats 的唯一来源 |
| `legacy_stats` | v1 手填汇总，只读冻结 |

**`asked_ids` 只管「首次出题」，不阻止复习** —— 判断出新题用 `asked_ids`，判断该复习用 `next_review`。

## 知识库

`knowledge/knowledge.json` 按**概念**组织（不是按题），随错题生长。目的是把反复考、反复错的概念串起来 —— 单题答案里没有这层聚合。

答错时：判断属于哪个**跨题概念组**（如"GC"涵盖 bagu 与 cs_basics 的多道题）→ 不存在则新建（含 `summary`/`key_points`/`pitfalls`）→ 追加错误记录 `{date, question_id, category, detail}`。`category` 从六类选一：`boundary`（边界/退化）/ `concept`（理解偏差）/ `derivation`（推不出）/ `application`（不知用在哪）/ `detail`（细节遗漏）/ `unfamiliar`（没接触过）。同一概念再错时**追加并把反复出现的错因合并进 `pitfalls`** —— 这是知识库最有价值的部分。插件题同样入知识库，概念组按**插件 + 机制**命名（如"HybridCLR 的 AOT 泛型"、"YooAsset 的引用计数与句柄"），不要把四类插件混成一个概念。

**不要做**：❌ 抄单题答案原文（重复建设且会不同步）❌ 为每道题都建概念组（要能多题共用才有意义）。✅ 只写答案里没有的：跨题聚合、错因归类、前驱后继关系。

## Commands

- `只出错题` / `查看错题本` — 从 `wrong_book` 出题 / 列出错题
- `查看知识库` / `查 <概念名>` — 概念组统计 / 该概念下全部题目与错因
- `出一道插件题` / `只出 yooasset 的题` — 插件题（`subtype`：`hybridclr` / `xlua` / `yooasset` / `unitask` / `scenario_design` / `scenario_decision`，可按子类筛）
- `出一道数据结构题` / `只出数据结构` — 走 `cs_basics` 的 `data_structure` 子类（还可以说 `只出树和图的` / `跳过哈希表`，都是在该子类内再筛）
- `出一道场景题` / `出一道故障场景题` / `出一道决策题` / `出一道选型题` — 场景类题（故障根因用 `scenario_design`；约束下做选择用 `scenario_decision`）
- `算法题用 acm 形式` — 指定算法题形式（默认 leetcode）
- `算法题做完了` / `已作答` — 读回答题区，验证并记录结果
- `清空错题` — 清空 `wrong_book`（`answered_log` 与知识库保留）
- `重置历史` — 清空 `asked_ids` 与 `daily_count`（二次确认；**不动 `answered_log`**）
- `同步` — 手动 pull + push。当前 `sync.enabled = false`，先提示填 `gist_id`
- `统计` — 从 `answered_log` 聚合，输出各类型正确率、错题数、待复习数

## 出题侧重

**`math` / `cs_basics`** —— 标准只有一条：**出游戏开发面试会问的题**。判断方法：想象一个 Unity 客户端岗位的面试官会不会问这道题。这条界定了边界：不会让人手算投影向量、不会考跟引擎无关的纯数学、不会要求现场证明公式。参考考点：math 是向量/变换/四元数/几何求交/插值/浮点/随机数；cs_basics 是数据结构/操作系统/网络/帧同步确定性/数据库索引。答案要写出**方法或原理**并说清怎么用；"已知 X 求 Y"的计算题面试官不会问。

`cs_basics` 里 `data_structure` 是最大的子类，覆盖：数组/链表/动态数组与扩容、栈与队列（含环形缓冲）、哈希表与 Dictionary 的 key 语义、树（BST/平衡树/堆/Trie/线段树与树状数组）、图（最短路/拓扑排序/并查集）。出这一子类时要和 `algorithm` 分开：**`algorithm` 考「手写实现 + 复杂度」，`cs_basics.data_structure` 考「为什么这样设计、工程上怎么选、游戏里用在哪」**。例如「反转链表」属于 `algorithm`，「栈和队列的区别与游戏应用」属于 `cs_basics`。

**`rendering`（渲染/TA）** —— 与 `math` 的区别：`math` 考数学方法本身，`rendering` 考渲染管线的实现与原理。范围：管线各阶段、坐标空间、混合与透明、贴图（法线/AO/MipMap/光照贴图）、光照模型（BlinnPhong/PBR/BRDF）、阴影、抗锯齿（MSAA/TAA/FXAA）、后处理（Bloom/色调映射/Gamma）、剔除与性能（DrawCall/合批/LOD/Overdraw）、管线选型（URP/HDRP/SRP）、Shader 编程。**只收有标准答案的技术题** —— "你对 TA 的理解""看过哪些博主""职业规划"这类开放题不收。

**`plugins`（第三方插件）** —— 考察简历上写了、面试官就会追问的四个常用插件。`subtype` 六选一，前四个是插件子类，后两个是题型：

插件子类：
- `hybridclr` —— 热更路线选型、il2cpp/IL2CPP 与 AOT 限制、AOT 泛型与补充元数据（含 `full generic sharing` 的版本差异）、程序集划分与代码裁剪、`MissingMethodException` 类报错、不支持的特性。
- `xlua` —— Lua 与 C# 的交互原理（虚拟栈、C#⇄C⇄Lua、wrapper 绑定）、元表/闭包/`require` 加载机制、跨语言 GC 与性能优化、`[Hotfix]` 补丁。
- `yooasset` —— 运行模式与初始化、句柄与引用计数、卸载时机与 `UnloadUnusedAssets`／`ForceUnloadAllAssets` 的取舍、分包与零冗余、版本/差量/断点续传、与 Addressables/原生 AB 的对比。
- `unitask` —— 为什么不用协程/Task、`async`/`await` 编译成状态机、零 GC 的来源与边界、`CancellationToken` 传递与生命周期绑定、常见坑、与 Unity 6 `Awaitable` 的选型。

场景题型（`source_tier: generated` 且 `verified: false`，答案不是唯一解）：
- `scenario_design` —— **故障场景题**：给一个线上故障现象（内存不降、贴图变紫、回调打到已销毁对象），要求分析根因 + 给方案。答对标准是根因定位链路与方案完整性。
- `scenario_decision` —— **决策场景题**：给一组约束（团队技术栈、已上线存量、包体/内存死线、2 周预算、多个候选方案），问「你会怎么做」。答对标准是**先给结论、再给理由、再说代价与回退成本**，并说清「什么条件下我的结论会反过来」。

出题原则：**考机制与取舍，不考 API 背诵**。每道题都要能回答「为什么这么设计、代价是什么、工程上怎么选」。答案必须区分**官方文档明说的**与**工程经验的**，涉及版本差异（YooAsset 3.0 移除弱引用句柄、HybridCLR v8.0 支持 extern、Unity 6 提供 `Awaitable`）要写清版本号。

**决策题的重点不是「选对了」，而是「有没有给判断依据」** —— 判分时允许用户的结论与参考答案不同，只要约束分析、代价评估、回退成本这三段说得通就算对；反过来，只报一个方案名不说理由的，即使和参考答案一致也判「不完整」。

**`design`（设计题）** 与插件场景题的分工：`design` 考**从零设计一个系统**（给需求，给类结构、数据流、取舍）；`plugins` 的 `scenario_design` 考**从故障反推原因**（给现象，给根因、方案、验证手段）；`scenario_decision` 考**在约束下做选择**（给多个候选与死线，给结论、代价、回退成本）。三者不要互相重复。

**其他**：`algorithm` 侧重思路与复杂度；`bagu` 侧重原理与版本差异；`design` 侧重架构取舍。

## 真题来源

优先企业真题（大厂游戏岗：腾讯、网易、米哈游、字节、莉莉丝、叠纸），其次本地种子题，最后自拟。来源按牛客面经 > GitHub 题库仓库 > 技术社区排序。

**抓取方式（本环境实测）**：`WebSearch` 可用但只返回标题+URL；**`WebFetch` 不可用**（域名校验失败，牛客/GitHub/知乎全被拦）；**`curl` 可用**。标准流程是 **WebSearch 找链接 → curl 抓正文**：

```bash
curl -sL -m 20 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36" "<URL>" -o page.html
```

`-o` 要写到 `E:\Unity就业面试\.fetch\`（项目内临时目录）下，不要写 `/tmp`（本环境 Git Bash 的 `/tmp` 与 python 看到的不是同一个路径，会 FileNotFoundError）。抓完用 python 去标签取正文：`re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)` 再 `re.sub(r'(?s)<[^>]+>', '\n', s)`。牛客页为服务端渲染，去掉标签后可见正文含题目原文（注意页尾会混入「相关推荐」，按标题定位正文范围）。搜索用带企业名的查询词提高命中率。**搜不到真题时不要编造** —— 退化并如实标注，绝不伪造企业出处。抓取的中间文件放在 `.fetch/`，不要提交、也不要留在项目根目录污染结构。

### source_tier

| tier | 含义 |
|---|---|
| `company_verified` | 明确企业真题，有可访问 URL，且核对通过 —— 最优先出 |
| `company_unverified` | 面经提及企业但无法核实，或答案未核对通过 —— 标注「回忆版，未核实」 |
| `community` | 社区/仓库整理，未指明企业 |
| `seed` | 本地种子题，`source_url: null`，已验证 |
| `seed_unverified` | 本地种子题且 `verified: false` —— 可出但必须显示争议警告 |
| `generated` | Agent 自拟 —— 最后兜底，必须显式标注 |

三条硬约束：① `company_verified` 的前提是**真有可访问 URL**；② **`verified: false` 的题一律不得标 `company_verified`**（出处权威 ≠ 答案正确）；③ `source` 与 `source_url` 必须互相印证，不允许编造 URL。

**插件题（`plugins`）的出处现状**：牛客讨论页正文已改为客户端渲染 + 登录墙，`curl` 只能拿到 `<meta name="description">` 摘要（实测：`/discuss/<id>` 与 `/feed/main/detail/<id>` 均如此），**插件题目前拿不到可核实的公司真题**。已验证可访问的核对源是：`hybridclr.cn/docs/...`（HybridCLR 官方文档）、`yooasset.com/docs/...`（YooAsset 官方文档）、`docs.unity.cn`（Unity 官方手册）、`learn.microsoft.com`（.NET 官方文档）、`cloud.tencent.cn/developer/article/2304513` 与 `cnblogs.com`（社区整理）。因此插件题目前只标 `community` / `generated`，**联网补题时若找到新的可访问面经 URL，先 curl 核实正文再决定能否升到 `company_unverified`/`company_verified`**。已核实但不通的域名（别浪费时间）：`github.com`、`raw.githubusercontent.com`、`cdn.jsdelivr.net`（会 301 到 raw）、`gitcode.com`（418）、`blog.csdn.net`（521 时好时坏）；`gitee.com/<repo>` 可访问但只给仓库描述。HybridCLR 在 gitee 有镜像仓库可作备用核对源。

### 答案验证

**入库即验证**。依据顺序：官方文档（Unity Docs / Microsoft Learn）> MDN / 语言规范 > 权威教材 > 高赞社区答案。核对通过 → `verified: true` 并在 `verify_note` 写明依据；不通过或有版本差异/工程争议 → `verified: false` 并写明**争议点是什么、两种立场分别是什么**。**面经答案本身可能是错的**（面试者记错、面试官口误），不能因为"这是大厂真题"跳过核对。

## 出题优先级

同类型内按此顺序抽取：① 间隔重复到期题（最高）② 错题重练 ③ 企业真题（`company_verified` > `company_unverified`）④ 本地种子题 / 社区题 ⑤ Agent 自拟题（仅以上都不足时）。

`config.prefer_real_questions` 为 `false` 时只用本地题库，不出网。

## Output Format

按类型分组，每组标注：类型 / 子类型 / 难度；来源（企业名 + URL + `source_tier`，`seed`/`generated` 要显式说明）；是否错题重练 / 间隔重复；题目（答案用 `<details>` 折叠）；验证状态（`verified: false` 必须写出争议点）。
