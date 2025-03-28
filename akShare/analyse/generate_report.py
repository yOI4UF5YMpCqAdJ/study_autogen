import sys
import os
from datetime import datetime
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.db_manager import db_manager

def load_config():
    """加载.env配置文件"""
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    return {
        'queryNum': int(os.getenv('QUERY_NUM', 5)),
        'multiple': {
            'low': float(os.getenv('MULTIPLE_LOW', 2)),
            'high': float(os.getenv('MULTIPLE_HIGH', -1))
        },
        'exceedMultiple': float(os.getenv('EXCEED_MULTIPLE', 2)),
        'queryDate': os.getenv('QUERY_DATE', 'auto')
    }

def print_debug(msg):
    """打印调试信息"""
    print(f"DEBUG: {msg}")

def get_quarter_dates():
    """获取所有季度末日期"""
    return [
        (3, 31),
        (6, 30),
        (9, 30),
        (12, 31)
    ]

def get_next_quarter_end():
    """获取下一个最近的季度末日期（用于预报业绩变动）"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day

    quarter_dates = get_quarter_dates()

    for q_month, q_day in quarter_dates:
        if month < q_month or (month == q_month and day <= q_day):
            return f"{year}{q_month:02d}{q_day:02d}"
    
    return f"{year + 1}0331"

def get_prev_quarter_end():
    """获取上一个最近的季度末日期（用于业绩超预期分析）"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day

    quarter_dates = [
        (3, 31),
        (6, 30),
        (9, 30),
        (12, 31)
    ]
    
    # 获取当前季度的索引
    current_quarter_idx = (month - 1) // 3
    
    # 计算上一个季度的年份和月份
    if current_quarter_idx == 0:  # 如果是第一季度
        prev_year = year - 1
        prev_month, prev_day = quarter_dates[3]  # 返回上一年第四季度
    else:
        prev_year = year
        prev_month, prev_day = quarter_dates[current_quarter_idx - 1]
    
    return f"{prev_year}{prev_month:02d}{prev_day:02d}"

def get_prev_period_date(current_date):
    """获取上一期的日期"""
    year = int(current_date[:4])
    month = int(current_date[4:6])
    
    quarter_dates = [
        (3, 31),
        (6, 30),
        (9, 30),
        (12, 31)
    ]
    
    # 获取当前季度的索引
    current_quarter_idx = (month - 1) // 3
    
    # 计算上一期的年份和月份
    if current_quarter_idx == 0:  # 如果是第一季度
        prev_year = year - 1
        prev_month, prev_day = quarter_dates[3]  # 返回上一年第四季度
    else:
        prev_year = year
        prev_month, prev_day = quarter_dates[current_quarter_idx - 1]
    
    return f"{prev_year}{prev_month:02d}{prev_day:02d}"

def get_target_report_dates(query_date):
    """根据配置获取目标分析日期"""
    if query_date.lower() == 'auto':
        # auto模式：预告日期为下一季度末，超预期分析日期为上一季度末
        prereport_date = get_next_quarter_end()
        exceed_date = get_prev_quarter_end()
    else:
        # 指定日期模式：预告日期为指定日期，超预期分析使用指定日期作为当期
        prereport_date = query_date
        exceed_date = query_date
    
    print_debug(f"目标日期确定:")
    print_debug(f"- 预告业绩分析日期: {prereport_date}")
    print_debug(f"- 超预期分析当期日期: {exceed_date}")
    return prereport_date, exceed_date

def check_data_availability(date):
    """检查指定日期的数据是否可用"""
    print_debug(f"检查 {date} 的数据可用性")
    
    sql = """
    SELECT COUNT(DISTINCT stock_code) FROM stock_prereport WHERE report_date = %s
    """
    
    db_manager.execute(sql, (date,))
    result = db_manager.fetchone()
    count = result[0] if result else 0
    
    print_debug(f"预告数据数量: {count}")
    return count > 0

def get_exceed_area_stocks(current_report_date, query_num, exceed_multiple_percentage):
    """获取业绩超预期的股票"""
    print_debug(f"执行业绩超预期分析:")
    prev_period_date = get_prev_period_date(current_report_date)
    print_debug(f"- 当期业绩期: {current_report_date}")
    print_debug(f"- 上期预告期: {prev_period_date}")
    exceed_multiple = exceed_multiple_percentage  # 直接使用倍数值
    print_debug(f"- 超预期倍数要求: {exceed_multiple}倍")
    print_debug(f"- 返回记录数限制: {query_num}")
    
    # 检查数据可用性
    db_manager.execute("SELECT COUNT(*) FROM stock_report WHERE report_date = %s", (current_report_date,))
    current_report_count = db_manager.fetchone()[0]
    print_debug(f"实际业绩报告数量: {current_report_count}")
    
    db_manager.execute("SELECT COUNT(*) FROM stock_prereport WHERE report_date = %s AND predict_indicator = '净利润'", (prev_period_date,))
    prereport_count = db_manager.fetchone()[0]
    print_debug(f"上期业绩预告数量: {prereport_count}")
    
    if current_report_count == 0 or prereport_count == 0:
        print_debug(f"数据不足，无法进行超预期分析")
        print_debug(f"当期业绩({current_report_date}): {current_report_count}条")
        print_debug(f"上期预告({prev_period_date}): {prereport_count}条")
        return [], current_report_date
    
    # 获取所有当期业绩报告数据
    current_report_sql = """
    WITH RankedReports AS (
        SELECT 
            stock_code,
            stock_name,
            net_profit as actual_profit,
            ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY net_profit DESC) as rn
        FROM stock_report 
        WHERE report_date = %s
    )
    SELECT 
        stock_code,
        stock_name,
        actual_profit
    FROM RankedReports
    WHERE rn = 1
    """
    
    # 获取所有上期预告数据（每个股票取预测值最大的一条记录）
    prereport_sql = """
    WITH RankedPredictions AS (
        SELECT 
            stock_code,
            stock_name,
            predict_value,
            predict_type,
            predict_indicator,
            ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY 
                CASE 
                    WHEN predict_type IN ('预增', '预盈') THEN 1
                    WHEN predict_type = '预平' THEN 2
                    ELSE 3
                END,
                predict_value DESC
            ) as rn
        FROM stock_prereport
        WHERE report_date = %s  -- 使用上期日期
        AND predict_indicator = '净利润'
    )
    SELECT 
        stock_code,
        stock_name,
        predict_value,
        predict_type,
        predict_indicator
    FROM RankedPredictions
    WHERE rn = 1
    """
    
    try:
        # 获取当期业绩数据
        db_manager.execute(current_report_sql, (current_report_date,))
        current_reports = {row[0]: row for row in db_manager.fetchall()}  # 使用股票代码作为key
        
        # 获取预告数据
        db_manager.execute(prereport_sql, (prev_period_date,))
        prereports = {row[0]: row for row in db_manager.fetchall()}  # 使用股票代码作为key
        
        # 比较所有股票并计算超预期倍数
        all_exceed_stocks = []
        for stock_code, report in current_reports.items():
            if stock_code in prereports:
                prereport = prereports[stock_code]
                if prereport[2] > 0:  # 只有当预测值大于0时才进行比较
                    exceed_rate = report[2] / prereport[2]  # actual_profit / predict_value
                    all_exceed_stocks.append((
                        stock_code,            # stock_code
                        report[1],             # stock_name
                        prereport[2],          # prereport_predict
                        report[2],             # actual_profit
                        exceed_rate,           # exceed_rate
                        prereport[3],          # predict_type
                        prereport[4]           # predict_indicator
                    ))
        
        # 按超预期倍数降序排序
        all_exceed_stocks.sort(key=lambda x: x[4], reverse=True)
        
        # 筛选超过指定倍数的记录，并返回前N条
        exceed_stocks = [stock for stock in all_exceed_stocks if stock[4] >= exceed_multiple][:query_num]
        
        print_debug(f"查询返回记录数: {len(exceed_stocks)}")
        return exceed_stocks, current_report_date
        
    except Exception as e:
        print(f"执行SQL出错: {e}")
        return [], None

def get_high_change_stocks(report_date, config):
    """获取业绩变动超过指定倍数的股票"""
    print_debug(f"查询 {report_date} 的高变动股票")
    
    multiple_low = config['multiple']['low'] * 100
    multiple_high = config['multiple']['high'] * 100 if config['multiple']['high'] != -1 else float('inf')
    query_num = config['queryNum']
    
    sql = """
    WITH RankedStocks AS (
        SELECT 
            stock_code, 
            stock_name, 
            predict_indicator, 
            change_rate, 
            predict_value, 
            last_year_value, 
            predict_type,
            change_reason, 
            notice_date,
            ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY ABS(change_rate) DESC) as rn
        FROM stock_prereport 
        WHERE report_date = %s 
        AND ABS(change_rate) >= %s
    )
    SELECT 
        stock_code, 
        stock_name, 
        predict_indicator, 
        change_rate, 
        predict_value, 
        last_year_value,
        predict_type,
        change_reason, 
        notice_date
    FROM RankedStocks 
    WHERE rn = 1
    """
    
    params = [report_date, multiple_low]
    if multiple_high != float('inf'):
        sql += " AND ABS(change_rate) <= %s"
        params.append(multiple_high)
    
    sql += " ORDER BY ABS(change_rate) DESC LIMIT %s"
    params.append(query_num)
    
    db_manager.execute(sql, tuple(params))
    results = db_manager.fetchall()
    print_debug(f"找到 {len(results)} 条结果")
    return results

def format_number(number):
    """格式化数字为万元"""
    if number is None:
        return "0"
    return format(number / 10000, ',.2f')

def generate_html_report(prereport_date, exceed_date, high_change_stocks, exceed_area_stocks):
    """生成HTML报告"""
    template_path = os.path.join(os.path.dirname(__file__), 'performance_analysis.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    formatted_prereport_date = f"{prereport_date[:4]}年{prereport_date[4:6]}月{prereport_date[6:]}日"
    formatted_exceed_date = f"{exceed_date[:4]}年{exceed_date[4:6]}月{exceed_date[6:]}日" if exceed_date else "无可用数据"
    
    # 替换表格标题中的日期
    html_content = html_content.replace(
        '<h2 class="section-title">业绩预告变动</h2>',
        f'<h2 class="section-title">业绩预告变动<span class="date-info">业绩预告分析期: {formatted_prereport_date}</span></h2>'
    )
    
    # 获取上期预告日期
    prev_period_date = get_prev_period_date(exceed_date)
    formatted_prev_date = f"{prev_period_date[:4]}年{prev_period_date[4:6]}月{prev_period_date[6:]}日"
    
    html_content = html_content.replace(
        '<h2 class="section-title">业绩预告超预期股票</h2>',
        f'<h2 class="section-title">业绩超预期<span class="date-info">当期业绩期: {formatted_exceed_date}, 上期预测期: {formatted_prev_date}</span></h2>'
    )
    
    # 移除原有的日期显示区域
    html_content = html_content.replace(
        '<div class="report-dates">\n            <!-- 日期信息将通过Python脚本动态生成 -->\n        </div>',
        ''
    )
    
    high_change_rows = ""
    for stock in high_change_stocks:
        change_class = "positive-change" if stock[3] > 0 else "negative-change"
        high_change_rows += f"""
        <tr>
            <td>{stock[0]}</td>
            <td>{stock[1]}</td>
            <td>{stock[2]}</td>
            <td class="{change_class}">{stock[3]:+.2f}%</td>
            <td>{format_number(stock[4])}</td>
            <td>{format_number(stock[5])}</td>
            <td class="small-text">{stock[6] or ''}</td>
            <td class="change-reason small-text">{stock[7] or ''}</td>
            <td>{stock[8]}</td>
        </tr>
        """
    
    exceed_rows = ""
    for stock in exceed_area_stocks:
        exceed_rate = stock[4]  # 实际值/预测值的倍数
        exceed_rows += f"""
        <tr>
            <td>{stock[0]}</td>
            <td>{stock[1]}</td>
            <td>{format_number(stock[2])}</td>
            <td>{format_number(stock[3])}</td>
            <td class="positive-change">{exceed_rate:.2f}倍</td>
            <td class="small-text">{stock[5] or ''}</td>
            <td>{stock[6]}</td>
        </tr>
        """
    
    html_content = html_content.replace(
        '<!-- 数据将通过Python脚本动态生成 -->', 
        high_change_rows if high_change_stocks else "<tr><td colspan='9'>没有找到符合条件的数据</td></tr>", 
        1
    )
    html_content = html_content.replace(
        '<!-- 数据将通过Python脚本动态生成 -->', 
        exceed_rows if exceed_area_stocks else "<tr><td colspan='7'>没有找到符合条件的数据</td></tr>", 
        1
    )
    
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_analysis_{current_time}.html"
    output_path = os.path.join(os.path.dirname(__file__), 'htmls', filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

def main():
    try:
        config = load_config()
        print_debug(f"加载配置: {config}")
        
        if not db_manager.connect():
            print("数据库连接失败")
            return
        
        prereport_date, exceed_date = get_target_report_dates(config['queryDate'])
        if not prereport_date or not exceed_date:
            print("无法确定目标报告期")
            return
            
        print(f"\n=== 分析日期确定 ===")
        print(f"当前日期: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"配置日期: {config['queryDate']}")
        print(f"预报业绩分析期: {prereport_date}")
        print(f"超预期分析期: {exceed_date}")
        
        if not check_data_availability(prereport_date):
            print(f"未找到 {prereport_date} 的预告数据")
            return
            
        high_change_stocks = get_high_change_stocks(prereport_date, config)
        exceed_area_stocks, _ = get_exceed_area_stocks(exceed_date, config['queryNum'], config['exceedMultiple'])
            
        print(f"\n=== 数据分析报告 ===")
        print(f"业绩预告分析期: {prereport_date}")
        print(f"超预期分析期: {exceed_date if exceed_date else '无可用数据'}")
        
        output_path = generate_html_report(prereport_date, exceed_date, high_change_stocks, exceed_area_stocks)
        print(f"\n报告生成完成！")
        print(f"报告保存路径: {output_path}")
        
    except Exception as e:
        print(f"生成报告时发生错误: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
