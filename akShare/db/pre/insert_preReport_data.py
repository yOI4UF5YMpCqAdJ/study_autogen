import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
from ..db_manager import db_manager

def insert_preReport_data(stock_yjyg_em_df=None, batch_no=None):
    """
    将数据插入到stock_preReport表中
    
    参数:
        stock_yjyg_em_df: pandas.DataFrame, 包含股票业绩预告数据的DataFrame
        batch_no: str, 批次号，用于关联头表
    
    返回:
        bool: 表示操作是否成功
        int: 插入的记录数量
    """
    try:
        # 如果未提供数据，则尝试获取
        if stock_yjyg_em_df is None:
            # 调用akshare函数获取数据
            print("错误：未提供数据")
            return False, 0
        
        # 检查是否有数据返回
        if stock_yjyg_em_df.empty:
            print("没有获取到数据，请检查日期参数或稍后再试")
            return False, 0
        
        print(f"准备插入{len(stock_yjyg_em_df)}条业绩预告数据")
        
        # 连接到数据库
        if not db_manager.connect():
            print("数据库连接失败")
            return False, 0
        
        # 准备批量插入数据
        insert_count = 0
        
        # 验证批次号是否存在
        if batch_no is None:
            print("错误：未提供批次号")
            return False, 0
        
        # 检查头表中是否存在该批次号
        check_sql = "SELECT 1 FROM stock_prereport_header WHERE batch_no = %s"
        db_manager.execute(check_sql, (batch_no,))
        if not db_manager.fetchone():
            print(f"错误：批次号 {batch_no} 在头表中不存在")
            return False, 0
            
        for _, row in stock_yjyg_em_df.iterrows():
            # 准备插入的数据
            insert_data = {
                'batch_no': batch_no,  # 添加批次号字段
                'seq_no': row.get('序号', 0),
                'stock_code': row.get('股票代码', ''),
                'stock_name': row.get('股票简称', ''),
                'predict_indicator': row.get('预测指标', ''),
                'performance_change': row.get('业绩变动', ''),
                'predict_value': row.get('预测数值', 0),
                'change_rate': row.get('业绩变动幅度', 0),
                'change_reason': row.get('业绩变动原因', ''),
                'predict_type': row.get('预告类型', ''),
                'last_year_value': row.get('上年同期值', 0),
                'notice_date': row.get('公告日期', None)
            }
            
            # 处理数值字段中的NaN值
            for key, value in insert_data.items():
                # 检查是否为NaN值（对于数值类型字段）
                if isinstance(value, (int, float)) and (pd.isna(value) or np.isnan(value)):
                    insert_data[key] = None  # 将NaN替换为None，MySQL会将其转换为NULL
            
            # 处理日期字段
            if isinstance(insert_data['notice_date'], str):
                try:
                    insert_data['notice_date'] = datetime.strptime(insert_data['notice_date'], '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    try:
                        insert_data['notice_date'] = datetime.strptime(insert_data['notice_date'], '%Y-%m-%d').date()
                    except ValueError:
                        insert_data['notice_date'] = None
            
            # 构建插入SQL语句
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['%s'] * len(insert_data))
            insert_sql = f"INSERT INTO stock_preReport ({columns}) VALUES ({placeholders})"
            
            # 执行插入操作
            db_manager.execute(insert_sql, list(insert_data.values()))
            insert_count += 1
        
        # 提交事务
        db_manager.commit()
        print(f"成功插入{insert_count}条数据到stock_preReport表")
        
        return True, insert_count
        
    except Exception as e:
        print(f"插入数据时发生错误: {e}")
        return False, 0

if __name__ == "__main__":
    insert_preReport_data()
