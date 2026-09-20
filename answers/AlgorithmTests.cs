// ============================================================
// Unity 面试刷题 · 测试与入口
// 生成时间: 2026-09-20
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
{
    // 单链表节点（LeetCode 风格）
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


    // ==========================================================
    // [1] algo_007 · easy · 两数之和
    // ==========================================================
    public static class Solution_algo007_Tests
    {
        public static void Run()
        {
            Console.WriteLine("=== algo_007 两数之和 ===");
            var s007 = new Solution_algo007();
            Console.WriteLine(string.Join(",", s007.TwoSum(new[] { 2, 7, 11, 15 }, 9)) + "  期望 0,1");
            Console.WriteLine(string.Join(",", s007.TwoSum(new[] { 3, 2, 4 }, 6)) + "  期望 1,2");
            Console.WriteLine(string.Join(",", s007.TwoSum(new[] { 3, 3 }, 6)) + "  期望 0,1");
            Console.WriteLine();
        }
    }

    // ==========================================================
    // [2] algo_026 · easy · 反转链表
    // ==========================================================
    public static class Solution_algo026_Tests
    {
        public static void Run()
        {
            Console.WriteLine("=== algo_026 反转链表 ===");
            var s026 = new Solution_algo026();
            ListNode Build026(int[] a) { ListNode d = new ListNode(0), t = d; foreach (var v in a) { t.next = new ListNode(v); t = t.next; } return d.next; }
            string Show026(ListNode h) { var sb = new StringBuilder(); while (h != null) { if (sb.Length > 0) sb.Append("->"); sb.Append(h.val); h = h.next; } return sb.Length == 0 ? "(空)" : sb.ToString(); }
            Console.WriteLine(Show026(s026.ReverseList(Build026(new[] { 1, 2, 3, 4, 5 }))) + "  期望 5->4->3->2->1");
            Console.WriteLine(Show026(s026.ReverseList(Build026(new[] { 1 }))) + "  期望 1");
            Console.WriteLine(Show026(s026.ReverseList(null)) + "  期望 (空)");
            Console.WriteLine();
        }
    }
}

namespace InterviewDrill
{
    // ============================================================
    // 入口点
    // ============================================================
    public static class Program
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("Unity 面试刷题 · 算法题自测\n");
            // Solution_algo007_Tests.Run();   // [1] 两数之和
            // Solution_algo026_Tests.Run();   // [2] 反转链表
            Console.WriteLine("提示: 在 Main 里取消对应测试的注释即可运行。");
        }
    }
}
