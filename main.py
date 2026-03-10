#!/usr/bin/env python3
"""
跨平台本地打印机 CLI

提供 CLI 命令来操作本地打印机，支持 Windows、macOS、Linux。
配合 AI Skill 系统（OpenClaw / Cursor / Claude 等）使用。

用法:
    printer-ai printers              # 列出打印机
    printer-ai status [INDEX]        # 获取打印机状态
    printer-ai attrs [INDEX]         # 获取打印机属性
    printer-ai print FILE            # 打印文件
    printer-ai jobs                  # 列出打印任务
    printer-ai job-status JOB_ID     # 查询任务状态
    printer-ai cancel-job JOB_ID     # 取消打印任务
"""

import argparse
import json
import sys
from sys import platform

# 根据系统平台导入对应的打印机模块
if platform == "win32":
    from local_printer.windows import (
        get_printer_list as _get_printer_list,
        get_printer_status as _get_printer_status,
        get_printer_attrs as _get_printer_attrs,
        print_file as _print_file,
        get_print_jobs as _get_print_jobs,
        get_print_job_status as _get_print_job_status,
        cancel_print_job as _cancel_print_job,
    )
    from models.model import WindowsPrintOptions as PrintOptionsClass
elif platform == "linux" or platform == "darwin":
    from local_printer.cups import (
        get_printer_list as _get_printer_list,
        get_printer_status as _get_printer_status,
        get_printer_attrs as _get_printer_attrs,
        print_file as _print_file,
        get_print_jobs as _get_print_jobs,
        get_print_job_status as _get_print_job_status,
        cancel_print_job as _cancel_print_job,
    )
    from models.model import LinuxPrintOptions as PrintOptionsClass
else:
    _get_printer_list = None
    _get_printer_status = None
    _get_printer_attrs = None
    _print_file = None
    _get_print_jobs = None
    _get_print_job_status = None
    _cancel_print_job = None
    PrintOptionsClass = None


def output_json(data):
    """输出 JSON（便于 AI 解析）"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def check_platform():
    """检查平台是否支持"""
    if platform not in ("win32", "linux", "darwin"):
        print(f"❌ 不支持的操作系统: {platform}", file=sys.stderr)
        sys.exit(1)


# ==================== 子命令实现 ====================


def cmd_printers(args):
    """列出打印机"""
    check_platform()
    result = _get_printer_list()

    if args.json:
        output_json(result)
        return

    if result.get("code") != 200:
        print(f"❌ 获取打印机列表失败: {result.get('msg', '')}", file=sys.stderr)
        sys.exit(1)

    printers = result.get("data", {}).get("printers", [])
    default_printer = result.get("data", {}).get("default_printer", "")

    if not printers:
        print("未找到打印机")
        return

    print(f"找到 {len(printers)} 台打印机:\n")
    for p in printers:
        default_mark = " ⭐默认" if p.get("is_default") else ""
        status = p.get("status", "unknown")
        status_icon = {"idle": "🟢", "processing": "🟡", "stopped": "🔴"}.get(status, "⚪")
        print(f"  [{p.get('index')}] {p.get('name', '未知')}{default_mark}")
        print(f"      状态: {status_icon} {status}  |  型号: {p.get('model', '未知')}")
        if p.get("location"):
            print(f"      位置: {p.get('location')}")


def cmd_status(args):
    """获取打印机状态"""
    check_platform()
    result = _get_printer_status(args.index)

    if args.json:
        output_json(result)
        return

    if result.get("code") != 200:
        print(f"❌ 获取打印机状态失败: {result.get('msg', '')}", file=sys.stderr)
        sys.exit(1)

    data = result.get("data", {})
    status = data.get("status", "unknown")
    status_icon = {"idle": "🟢", "processing": "🟡", "stopped": "🔴"}.get(status, "⚪")
    print(f"打印机: {data.get('name', '未知')}")
    print(f"状态: {status_icon} {status}")
    print(f"接受任务: {'✅ 是' if data.get('is_accepting_jobs') else '❌ 否'}")


def cmd_attrs(args):
    """获取打印机属性"""
    check_platform()
    result = _get_printer_attrs(args.index)
    output_json(result)


def cmd_print(args):
    """打印文件"""
    check_platform()
    import os

    if not os.path.exists(args.file_path):
        print(f"❌ 文件不存在: {args.file_path}", file=sys.stderr)
        sys.exit(1)

    # 解析打印选项
    print_options = None
    if args.options and PrintOptionsClass:
        try:
            options_dict = json.loads(args.options)
            print_options = PrintOptionsClass.from_dict(options_dict)
        except json.JSONDecodeError:
            print("❌ 打印选项 JSON 格式错误", file=sys.stderr)
            sys.exit(1)

    result = _print_file(args.index, args.file_path, print_options)

    if result.get("code") == 200:
        data = result.get("data", {})
        job_id = data.get("job_id", "")
        print(f"✅ 打印任务已提交  job_id: {job_id}")
        print(f"   打印机: {data.get('printer_name', '')}")
        print(f"   文件: {data.get('file_path', '')}")
        print(f"   查询状态: printer-ai job-status {job_id}")
    else:
        print(f"❌ 打印失败: {result.get('msg', '')}", file=sys.stderr)
        output_json(result)
        sys.exit(1)


def cmd_jobs(args):
    """列出打印任务"""
    check_platform()
    result = _get_print_jobs(args.printer)

    if args.json:
        output_json(result)
        return

    if result.get("code") != 200:
        print(f"❌ 获取打印任务失败: {result.get('msg', '')}", file=sys.stderr)
        sys.exit(1)

    jobs = result.get("data", {}).get("jobs", [])
    if not jobs:
        print("没有打印任务")
        return

    print(f"共 {len(jobs)} 个打印任务:\n")
    for job in jobs:
        status = job.get("status", "unknown")
        status_icon = {
            "pending": "⏳", "processing": "🔄", "completed": "✅",
            "canceled": "🚫", "aborted": "❌"
        }.get(status, "⚪")
        print(f"  [{job.get('job_id')}] {job.get('job_name', '未知')}  {status_icon} {status}")
        print(f"      打印机: {job.get('printer_name', '')}")


def cmd_job_status(args):
    """查询打印任务状态（同时返回打印机状态）"""
    check_platform()
    result = _get_print_job_status(args.job_id)

    # 获取打印机状态并合并到结果中
    printer_name = result.get("data", {}).get("printer_name", "")
    if printer_name and result.get("code") == 200:
        # 从打印机列表中找到对应打印机的 index
        printer_list_result = _get_printer_list()
        if printer_list_result.get("code") == 200:
            for p in printer_list_result["data"].get("printers", []):
                if p.get("name") == printer_name:
                    status_result = _get_printer_status(p["index"])
                    if status_result.get("code") == 200:
                        result["data"]["printer_status"] = status_result["data"]
                    break

    output_json(result)


def cmd_cancel_job(args):
    """取消打印任务"""
    check_platform()
    result = _cancel_print_job(args.job_id)
    output_json(result)
    if result.get("code") == 200:
        print("✅ 打印任务已取消")


# ==================== 主入口 ====================


def main():
    parser = argparse.ArgumentParser(
        prog="printer-ai",
        description="跨平台本地打印机 CLI - 让 AI 驱动本地打印",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # printers
    p_printers = subparsers.add_parser("printers", help="列出打印机")
    p_printers.add_argument("--json", action="store_true", help="JSON 格式输出")
    p_printers.set_defaults(func=cmd_printers)

    # status
    p_status = subparsers.add_parser("status", help="获取打印机状态")
    p_status.add_argument("index", type=int, nargs="?", default=None,
                          help="打印机索引 (从1开始，默认: 默认打印机)")
    p_status.add_argument("--json", action="store_true", help="JSON 格式输出")
    p_status.set_defaults(func=cmd_status)

    # attrs
    p_attrs = subparsers.add_parser("attrs", help="获取打印机属性")
    p_attrs.add_argument("index", type=int, nargs="?", default=None,
                         help="打印机索引 (从1开始)")
    p_attrs.set_defaults(func=cmd_attrs)

    # print
    p_print = subparsers.add_parser("print", help="打印文件")
    p_print.add_argument("file_path", help="要打印的文件路径")
    p_print.add_argument("--index", type=int, default=None,
                         help="打印机索引 (从1开始，默认: 默认打印机)")
    p_print.add_argument("--options", help="打印选项 (JSON 格式字符串)")
    p_print.set_defaults(func=cmd_print)

    # jobs
    p_jobs = subparsers.add_parser("jobs", help="列出打印任务")
    p_jobs.add_argument("--printer", default=None, help="筛选指定打印机名称")
    p_jobs.add_argument("--json", action="store_true", help="JSON 格式输出")
    p_jobs.set_defaults(func=cmd_jobs)

    # job-status
    p_js = subparsers.add_parser("job-status", help="查询打印任务状态")
    p_js.add_argument("job_id", type=int, help="任务 ID")
    p_js.set_defaults(func=cmd_job_status)

    # cancel-job
    p_cj = subparsers.add_parser("cancel-job", help="取消打印任务")
    p_cj.add_argument("job_id", type=int, help="任务 ID")
    p_cj.set_defaults(func=cmd_cancel_job)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
