#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答题区生成/解析。

生成两个文件：
  answers/Algorithm.cs       —— 题目 + 你的实现（干净，只在这里写代码）
  answers/AlgorithmTests.cs  —— 节点类 + 测试 + Main 入口（不要改）

用法:
    python tools/make_answers.py --init              # 初始化空文件
    python tools/make_answers.py --status            # 显示答题进度
    python tools/make_answers.py --read              # 读回并解析作答
    python tools/make_answers.py --selftest          # 端到端自测
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANSWERS = os.path.join(ROOT, "answers")
CS_FILE = os.path.join(ANSWERS, "Algorithm.cs")
TEST_FILE = os.path.join(ANSWERS, "AlgorithmTests.cs")
DOCX_FILE = os.path.join(ANSWERS, "答题区.docx")

TYPE_CN = {
    "algorithm": "算法题", "bagu": "Unity/C# 八股", "design": "设计题",
    "math": "数学考察", "cs_basics": "计算机基础", "rendering": "渲染/TA",
    # 插件类：hybridclr / xlua / yooasset / unitask
    "plugins": "第三方插件",
}


# ================================================================ 实现文件

CS_HEADER = """// ============================================================
// Unity 面试刷题 · 算法实现
// 生成时间: {date}
//
// 在这里写你的解法。测试代码在 AlgorithmTests.cs，不要改那个文件。
// 写完后在 AlgorithmTests.cs 的 Main 里取消对应测试的注释，然后运行。
// ============================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace InterviewDrill
{{
"""

CS_LEETCODE = """
    // ----------------------------------------------------------
    // [{idx}] {qid} · {difficulty} · {subtype}
    // {title}
    // {desc}
    // 示例: {example}
    // ----------------------------------------------------------
    public class {cls}
    {{
        // TODO: 在此实现（方法必须是 public，否则 AlgorithmTests.cs 里的测试类访问不到）
        public {ret} {method}({params})
        {{
            throw new NotImplementedException();
        }}
    }}
"""

CS_ACM = """
    // ----------------------------------------------------------
    // [{idx}] {qid} · {difficulty} · {subtype} · ACM 形式
    // {title}
    // {desc}
    // 输入格式: {input_fmt}
    // 输出格式: {output_fmt}
    // 示例: {example}
    // ----------------------------------------------------------
    public static class {cls}
    {{
        // TODO: 在此实现（自己处理输入输出）
        public static void Solve()
        {{
            throw new NotImplementedException();
        }}
    }}
"""


def _cls_name(qid):
    return "Solution_" + qid.replace("_", "")


def write_cs(problems, mode="leetcode", date=""):
    """生成 answers/Algorithm.cs（只有题目与空实现）和 answers/AlgorithmTests.cs。"""
    impl = [CS_HEADER.format(date=date)]
    tests = [CS_TEST_HEADER.format(date=date, node_defs=_detect_node_defs(problems))]
    dispatch = []

    for i, p in enumerate(problems, 1):
        fmt = p.get("form", mode)
        cls = _cls_name(p["id"])
        common = dict(
            idx=i, qid=p["id"], difficulty=p.get("difficulty", ""),
            subtype=p.get("subtype", ""), title=p.get("title", ""),
            desc=p.get("desc", ""), example=p.get("example", "（无）"), cls=cls,
        )
        if fmt == "acm":
            impl.append(CS_ACM.format(
                input_fmt=p.get("input_fmt", "（未指定）"),
                output_fmt=p.get("output_fmt", "（未指定）"), **common))
            dispatch.append(f"            // {cls}.Solve();   // [{i}] {p.get('title','')} (ACM)")
        else:
            impl.append(CS_LEETCODE.format(
                ret=p.get("ret", "object"), method=p.get("method", "Solve"),
                params=p.get("params", ""), **common))
            tests.append(CS_TEST_CLASS.format(
                testcases=p.get("testcases") or "            // （待补充测试用例）",
                **common))
            dispatch.append(DISPATCH.format(cls=cls, idx=i, title=p.get("title", "")))

    impl.append("}\n")
    if not dispatch:
        dispatch.append("            // （本次没有算法题）")
    tests.append(CS_TEST_FOOTER.format(dispatches="\n".join(dispatch)))

    os.makedirs(ANSWERS, exist_ok=True)
    with open(CS_FILE, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("".join(impl))
    with open(TEST_FILE, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("".join(tests))
    return CS_FILE, TEST_FILE


# ---------------------------------------------------------------- 测试文件

CS_TEST_HEADER = """// ============================================================
// Unity 面试刷题 · 测试与入口
// 生成时间: {date}
//
// 本文件由 tools/make_answers.py 生成，不要手动修改 ——
// 下次出题会覆盖它。你的实现请写在 Algorithm.cs。
//
// 用法: 在 Main 里取消对应测试的注释，然后运行。
//   VS Code : 直接 F5（已配好 launch.json）或 dotnet run
//   VS 2022 : 双击 AlgorithmDrill.sln 后 F5
//   命令行  : cd answers && dotnet run
// ============================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace InterviewDrill
{{
{node_defs}
"""

CS_TEST_CLASS = """
    // ==========================================================
    // [{idx}] {qid} · {difficulty} · {title}
    // ==========================================================
    public static class {cls}_Tests
    {{
        public static void Run()
        {{
            Console.WriteLine("=== {qid} {title} ===");
{testcases}
            Console.WriteLine();
        }}
    }}
"""

CS_TEST_FOOTER = """}}

namespace InterviewDrill
{{
    // ============================================================
    // 入口点
    // ============================================================
    public static class Program
    {{
        public static void Main(string[] args)
        {{
            Console.WriteLine("Unity 面试刷题 · 算法题自测\\n");
{dispatches}
            Console.WriteLine("提示: 在 Main 里取消对应测试的注释即可运行。");
        }}
    }}
}}
"""

DISPATCH = """            // {cls}_Tests.Run();   // [{idx}] {title}"""


# ---------------------------------------------------------------- 节点类

# 注入到 CS_TEST_HEADER 的 {node_defs} 占位符，
# 该占位符的值在 .format() 时传入，内容不参与 format，故用单花括号。
NODE_DEFS = {
    "listnode": """    // 单链表节点（LeetCode 风格）
    public class ListNode
    {
        public int val;
        public ListNode next;
        public ListNode(int val = 0, ListNode next = null)
        {
            this.val = val;
            this.next = next;
        }
    }
""",
    "treenode": """    // 二叉树节点（LeetCode 风格）
    public class TreeNode
    {
        public int val;
        public TreeNode left;
        public TreeNode right;
        public TreeNode(int val = 0, TreeNode left = null, TreeNode right = null)
        {
            this.val = val;
            this.left = left;
            this.right = right;
        }
    }
""",
    "buildlist": """    // 测试辅助：从数组构造单链表，返回头节点（空数组返回 null）
    public static class ListBuilder
    {
        public static ListNode BuildList(params int[] vals)
        {
            ListNode dummy = new ListNode(), cur = dummy;
            foreach (var v in vals) { cur.next = new ListNode(v); cur = cur.next; }
            return dummy.next;
        }

        public static string Dump(ListNode head)
        {
            var sb = new StringBuilder();
            while (head != null)
            {
                if (sb.Length > 0) sb.Append("->");
                sb.Append(head.val);
                head = head.next;
            }
            return sb.Length > 0 ? sb.ToString() : "(空)";
        }
    }
""",
    "buildtree": """    // 测试辅助：从层序数组构造二叉树（null 为空节点），以及层序打印
    public static class TreeBuilder
    {
        public static TreeNode BuildTree(int?[] a)
        {
            if (a == null || a.Length == 0 || a[0] == null) return null;
            var root = new TreeNode(a[0].Value);
            var q = new Queue<TreeNode>();
            q.Enqueue(root);
            int i = 1;
            while (q.Count > 0 && i < a.Length)
            {
                var cur = q.Dequeue();
                if (i < a.Length && a[i] != null) { cur.left = new TreeNode(a[i].Value); q.Enqueue(cur.left); }
                i++;
                if (i < a.Length && a[i] != null) { cur.right = new TreeNode(a[i].Value); q.Enqueue(cur.right); }
                i++;
            }
            return root;
        }
    }
""",
}


def _detect_node_defs(problems):
    """扫描题目签名，判断需要注入哪些节点类与辅助方法。"""
    need = set()
    for p in problems:
        sig = f"{p.get('ret','')} {p.get('params','')} {p.get('testcases','')}"
        if "ListNode" in sig:
            need.add("listnode")
        if "TreeNode" in sig:
            need.add("treenode")
        # 题目需要从数组构造时，注入对应的 Build 辅助方法
        if "BuildList(" in sig:
            need.add("buildlist")
        if "BuildTree(" in sig:
            need.add("buildtree")
    order = ("listnode", "treenode", "buildlist", "buildtree")
    return "\n".join(NODE_DEFS[k] for k in order if k in need) or "\n"


# ================================================================ 读回

def read_cs():
    """读回 Algorithm.cs，返回 {qid: {'code': 解法代码, 'solved': 是否已实现}}。"""
    if not os.path.exists(CS_FILE):
        return {}
    src = open(CS_FILE, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"public\s+(?:static\s+)?class\s+Solution_(\w+)\b", src):
        raw = m.group(1)
        if "_Tests" in src[m.start():m.start() + 60]:
            continue
        qid = _restore_qid(raw) or raw
        i = src.index("{", m.end())
        depth, j = 0, i
        while j < len(src):
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = src[i + 1:j]
        out[qid] = {
            "code": body.strip(),
            "solved": "NotImplementedException" not in body,
        }
    return out


def _restore_qid(raw):
    """algo016 -> algo_016"""
    m = re.match(r"^([a-z_]+?)(\d+)$", raw)
    return f"{m.group(1)}_{m.group(2).zfill(3)}" if m else None


# ================================================================ docx

def write_docx(items, date=""):
    """生成 answers/答题区.docx。items 支持题库格式（id 或 qid 均可）。"""
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h.add_run("Unity 面试刷题 · 答题区")
    r.bold = True
    r.font.size = Pt(18)

    for txt in (f"生成日期：{date}",
                "在每道题的「作答：」下方写下你的答案，写完告诉 Claude 已作答。"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    for i, it in enumerate(items, 1):
        qid = it.get("qid") or it.get("id")
        if not qid:
            raise KeyError("题目缺少 id/qid 字段")
        doc.add_paragraph()

        p = doc.add_paragraph()
        r = p.add_run(f"【{i}】{qid} · "
                      f"{TYPE_CN.get(it.get('type',''), it.get('type',''))} · "
                      f"{it.get('difficulty','')}")
        r.bold = True
        r.font.size = Pt(13)

        question = it.get("question", "")
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(14)
        if it.get("title"):
            tr = p.add_run(it["title"] + "\n")
            tr.bold = True
        qr = p.add_run(question)
        # 题目里的换行在 docx 里要显示成真换行（Word 收到裸 \n 会挤成一行），
        # 否则多选题干、代码块会全部糊成一整段。
        if "\n" in question:
            from docx.oxml.ns import qn
            qr._r.clear_content()
            for j, line in enumerate(question.split("\n")):
                if j:
                    qr._r.append(qr._r.makeelement(qn("w:br"), {}))
                if line:
                    t = qr._r.makeelement(qn("w:t"), {})
                    t.set(qn("xml:space"), "preserve")
                    t.text = line
                    qr._r.append(t)

        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(14)
        r = p.add_run("作答：")
        r.bold = True

        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(14)
        r = p.add_run("（在此作答）")
        r.font.color.rgb = RGBColor(0xA0, 0xA0, 0xA0)

        # 场景题/决策题题干长、要求分点作答，留几行空行方便直接写
        answer_lines = 3 if it.get("subtype") in ("scenario_design", "scenario_decision") else 1
        ind = p.paragraph_format.left_indent
        for _ in range(answer_lines):
            blank = doc.add_paragraph()
            blank.paragraph_format.left_indent = ind

        p = doc.add_paragraph()
        r = p.add_run("─" * 40)
        r.font.color.rgb = RGBColor(0xC0, 0xC0, 0xC0)

    os.makedirs(ANSWERS, exist_ok=True)
    doc.save(DOCX_FILE)
    return DOCX_FILE


def parse_answers():
    """解析 docx 中每道题的作答，返回 {qid: 作答文本}。"""
    if not os.path.exists(DOCX_FILE):
        return {}
    from docx import Document
    paras = [p.text.strip() for p in Document(DOCX_FILE).paragraphs]

    out, cur, buf, grab = {}, None, [], False
    for s in paras:
        m = re.match(r"^【\d+】(\S+?)\s·", s)
        if m:
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur, buf, grab = m.group(1), [], False
            # 题目正文（含多行）是标签行之后的段落，grab 仍为 False，会被跳过
            continue
        if cur is None:
            continue
        if s.startswith("作答："):
            grab = True
            continue
        if s.startswith("─" * 5):
            out[cur] = "\n".join(buf).strip()
            cur, buf, grab = None, [], False
            continue
        if grab and s and s != "（在此作答）":
            buf.append(s)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def read_docx():
    if not os.path.exists(DOCX_FILE):
        return ""
    from docx import Document
    return "\n".join(p.text for p in Document(DOCX_FILE).paragraphs)


# ================================================================ 编辑器配置

# 目标框架。必须 <= VS 2022 内置 MSBuild 支持的版本 ——
# 本机 VS 2022 17.14 只认到 net9.0，写 net10.0 会导致 VS 报 NETSDK1045 无法加载项目。
# 改这个值时要同步改下面的 launch.json 路径，故用同一常量拼接。
TARGET_FRAMEWORK = "net9.0"

CSPROJ = f"""<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <!-- {TARGET_FRAMEWORK}：VS 2022 17.14 最高支持到此，改高会导致 VS 无法加载项目 -->
    <TargetFramework>{TARGET_FRAMEWORK}</TargetFramework>
    <Nullable>disable</Nullable>
    <LangVersion>latest</LangVersion>
    <RootNamespace>InterviewDrill</RootNamespace>
    <AssemblyName>AlgorithmDrill</AssemblyName>
    <ImplicitUsings>disable</ImplicitUsings>
    <RunWorkingDirectory>$(MSBuildProjectDirectory)</RunWorkingDirectory>
  </PropertyGroup>

  <!-- 排除 *.template.cs：它们是空模板，被 SDK 默认 glob 编译会与运行时文件重复定义 -->
  <ItemGroup>
    <Compile Remove="*.template.cs" />
  </ItemGroup>

</Project>
"""

SLN = """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "AlgorithmDrill", "AlgorithmDrill.csproj", "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"
EndProject
Global
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tDebug|Any CPU = Debug|Any CPU
\t\tRelease|Any CPU = Release|Any CPU
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
\t\t{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}.Debug|Any CPU.Build.0 = Debug|Any CPU
\t\t{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}.Release|Any CPU.ActiveCfg = Release|Any CPU
\t\t{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}.Release|Any CPU.Build.0 = Release|Any CPU
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

VSCODE_LAUNCH = """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "运行算法测试",
      "type": "coreclr",
      "request": "launch",
      "preLaunchTask": "build",
      "program": "${workspaceFolder}/bin/Debug/""" + TARGET_FRAMEWORK + """/AlgorithmDrill.dll",
      "args": [],
      "cwd": "${workspaceFolder}",
      "console": "internalConsole",
      "stopAtEntry": false
    }
  ]
}"""

VSCODE_TASKS = """{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "build",
      "command": "dotnet",
      "type": "process",
      "args": ["build", "${workspaceFolder}/AlgorithmDrill.csproj", "/property:GenerateFullPaths=true"],
      "problemMatcher": "$msCompile",
      "group": { "kind": "build", "isDefault": true }
    }
  ]
}"""

GITIGNORE = "bin/\nobj/\n*.user\n"


def write_editor_config():
    """写 csproj、sln、VS Code 的 .vscode/ 配置与 .gitignore。

    注意：sln/csproj 只在**不存在时**创建，避免覆盖用户的手动修改
    （如 VS 添加的配置、用户改的目标框架）。
    """
    os.makedirs(ANSWERS, exist_ok=True)
    vsc = os.path.join(ANSWERS, ".vscode")
    os.makedirs(vsc, exist_ok=True)

    csproj = os.path.join(ANSWERS, "AlgorithmDrill.csproj")
    if not os.path.exists(csproj):
        with open(csproj, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(CSPROJ)

    sln = os.path.join(ANSWERS, "AlgorithmDrill.sln")
    if not os.path.exists(sln):
        with open(sln, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(SLN)

    with open(os.path.join(vsc, "launch.json"), "w", encoding="utf-8") as f:
        f.write(VSCODE_LAUNCH)
    with open(os.path.join(vsc, "tasks.json"), "w", encoding="utf-8") as f:
        f.write(VSCODE_TASKS)
    with open(os.path.join(ANSWERS, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(GITIGNORE)


# ================================================================ CLI

def selftest():
    import shutil
    bak = {}
    for f in (CS_FILE, TEST_FILE, DOCX_FILE):
        if os.path.exists(f):
            bak[f] = f + ".bak"
            shutil.copy(f, bak[f])
    try:
        algo = [
            {"id": "algo_026", "difficulty": "easy", "subtype": "linked_list",
             "title": "反转链表", "desc": "反转单链表返回新头。", "example": "1->2->3 → 3->2->1",
             "ret": "ListNode", "method": "ReverseList", "params": "ListNode head",
             "testcases": '            var s = new Solution_algo026();\n'
                          '            Console.WriteLine(s.ReverseList(new ListNode(1)).val + "  期望 1");'},
            {"id": "algo_017", "difficulty": "easy", "subtype": "array_string",
             "form": "acm", "title": "A+B", "desc": "读两个整数输出和。",
             "input_fmt": "一行 a b", "output_fmt": "a+b", "example": "1 2 → 3"},
        ]
        write_cs(algo, mode="leetcode", date="2026-09-21")
        write_docx([
            {"qid": "bagu_027", "type": "bagu", "difficulty": "medium", "question": "请简述协程原理。"},
            {"id": "math_016", "type": "math", "difficulty": "medium", "question": "请写出投影公式。"},
            {"id": "plugins_001", "type": "plugins", "difficulty": "medium",
             "question": "主流代码热更方案有哪些？"},
        ], date="2026-09-21")

        ok = []
        impl = open(CS_FILE, encoding="utf-8").read()
        tst = open(TEST_FILE, encoding="utf-8").read()

        ok.append(("实现文件不含测试类", "_Tests" not in impl and "static void Main" not in impl))
        ok.append(("实现文件只有题目", "public class Solution_algo026" in impl))
        ok.append(("测试文件含测试类", "Solution_algo026_Tests" in tst))
        ok.append(("测试文件含 Main", "static void Main" in tst))
        ok.append(("节点类注入到测试文件", "public class ListNode" in tst))
        ok.append(("节点类未污染实现文件", "class ListNode" not in impl))

        cs = read_cs()
        ok.append(("读回 2 道题", len(cs) == 2))
        ok.append(("均未实现", all(not v["solved"] for v in cs.values())))
        ok.append(("qid 正确还原", set(cs) == {"algo_026", "algo_017"}))

        a = parse_answers()
        ok.append(("docx 解析 3 题", len(a) == 3))
        ok.append(("id/qid 两种键都支持", {"bagu_027", "math_016"} <= set(a)))
        ok.append(("新增类型 plugins 能解析", "plugins_001" in a))

        # 模拟实现 algo_026，确认检测到
        src = impl.replace("throw new NotImplementedException();", "return head;", 1)
        open(CS_FILE, "w", encoding="utf-8", newline="\r\n").write(src)
        cs2 = read_cs()
        ok.append(("检测到 algo_026 已实现", cs2.get("algo_026", {}).get("solved") is True))
        ok.append(("algo_017 仍未实现", cs2.get("algo_017", {}).get("solved") is False))

        print("=== 自测结果 ===")
        for n, p in ok:
            print(f"  {'✅' if p else '❌'} {n}")
        return all(p for _, p in ok)
    finally:
        for f, b in bak.items():
            shutil.move(b, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--read", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--date", default="")
    args = ap.parse_args()

    if args.init:
        write_cs([], date=args.date)
        write_docx([], date=args.date)
        write_editor_config()
        print(f"已初始化:\n  {CS_FILE}\n  {TEST_FILE}\n  {DOCX_FILE}\n  {ANSWERS}/.vscode/")
    elif args.status:
        for label, f in (("实现文件", CS_FILE), ("测试文件", TEST_FILE), ("docx    ", DOCX_FILE)):
            ex = os.path.exists(f)
            print(f"{label}: {'存在' if ex else '缺失'} {os.path.getsize(f) if ex else 0}B  {f}")
        ans, cs = parse_answers(), read_cs()
        print(f"\ndocx 作答: {sum(1 for v in ans.values() if v)}/{len(ans)} 道已答")
        print(f"C# 作答 : {sum(1 for v in cs.values() if v['solved'])}/{len(cs)} 道已实现")
    elif args.read:
        print("=== docx 作答 ===")
        for qid, a in parse_answers().items():
            print(f"  {qid}: {a[:80] if a else '（未作答）'}")
        print("\n=== C# 作答 ===")
        for qid, v in read_cs().items():
            print(f"  {qid}: {'已实现' if v['solved'] else '未实现'}")
    elif args.selftest:
        sys.exit(0 if selftest() else 1)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
