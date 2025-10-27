#!/usr/bin/env python3
"""
生成微信读书阅读时间热力图
使用修复后的 WeRead API 获取数据
支持动画、多年份统计等高级功能
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
import svgwrite
import pendulum

# 添加项目路径
sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')

from weread2notionpro.weread_api import WeReadApi

def get_color_intensity(minutes, max_minutes, colors):
    """根据阅读时间计算颜色强度"""
    if minutes == 0:
        return colors['dom']
    elif minutes < max_minutes * 0.25:
        return colors['track']
    elif minutes < max_minutes * 0.5:
        return colors['special1']
    else:
        return colors['special2']

def generate_heatmap_svg(read_times, year, user_name="WeRead User", colors=None, with_animation=False):
    """
    生成热力图 SVG
    支持动画和自定义颜色
    """
    if colors is None:
        colors = {
            'background': '#FFFFFF',
            'track': '#ACE7AE',
            'special1': '#69C16E',
            'special2': '#549F57',
            'dom': '#EBEDF0',
            'text': '#000000'
        }

    # 创建 SVG
    dwg = svgwrite.Drawing(f'weread_heatmap_{year}.svg', size=('1600px', '400px'))

    # 如果启用动画，添加 CSS 动画定义
    if with_animation:
        dwg.defs.add(dwg.style("""
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .animated {
                animation: fadeIn 0.5s ease-in;
            }
        """))

    # 背景
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=colors['background']))

    # Title
    title = f"{user_name}'s WeRead Reading Heatmap - {year}"
    title_elem = dwg.text(title, insert=(20, 30), fill=colors['text'],
                         font_size='18px', font_family='Arial')
    if with_animation:
        title_elem['class'] = 'animated'
    dwg.add(title_elem)

    # 计算日期范围
    start_date = pendulum.date(year, 1, 1)
    end_date = pendulum.date(year, 12, 31)

    # 热力图参数
    cell_size = 12
    cell_margin = 2
    start_x = 50
    start_y = 60

        # Month labels (English) - 显示全部月份
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Weekday labels (English)
    weekdays = ['', 'Mon', '', 'Wed', '', 'Fri', '']

    # 统计数据
    max_minutes = max(read_times.values()) if read_times else 0
    total_days = len(read_times)
    total_minutes = sum(read_times.values())

    # 先绘制热力图，记录月份位置
    month_positions = {}  # 记录每个月的起始x位置
    current_date = start_date
    x_offset = 0
    day_count = 0

    while current_date <= end_date:
        # 计算位置
        weekday = current_date.weekday()  # 0=周一, 6=周日

        # 计算当前日期是第几周（相对于起始日期）
        days_diff = (current_date - start_date).days
        week_diff = days_diff // 7
        x_offset = week_diff

        if current_date.day == 1:
            # 记录每个月的起始位置
            month_idx = current_date.month - 1
            month_positions[month_idx] = start_x + x_offset * (cell_size + cell_margin)

        x = start_x + x_offset * (cell_size + cell_margin)
        y = start_y + weekday * (cell_size + cell_margin)

        # 获取该日期的阅读时间
        date_key = int(current_date.format('YYYYMMDD'))
        minutes = read_times.get(date_key, 0)

        # 计算颜色
        fill_color = get_color_intensity(minutes, max_minutes, colors)

        # 绘制方块
        rect_elem = dwg.rect(insert=(x, y), size=(cell_size, cell_size),
                            fill=fill_color, stroke=colors['background'],
                            stroke_width=1)

        # 如果启用动画，为每个方块添加延迟动画
        if with_animation:
            delay = day_count * 0.01  # 每个方块延迟 0.01 秒
            rect_elem['style'] = f'animation: fadeIn 0.5s ease-in {delay}s both;'

        dwg.add(rect_elem)

        current_date = current_date.add(days=1)
        day_count += 1
    # 绘制月份和星期标签（使用记录的实际位置，显示全部月份）
    for month_idx in range(12):
        if month_idx in month_positions:
            x = month_positions[month_idx]
            month_name = months[month_idx]
            month_elem = dwg.text(month_name, insert=(x, start_y - 10),
                                 fill=colors['text'], font_size='10px',
                                 font_family='Arial')
            if with_animation:
                month_elem['class'] = 'animated'
            dwg.add(month_elem)

    # 绘制星期标签
    for i, weekday in enumerate(weekdays):
        if weekday:
            weekday_elem = dwg.text(weekday,
                                   insert=(start_x - 30,
                                          start_y + i * (cell_size + cell_margin) + 8),
                                   fill=colors['text'], font_size='10px',
                                   font_family='Arial')
            if with_animation:
                weekday_elem['class'] = 'animated'
            dwg.add(weekday_elem)

    # 添加统计信息
    stats_y = start_y + 8 * (cell_size + cell_margin) + 40

    stats_elements = [
        f"Total reading days: {total_days} days",
        f"Total reading time: {total_minutes / 60:.1f} hours",
        f"Max daily reading: {max_minutes / 60:.1f} hours" if max_minutes > 0
        else "No reading data yet"
    ]

    for i, stat_text in enumerate(stats_elements):
        stat_elem = dwg.text(stat_text, insert=(start_x, stats_y + i * 20),
                           fill=colors['text'], font_size='14px', font_family='Arial')
        if with_animation:
            stat_elem['style'] = f'animation: fadeIn 0.5s ease-in {1 + i * 0.2}s both;'
        dwg.add(stat_elem)

    return dwg

def generate_multi_year_heatmap(read_times_by_year, user_name="WeRead User", colors=None, with_animation=False):
    """
    生成多年度热力图
    """
    if colors is None:
        colors = {
            'background': '#FFFFFF',
            'track': '#ACE7AE',
            'special1': '#69C16E',
            'special2': '#549F57',
            'dom': '#EBEDF0',
            'text': '#000000'
        }

    # 计算总年份
    years = sorted(read_times_by_year.keys(), reverse=True)  # 从新到旧排序
    if not years:
        return None

    # 计算整体统计
    all_read_times = {}
    for year_data in read_times_by_year.values():
        all_read_times.update(year_data)

    total_days = len(all_read_times)
    total_minutes = sum(all_read_times.values())
    max_minutes = max(all_read_times.values()) if all_read_times else 0

    # 创建 SVG (根据年份数量调整高度)
    height = 200 + len(years) * 180  # 基础高度 + 每年180px
    dwg = svgwrite.Drawing('weread_heatmap_multi_year.svg', size=('1600px', f'{height}px'))

    # 如果启用动画，添加 CSS 动画定义
    if with_animation:
        dwg.defs.add(dwg.style("""
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animated {
                animation: fadeIn 0.8s ease-out forwards;
            }
        """))

    # 背景
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=colors['background']))

    # Main title
    title = f"{user_name}'s WeRead Reading Heatmap (Multi-year Statistics)"
    title_elem = dwg.text(title, insert=(20, 30), fill=colors['text'],
                         font_size='20px', font_family='Arial')
    if with_animation:
        title_elem['class'] = 'animated'
    dwg.add(title_elem)

    # 为每个年份生成热力图
    current_y = 60
    year_count = 0

    for year in years:
        year_data = read_times_by_year[year]

        # Year title
        year_title = f"{year} Year"
        year_elem = dwg.text(year_title, insert=(20, current_y), fill=colors['text'],
                           font_size='16px', font_family='Arial')
        if with_animation:
            year_elem['style'] = f'animation: fadeIn 0.8s ease-out {year_count * 0.3}s both;'
        dwg.add(year_elem)

        # 生成单年热力图 (缩放版)
        year_svg = generate_single_year_section(year_data, year, colors, with_animation, year_count)
        year_svg['transform'] = f'translate(0, {current_y + 10})'
        dwg.add(year_svg)

        # 年份统计
        year_days = len(year_data)
        year_minutes = sum(year_data.values())
        year_max = max(year_data.values()) if year_data else 0

        stats_text = f"{year} Year: {year_days} days {year_minutes / 60:.1f} hours Max {year_max / 60:.1f} hours"
        stats_elem = dwg.text(stats_text, insert=(20, current_y + 150), fill=colors['text'],
                             font_size='12px', font_family='Arial')
        if with_animation:
            stats_elem['style'] = f'animation: fadeIn 0.8s ease-out {year_count * 0.3 + 0.5}s both;'
        dwg.add(stats_elem)

        current_y += 180
        year_count += 1

    # Overall statistics
    summary_y = current_y + 20
    summary_title = dwg.text("Overall Statistics", insert=(20, summary_y), fill=colors['text'],
                           font_size='18px', font_family='Arial')
    if with_animation:
        summary_title['style'] = f'animation: fadeIn 0.8s ease-out {year_count * 0.3}s both;'
    dwg.add(summary_title)

    summary_stats = [
        f"Total reading years: {len(years)} years ({years[0]}-{years[-1]})",
        f"Total reading days: {total_days} days",
        f"Total reading time: {total_minutes / 60:.1f} hours",
        f"Max daily reading: {max_minutes / 60:.1f} hours"
    ]

    for i, stat in enumerate(summary_stats):
        stat_elem = dwg.text(stat, insert=(20, summary_y + 25 + i * 20), fill=colors['text'],
                           font_size='14px', font_family='Arial')
        if with_animation:
            stat_elem['style'] = f'animation: fadeIn 0.8s ease-out {year_count * 0.3 + 0.2 * (i + 1)}s both;'
        dwg.add(stat_elem)

    return dwg

def generate_single_year_section(read_times, year, colors, with_animation, year_index):
    """生成单年热力图部分 (用于多年度视图)"""
    # 创建组元素
    group = svgwrite.container.Group()

    # 计算日期范围
    start_date = pendulum.date(year, 1, 1)
    end_date = pendulum.date(year, 12, 31)

    # 热力图参数 (缩小版)
    cell_size = 8
    cell_margin = 1
    start_x = 50
    start_y = 20

    # 月份标签 (简化)
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    # 统计数据
    max_minutes = max(read_times.values()) if read_times else 0

    # 先绘制热力图，记录月份位置
    month_positions = {}  # 记录每个月的起始x位置
    current_date = start_date
    x_offset = 0
    day_count = 0

    while current_date <= end_date:
        weekday = current_date.weekday()

        # 计算当前日期是第几周（相对于起始日期）
        days_diff = (current_date - start_date).days
        week_diff = days_diff // 7
        x_offset = week_diff

        if current_date.day == 1:
            # 记录每个月的起始位置
            month_idx = current_date.month - 1
            month_positions[month_idx] = start_x + x_offset * (cell_size + cell_margin)

        x = start_x + x_offset * (cell_size + cell_margin)
        y = start_y + weekday * (cell_size + cell_margin)

        date_key = int(current_date.format('YYYYMMDD'))
        minutes = read_times.get(date_key, 0)

        fill_color = get_color_intensity(minutes, max_minutes, colors)

        rect_elem = group.add(svgwrite.shapes.Rect(insert=(x, y),
                                                  size=(cell_size, cell_size),
                                                  fill=fill_color,
                                                  stroke=colors['background'],
                                                  stroke_width=1))

        if with_animation:
            delay = year_index * 0.3 + day_count * 0.005
            rect_elem['style'] = f'animation: fadeIn 0.3s ease-in {delay}s both;'

        current_date = current_date.add(days=1)
        day_count += 1
    for i, month in enumerate(months):
        if i in month_positions:
            x = month_positions[i]
            month_elem = group.add(svgwrite.text.Text(month,
                                                     insert=(x, start_y - 5),
                                                     fill=colors['text'],
                                                     font_size='8px',
                                                     font_family='Arial'))
            if with_animation:
                month_elem['style'] = f'animation: fadeIn 0.5s ease-in {year_index * 0.3 + i * 0.02}s both;'

    return group

def load_cached_data(cache_file='weread_data_cache.json'):
    """Load cached reading data"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📋 Loaded cached data from {cache_file}")
                return data
        except Exception as e:
            print(f"⚠️  Failed to load cache: {e}")
    return None

def save_cached_data(data, cache_file='weread_data_cache.json'):
    """Save reading data to cache"""
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Data cached to {cache_file}")
    except Exception as e:
        print(f"⚠️  Failed to save cache: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate WeRead reading time heatmap')
    parser.add_argument('--year', type=int, help='Specify year (default: current year)')
    parser.add_argument('--me', type=str, help='Username (default: WeRead User)')
    parser.add_argument('--with-animation', action='store_true', help='Enable animation effects')
    parser.add_argument('--multi-year', action='store_true', help='Generate multi-year statistics')
    parser.add_argument('--background-color', default='#FFFFFF', help='Background color')
    parser.add_argument('--track-color', default='#ACE7AE', help='Low intensity color')
    parser.add_argument('--special-color1', default='#69C16E', help='Medium intensity color')
    parser.add_argument('--special-color2', default='#549F57', help='High intensity color')
    parser.add_argument('--dom-color', default='#EBEDF0', help='No data color')
    parser.add_argument('--text-color', default='#000000', help='Text color')
    parser.add_argument('--no-cache', action='store_true', help='Skip cache and fetch fresh data')
    parser.add_argument('--cache-file', default='weread_data_cache.json', help='Cache file path')

    args = parser.parse_args()

    print("🔥 Generate WeRead reading time heatmap...")

    try:
        # Try to load cached data first
        api_data = None
        if not args.no_cache:
            api_data = load_cached_data(args.cache_file)

        if api_data is None:
            print("🔍 Fetching reading statistics data...")
            # Initialize WeRead API
            weread_api = WeReadApi()

            # Get reading data
            api_data = weread_api.get_api_data()

            # Cache the data
            if not args.no_cache:
                save_cached_data(api_data, args.cache_file)

        read_times_raw = api_data.get("readTimes", {})

        # 转换数据格式
        read_times = {}
        read_times_by_year = defaultdict(dict)

        for timestamp, minutes in read_times_raw.items():
            try:
                date_obj = datetime.fromtimestamp(int(timestamp))
                date_key = int(date_obj.strftime('%Y%m%d'))
                year = date_obj.year
                read_times[date_key] = minutes
                read_times_by_year[year][date_key] = minutes
            except (ValueError, OSError) as e:
                print(f"⚠️  跳过无效时间戳: {timestamp} ({e})")
                continue

        print(f"📊 处理了 {len(read_times)} 天的阅读数据")

        # 颜色配置
        colors = {
            'background': args.background_color,
            'track': args.track_color,
            'special1': args.special_color1,
            'special2': args.special_color2,
            'dom': args.dom_color,
            'text': args.text_color
        }

        # 用户名
        user_name = args.me or os.getenv('HEATMAP_USER_NAME', 'WeRead User')

        # 年份
        if args.multi_year:
            # 多年度统计
            print("📈 生成多年度热力图...")
            dwg = generate_multi_year_heatmap(read_times_by_year, user_name, colors, args.with_animation)
            output_file = 'weread_heatmap_multi_year.svg'
        else:
            # 单年统计
            year = args.year or datetime.now().year
            print(f"📅 生成 {year} 年热力图...")
            year_data = read_times_by_year.get(year, {})
            dwg = generate_heatmap_svg(year_data, year, user_name, colors, args.with_animation)
            output_file = f'weread_heatmap_{year}.svg'

        if dwg is None:
            print("❌ 没有找到阅读数据")
            return False

        # 保存 SVG 文件
        output_dir = './OUT_FOLDER'
        os.makedirs(output_dir, exist_ok=True)

        dwg.save()

        # 移动到正确位置
        final_output = os.path.join(output_dir, 'weread_heatmap.svg')
        if os.path.exists(output_file):
            os.rename(output_file, final_output)

        print(f"✅ 热力图已生成: {final_output}")

        # 显示统计信息
        if read_times:
            total_days = len(read_times)
            total_minutes = sum(read_times.values())
            max_minutes = max(read_times.values())
            print(f"📈 统计信息:")
            print(f"   总阅读天数: {total_days} 天")
            print(f"   总阅读时间: {total_minutes / 60:.1f} 小时")
            print(f"   最高日阅读: {max_minutes / 60:.1f} 小时")

        if args.with_animation:
            print("🎬 已启用动画效果")

        return True

    except Exception as e:
        print(f"❌ 生成热力图失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    main()