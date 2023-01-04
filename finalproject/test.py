#%%
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import os

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

#%% 連接儲存體內的容器


storage_account_name = "11177016qrcode"
storage_account_key = "cRF8iZARPDakrmZDmdkIyY6yZwU2yll+kFRmwv75lZDDlSZAblm66nlsoraKiIVpTY2wHIDorgY1+AStAIa+Sw=="

service = BlobServiceClient(
    account_url="https://{}.blob.core.windows.net".format(storage_account_name),
    credential=storage_account_key,
)

container_name = "qrcode"
container_client = service.get_container_client(container_name)

blob_name = "qrcode.jpg"
blob_client = container_client.get_blob_client(blob_name)

# 讀取 blob 中的數據
blob_data = blob_client.download_blob().readall()

#%% 將檔案載下來
path = 'F:/clould/finalproject/data/' + blob_name
with open( path, "wb") as download_file:
    download_file.write( blob_data )



#%%

# 读取图像
image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

# 查找QR码
codes = pyzbar.decode(image)


# 遍历找到的所有QR码
for code in codes:
    # 打印QR码数据
    
    if ( code.type == 'QRCODE' ) :
      if ( code.data[0:2] == b'**' ) :
          right_code = code.data
      else :
          
          left_code = code.data


left_code = left_code.decode( 'utf-8' )
print( left_code )
number = left_code[0:10]                    #發票號碼
date = left_code[10:17]                     #開發票日期
random_code = left_code[17:21]              #隨機碼
sales = left_code[21:29]                    #銷售額
total = left_code[29:37]                    #總計額
buyer_compilation = left_code[37:45]        #買方統編
seller_compilation = left_code[45:53]       #賣方統編
encryption = left_code[53:77]               #加密資訊
product = left_code[95:len(left_code)]      #產品資訊


#%% 

from azure.cosmos import CosmosClient, PartitionKey

# 3. 創建 CosmosClient 對象
cosmos_account_name = "https://11177016cosmosdb.documents.azure.com:443/"
cosmos_account_key = "oIypK85ivjY3tdxaNlZ5QLpq6IQbop3qGsCYWHZ33KaIW7K0IKsxAvaAN6JOiG47i9WkRWLdKV2tACDb9EUwPQ=="

client = CosmosClient(cosmos_account_name, cosmos_account_key)

#%% 上傳資料至指定的database內的容器

# 4. 選擇數據庫和容器
database_name = "qrcodeTest"
database_client = client.get_database_client(database_name)

container_name = "qrcode"
container = database_client.get_container_client(container_name)

# 5. 創建文檔
document = {
    "id": number,
    "date" : date,
    "product" : product
}    

container.create_item(document)


#%%
# 6. 查詢文檔
try:
    results = container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True)
    for result in results:
        print(result)
except Exception as e:
    print("Error: {}".format(e))

# %%