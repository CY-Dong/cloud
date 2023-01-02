#%%
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from flask import Flask, request, jsonify

# 在這裡填入 Azure Blob 存儲的相關設定（如帳戶名稱、密鑰、容器名稱等）
storage_account_name = "11177016qrcode"
storage_account_key = "cRF8iZARPDakrmZDmdkIyY6yZwU2yll+kFRmwv75lZDDlSZAblm66nlsoraKiIVpTY2wHIDorgY1+AStAIa+Sw=="
container_name = "qrcode"
blob_name = "qrcode.jpg"

blob_service_client = BlobServiceClient(account_url="https://{}.blob.core.windows.net".format(storage_account_name),
    credential=storage_account_key,)
container_client = ContainerClient(account_url="https://{}.blob.core.windows.net".format(storage_account_name), container_name=container_name, credential=storage_account_key)
#container_client = ContainerClient(account_url="<account_url>", container_name=container_name, credential="<credential>")

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_image():
  # 讀取表單中上傳的圖片並上傳到 Azure Blob 存儲
  image = request.files["image"]
  blob_client = BlobClient(account_url="https://{}.blob.core.windows.net".format(storage_account_name), container_name=container_name, blob_name=image.filename, credential=storage_account_key)
  blob_client.upload_blob(image)

  # 將圖片的相關資訊（如圖片名稱、URL 等）存入資料庫
  # 這裡省略了資料庫的相關操作

  # 回傳圖片的相關資訊
  data = {
    "name": image.filename,
    "url": blob_client.url
  }
  return jsonify(data)

# %%
if __name__ == '__main__':
    app.run()
# %%
