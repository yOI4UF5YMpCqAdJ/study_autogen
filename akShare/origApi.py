import akshare as ak

#业绩预告
def getPreData():

    stock_yjyg_em_df = ak.stock_yjyg_em(date="20250331")
    print(stock_yjyg_em_df)

#业绩
def getReport():
    stock_yjbb_em_df = ak.stock_yjbb_em(date="20220331")
    print(stock_yjbb_em_df)

if __name__ == "__main__":
    process_preReport_data(force_recreate=True)