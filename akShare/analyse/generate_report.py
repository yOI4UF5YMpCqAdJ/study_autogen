import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import akshare as ak
from typing import Dict, Any, List, Tuple

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from akShare.analyse import createHtml
from akShare.db.db_manager import db_manager
from akShare.analyse.date_utils import get_quarter_dates, get_next_quarter_end, get_prev_quarter_end

def load_config():
    """加载.env配置文件"""
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    return {
        'queryNum': int(os.getenv('QUERY_NUM', 5)),
        'multiple': {
            'low': float(os.getenv('MULTIPLE_LOW', 2)),
            'high': float(os.getenv('MULTIPLE_HIGH', -1))
        },
        'exceedMultiple': {
            'low': float(os.getenv('EXCEED_MULTIPLE_LOW', 2)),
            'high': float(os.getenv('EXCEED_MULTIPLE_HIGH', 5))
        },
        'queryDate': os.getenv('QUERY_DATE', 'auto')
    }

def print_debug(msg):
    """打印调试信息"""
    print(f"DEBUG: {msg}")

def get_prev_period_date(current_date):
    """获取上一期的日期"""
    year = int(current_date[:4])
    month = int(current_date[4:6])
    
    quarter_dates = get_quarter_dates()
    
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
        # 指定日期模式：预告日期为指定日期，超预期分析日期为指定日期所在期间的上一期
        prereport_date = query_date
        exceed_date = get_prev_period_date(query_date)
    
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

def get_exceed_area_stocks(current_report_date, query_num, exceed_multiple_config):
    """获取业绩超预期的股票"""
    print_debug(f"执行业绩超预期分析:")
    prev_period_date = get_prev_period_date(current_report_date)
    print_debug(f"- 当期业绩期: {current_report_date}")
    print_debug(f"- 上期预告期: {prev_period_date}")
    exceed_multiple_low = exceed_multiple_config['low']
    exceed_multiple_high = exceed_multiple_config['high']
    print_debug(f"- 超预期倍数范围: {exceed_multiple_low}~{exceed_multiple_high}倍")
    print_debug(f"- 返回记录数限制: {query_num}")
    
    # # 检查数据可用性
    # db_manager.execute("SELECT COUNT(*) FROM stock_report WHERE report_date = %s", (current_report_date,))
    # current_report_count = db_manager.fetchone()[0]
    # print_debug(f"实际业绩报告数量: {current_report_count}")
    
    # db_manager.execute("SELECT COUNT(*) FROM stock_prereport WHERE report_date = %s", (prev_period_date,))
    # prereport_count = db_manager.fetchone()[0]
    # print_debug(f"上期业绩预告数量: {prereport_count}")
    
    # if current_report_count == 0 or prereport_count == 0:
    #     print_debug(f"数据不足，无法进行超预期分析")
    #     print_debug(f"当期业绩({current_report_date}): {current_report_count}条")
    #     print_debug(f"上期预告({prev_period_date}): {prereport_count}条")
    #     return [], current_report_date
    
    # 获取当期业绩报告数据，每个股票取净利润最高的一条记录
    current_report_sql = """
    WITH StockProfit AS (
        SELECT 
            stock_code,
            stock_name,
            net_profit as actual_profit,
            ROW_NUMBER() OVER(PARTITION BY stock_code ORDER BY net_profit DESC) as rn
        FROM stock_report 
        WHERE report_date = %s
    )
    SELECT 
        stock_code,
        stock_name,
        actual_profit
    FROM StockProfit
    WHERE rn = 1
    """
    
    # 获取上期预告数据，每个股票取预测值最高的一条记录
    prereport_sql = """
    WITH StockPredict AS (
        SELECT 
            stock_code,
            stock_name,
            predict_value,
            predict_type,
            predict_indicator,
            ROW_NUMBER() OVER(PARTITION BY stock_code ORDER BY predict_value DESC) as rn
        FROM stock_prereport
        WHERE report_date = %s
    )
    SELECT 
        stock_code,
        stock_name,
        predict_value,
        predict_type,
        predict_indicator
    FROM StockPredict
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
        
        # 筛选在指定倍数范围内的记录，并返回前N条
        exceed_stocks = [stock for stock in all_exceed_stocks if exceed_multiple_low <= stock[4] <= exceed_multiple_high][:query_num]
        
        print_debug(f"查询返回记录数: {len(exceed_stocks)}")
        return exceed_stocks, current_report_date
        
    except Exception as e:
        print(f"执行SQL出错: {e}")
        return [], None

def get_high_change_stocks(report_date, config):
    """获取业绩变动超过指定倍数的股票"""
    print_debug(f"查询 {report_date} 的高变动股票")
    
    multiple_low = int(config['multiple']['low'] * 100)
    multiple_high = int(config['multiple']['high'] * 100) if config['multiple']['high'] != -1 else float('inf')
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
            ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY change_rate DESC) as rn
        FROM stock_prereport 
        WHERE report_date = %s 
        AND change_rate >= %s
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
        sql += " AND change_rate <= %s"
        params.append(multiple_high)
    
    sql += " ORDER BY change_rate DESC LIMIT %s"
    params.append(query_num)
    
    final_sql = db_manager.cursor.mogrify(sql, tuple(params))
    # print_debug(f"执行SQL:\n{final_sql}")
    
    db_manager.execute(sql, tuple(params))
    results = db_manager.fetchall()
    print_debug(f"找到 {len(results)} 条结果")
    return results

def get_stock_fund_flow(stock_code):
    """获取单个股票的资金流数据"""
    try:
        # 根据股票代码判断市场
        market = ''
        if stock_code.startswith('300'):
            market = 'bj'
        elif stock_code.startswith('6'):
            market = 'sh'
        elif stock_code.startswith(('001', '002', '003', '004')):
            market = 'sz'
        else:
            return None
            
        # 获取资金流数据
        df = ak.stock_individual_fund_flow(stock=stock_code, market=market)
        print(f"===== 股票 {stock_code} 资金流数据 =====")
        print("列名:", df.columns.tolist())
        print("数据形状:", df.shape)
        if not df.empty:
            print("前5条数据:")
            print(df.sort_values(by='日期', ascending=False).head(5))
        else:
            print("警告: 未获取到数据")
        # 按日期倒序排序并取前5条记录
        return df.sort_values(by='日期', ascending=False).head(5)
    except Exception as e:
        print(f"获取股票 {stock_code} 资金流数据失败: {e}")
        return None

def add_fund_flow_data(stocks: List[Tuple]) -> List[Dict[str, Any]]:
    """为股票数据添加资金流信息"""
    enhanced_stocks = []
    for stock in stocks:
        stock_dict = {
            str(i): value for i, value in enumerate(stock)  # 将元组转换为字典以便添加额外数据
        }
        stock_dict['fund_flow'] = get_stock_fund_flow(stock[0])
        enhanced_stocks.append(stock_dict)
    return enhanced_stocks

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
        
        # if not check_data_availability(prereport_date):
        #     print(f"未找到 {prereport_date} 的预告数据")
        #     return
            
        # 预报业绩变动
        high_change_stocks = get_high_change_stocks(prereport_date, config)
        high_change_stocks_with_fund = add_fund_flow_data(high_change_stocks)
        
        # 实际业绩报告
        exceed_area_stocks, _ = get_exceed_area_stocks(exceed_date, config['queryNum'], config['exceedMultiple'])
        exceed_area_stocks_with_fund = add_fund_flow_data(exceed_area_stocks)
            
        print(f"\n=== 数据分析报告 ===")
        print(f"业绩预告分析期: {prereport_date}")
        print(f"超预期分析期: {exceed_date if exceed_date else '无可用数据'}")
        
        prev_period_date = get_prev_period_date(exceed_date)
        # 使用新的HTML生成模块
        output_path = createHtml.generate_html_report(
            prereport_date=prereport_date,
            exceed_date=exceed_date,
            prev_period_date=prev_period_date,
            high_change_stocks=high_change_stocks_with_fund,
            exceed_area_stocks=exceed_area_stocks_with_fund
        )
        
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
