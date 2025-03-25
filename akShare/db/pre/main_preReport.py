import akshare as ak
import sys
import os
from datetime import datetime
# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from db.db_manager import db_manager
from db_preReport import (update_header_status, check_existing_query, 
                         delete_preReport_detail_by_date, insert_preReport_data)

def check_tables(date="20250331"):
    """
    检查头表和数据表是否存在
    
    参数:
        date: str, 查询参数日期，格式为YYYYMMDD，默认为20250331
    
    返回:
        tuple: (header_table_exists, detail_table_exists)
            header_table_exists: bool, 头表是否存在
            detail_table_exists: bool, 数据表是否存在
    """
    try:
        # 连接到数据库
        if not db_manager.connect():
            print("数据库连接失败")
            return False, False
            
        # 检查表是否存在
        print("\n检查表是否存在...")
        db_manager.execute("SHOW TABLES LIKE 'stock_prereport_header'")
        header_table_exists = db_manager.fetchone() is not None
        
        db_manager.execute("SHOW TABLES LIKE 'stock_preReport'")
        detail_table_exists = db_manager.fetchone() is not None
        
        print(f"头表存在: {header_table_exists}, 数据表存在: {detail_table_exists}")
        
        if not header_table_exists or not detail_table_exists:
            print("错误：必要的表不存在，请先创建相关表")
            return False, False
            
        return header_table_exists, detail_table_exists
        
    except Exception as e:
        print(f"检查表时发生错误: {e}")
        return False, False

def process_preReport_data(date="20250331"):
    """
    主函数：调用ak.stock_yjyg_em函数，当返回有数据时：
    1. 检查表是否存在
    2. 将数据插入到表中
    3. 更新头表状态
    
    参数:
        date: str, 业绩预告日期，格式为"YYYYMMDD"
        
    返回:
        bool: 表示操作是否成功
    """
    try:
        print("开始处理股票业绩预告数据...")
        
        # 调用akshare函数获取数据
        stock_yjyg_em_df = ak.stock_yjyg_em(date=date)
        
        # 检查是否有数据返回
        if stock_yjyg_em_df.empty:
            print("没有获取到数据，请检查日期参数或稍后再试")
            return False
        
        print(f"成功获取到{len(stock_yjyg_em_df)}条业绩预告数据")
        
        # 检查是否存在相同查询参数的记录
        has_existing_query = check_existing_query(date)
        
        if has_existing_query:
            print("\n发现相同日期参数的记录，将删除对应的子表数据")
            if not delete_preReport_detail_by_date(date):
                print("删除子表数据失败，终止数据处理")
                return False
        
        # 步骤1: 检查必要的表是否存在
        print("\n步骤1: 检查必要的表")
        header_exists, detail_exists = check_tables(date)
        
        if not header_exists or not detail_exists:
            print("必要的表不存在，终止数据处理")
            return False
            
        print("\n步骤2: 插入数据")
        # 连接数据库并检查头表记录
        if not db_manager.connect():
            print("数据库连接失败")
            return False
            
        # 检查头表是否已存在该日期的记录
        check_sql = """
        SELECT 1 FROM stock_prereport_header 
        WHERE report_date = %s
        """
        db_manager.execute(check_sql, (date,))
        exists = db_manager.fetchone()
        
        # 如果记录不存在，则插入
        if not exists:
            db_manager.execute("""
                INSERT INTO stock_prereport_header 
                (report_date, query_param, status) 
                VALUES (%s, %s, %s)
            """, (date, f"date={date}", "PENDING"))
            db_manager.commit()
        else:
            # 如果记录存在，更新状态为PENDING
            db_manager.execute("""
                UPDATE stock_prereport_header 
                SET status = 'PENDING'
                WHERE report_date = %s
            """, (date,))
            db_manager.commit()
        
        # 插入预告数据
        success, insert_count = insert_preReport_data(stock_yjyg_em_df, date)
        if not success:
            print("插入数据失败，终止数据处理")
            # 更新头表状态为失败
            update_header_status(date, 0, "FAILED", "插入数据失败")
            return False
            
        # 更新头表状态
        print("\n步骤3: 更新头表状态")
        status_updated = update_header_status(date, insert_count, "COMPLETED", "处理成功")
        if not status_updated:
            print("警告: 更新头表状态失败，但数据处理已完成")
        
        # 展示表结构
        print("\n表 stock_preReport 的结构：")
        db_manager.connect()
        db_manager.execute("DESCRIBE stock_preReport")
        for field in db_manager.fetchall():
            print(field)
        
        db_manager.close()
        
        print("\n数据处理完成！")
        return True
        
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
        db_manager.close()
        return False

if __name__ == "__main__":
    process_preReport_data(date="20200930")
# 20200630
