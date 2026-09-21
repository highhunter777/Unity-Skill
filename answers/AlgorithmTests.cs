// ============================================================
// Unity 面试刷题 · 测试与入口
// 生成时间: 2026-09-21
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



    // ==========================================================
    // [1] algo_023 · hard · 最大频率栈
    // ==========================================================
    public static class Solution_algo023_Tests
    {
        public static void Run()
        {
            Console.WriteLine("=== algo_023 最大频率栈 ===");
            var s023 = new Solution_algo023();
            var popped = s023.Simulate(new[] { 5, 7, 5, 7, 4, 5, 0, 0, 0, 0 });
            Console.WriteLine(string.Join(",", popped) + "  期望 5,7,5,4");
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
            // Solution_algo023_Tests.Run();   // [1] 最大频率栈
            Console.WriteLine("提示: 在 Main 里取消对应测试的注释即可运行。");
        }
    }
}
