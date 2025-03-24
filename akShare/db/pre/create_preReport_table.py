import akshare as ak
import pandas as pd
from ..db_manager import db_manager

def create_stock_preReport_table(stock_yjyg_em_df=None, batch_no=None, force_recreate=True):
    """
    根据返回数据创建MySQL表
    表名：stock_preReport
    
    参数:
        stock_yjyg_em_df: pandas.DataFrame, 包含股票业绩预告数据的DataFrame
        batch_no: str, 批次号，用于关联头表
        force_recreate: bool, 是否强制重新创建表，默认为True
    
    返回:
        bool: 表示操作是否成功
    """
    try:
        # 如果未提供数据，则尝试获取
        if stock_yjyg_em_df is None:
            # 调用akshare函数获取数据
            print("错误：未提供数据")
            return False
        
        # 检查是否有数据返回
        if stock_yjyg_em_df.empty:
            print("没有获取到数据，请检查日期参数或稍后再试")
            return False
        
        # 连接到数据库
        if not db_manager.connect():
            print("数据库连接失败")
            return False
        
        # 删除表（如果已存在且需要重新创建）
        if force_recreate:
            print("删除旧表（如果存在）...")
            db_manager.execute("DROP TABLE IF EXISTS stock_preReport")
        else:
            # 检查表是否存在
            db_manager.execute("SHOW TABLES LIKE 'stock_preReport'")
            table_exists = db_manager.fetchone()
            if table_exists:
                print("表 stock_preReport 已存在，不再重新创建")
                return True
        
        print("创建新表 stock_preReport...")
        
        # 创建表SQL语句
        create_table_sql = """
        CREATE TABLE stock_preReport (
            id INT AUTO_INCREMENT PRIMARY KEY,
            batch_no VARCHAR(20) NOT NULL COMMENT '批次号',
            seq_no INT COMMENT '序号',
            stock_code VARCHAR(10) COMMENT '股票代码',
            stock_name VARCHAR(50) COMMENT '股票简称',
            predict_indicator VARCHAR(50) COMMENT '预测指标',
            performance_change TEXT COMMENT '业绩变动',
            predict_value DECIMAL(20,2) COMMENT '预测数值',
            change_rate DECIMAL(10,2) COMMENT '业绩变动幅度',
            change_reason TEXT COMMENT '业绩变动原因',
            predict_type VARCHAR(20) COMMENT '预告类型',
            last_year_value DECIMAL(20,2) COMMENT '上年同期值',
            notice_date DATE COMMENT '公告日期',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_batch_no (batch_no),
            CONSTRAINT fk_batch_no FOREIGN KEY (batch_no) REFERENCES stock_prereport_header(batch_no) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票业绩预告';
        """
        
        db_manager.execute(create_table_sql)
        
        print("表创建成功！表结构如下：")
        db_manager.execute("DESCRIBE stock_preReport")
        for field in db_manager.fetchall():
            print(field)
        
        db_manager.commit()
        
        print("\n表 stock_preReport 已成功创建！")
        return True
        
    except Exception as e:
        print(f"表创建过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    create_stock_preReport_table()
