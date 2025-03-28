import sys
import os
from datetime import datetime
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.db_manager import db_manager
from generate_report import get_target_report_dates, get_prev_period_date

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

def test_exceed_analysis(stock_code='300274', stock_name='阳光电源'):
    """测试特定股票的业绩超预期分析"""
    # 加载配置
    config = load_config()
    print(f"\n开始分析 {stock_name}({stock_code}) 的业绩超预期情况...")
    
    # 从配置获取目标日期
    prereport_date, exceed_date = get_target_report_dates(config['queryDate'])
    print(f"\n配置信息:")
    print(f"查询日期设置: {config['queryDate']}")
    print(f"当期业绩期: {exceed_date}")
    
    # 获取上期预告期
    prev_date = get_prev_period_date(exceed_date)
    print(f"上期预告期: {prev_date}")
    
    # 查看数据可用性
    print("\n检查数据可用性:")
    print("1. 查询业绩报告可用日期...")
    report_sql = """
    SELECT DISTINCT report_date 
    FROM stock_report 
    WHERE stock_code = %s 
    AND report_date BETWEEN '20200101' AND '20201231'
    ORDER BY report_date
    """
    
    db_manager.execute(report_sql, (stock_code,))
    report_dates = [row[0] for row in db_manager.fetchall()]
    print(f"业绩报告可用日期: {report_dates}")
    
    print("\n2. 查询业绩预告可用日期...")
    prereport_sql = """
    SELECT DISTINCT report_date 
    FROM stock_prereport 
    WHERE stock_code = %s 
    AND report_date BETWEEN '20200101' AND '20201231'
    ORDER BY report_date
    """
    
    db_manager.execute(prereport_sql, (stock_code,))
    prereport_dates = [row[0] for row in db_manager.fetchall()]
    print(f"业绩预告可用日期: {prereport_dates}")
    
    # 获取当期业绩数据
    current_sql = """
    SELECT 
        stock_code,
        stock_name,
        net_profit as actual_profit
    FROM stock_report 
    WHERE report_date = %s
    AND stock_code = %s
    """
    
    # 获取上期预告数据（调试：显示所有预告数据）
    prev_sql = """
    SELECT 
        stock_code,
        stock_name,
        predict_value,
        predict_type,
        predict_indicator
    FROM stock_prereport
    WHERE report_date = %s
    AND stock_code = %s
    """
    
    try:
        if not db_manager.connect():
            print("数据库连接失败")
            return
            
        # 查询当期业绩
        db_manager.execute(current_sql, (exceed_date, stock_code))
        current_report = db_manager.fetchone()
        
        # 查询上期预告
        db_manager.execute(prev_sql, (prev_date, stock_code))
        prev_report = db_manager.fetchone()
        
        if current_report and prev_report:
            print(f"\n业绩数据:")
            print(f"当期实际净利润: {current_report[2]:,.2f}")
            print("\n预告数据:")
            if prev_report:
                for i, field in enumerate(prev_report):
                    print(f"字段{i}: {field}")
            else:
                print("无预告数据")
        else:
            print(f"\n数据缺失:")
            if not current_report:
                print(f"- 未找到{exceed_date}的业绩报告数据")
            if not prev_report:
                print(f"- 未找到{prev_date}的业绩预告数据")
    
    except Exception as e:
        print(f"查询出错: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    test_exceed_analysis()
