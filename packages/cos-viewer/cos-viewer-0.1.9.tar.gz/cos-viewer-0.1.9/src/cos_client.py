from qcloud_cos import CosConfig, CosS3Client
import time
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from src.config_manager import ConfigManager
import os
from pathlib import Path


class COSClient:
    def __init__(self, config_name):
        self.config_manager = ConfigManager()
        config = self.config_manager.get_config(config_name)
        if not config:
            raise ValueError("配置不存在")

        self.client = CosS3Client(
            CosConfig(
                Region=config['cos_region'],
                SecretId=config['cos_secret_id'],
                SecretKey=config['cos_secret_key']
            )
        )
        self.bucket = config['cos_bucket']
        self.prefix = config['prefix']
        self.region = config['cos_region']

    def list_objects(self):
        try:
            response = self.client.list_objects(
                Bucket=self.bucket,
                Prefix=self.prefix,
                MaxKeys=1000
            )
            contents = response.get('Contents', [])
            return [{
                'Key': content['Key'],
                'Size': content['Size'],
                'LastModified': content['LastModified'],
                'ETag': content['ETag']
            } for content in response.get('Contents', [])]
        except (CosClientError, CosServiceError) as e:
            raise RuntimeError(f"COS操作失败: {e}")
        
    def get_object(self, key):
        try:
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
            # 获取对象标签
            tags_response = self.client.get_object_tagging(
                Bucket=self.bucket,
                Key=key
            )

            tag_set = tags_response.get('TagSet', [])
            if tag_set:
                tags = {tag['Key']: tag['Value'] for tag in tag_set['Tag']}
            else:
                tags = {}

            return {
                'Key': key,
                'Location': f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{key}",
                'Tags': tags,
                'Metadata': response,
            }
        except (CosClientError, CosServiceError) as e:
            raise RuntimeError(f"获取对象详情失败: {e}")

    def delete_object(self, key):
        try:
            # 如果是目录，需要先删除目录下的所有文件
            if key.endswith('/'):
                # 列出目录下的所有文件
                response = self.client.list_objects(
                    Bucket=self.bucket,
                    Prefix=key,
                    MaxKeys=1000
                )
                for obj in response.get('Contents', []):
                    self.client.delete_object(
                        Bucket=self.bucket,
                        Key=obj['Key']
                    )
            # 删除对象本身
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except (CosClientError, CosServiceError) as e:
            raise RuntimeError(f"删除失败: {e}")

    def upload_file(self, file_path: str, cos_key: str, progress_callback=None):
        try:
            # 获取文件大小
            total_size = os.path.getsize(file_path)
            
            # 定义进度回调函数
            def upload_progress_callback(consumed_bytes, total_bytes):
                if progress_callback:
                    progress_callback(total=total_bytes, value=consumed_bytes)
            
            self.client.upload_file(
                Bucket=self.bucket,
                LocalFilePath=file_path,
                Key=f"{self.prefix}/{cos_key}",
                MAXThread=10,
                progress_callback=upload_progress_callback
            )
            return True
        except (CosClientError, CosServiceError) as e:
            raise RuntimeError(f"上传失败: {e}")

    def download_directory(self, prefix, download_path, progress_callback=None):
        try:
            # 确保下载路径存在
            Path(download_path).mkdir(parents=True, exist_ok=True)

            # 列出目录下的所有文件
            response = self.client.list_objects(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=1000
            )

            for obj in response.get('Contents', []):
                key = obj['Key']
                if key.endswith('/'):
                    continue  # 跳过目录本身

                # 构造本地文件路径
                relative_path = key[len(prefix):].lstrip('/')
                local_path = Path(download_path) / relative_path

                # 确保本地目录结构存在
                local_path.parent.mkdir(parents=True, exist_ok=True)

                # 下载单个文件
                self.download_object(key, str(local_path.parent), progress_callback)

        except (CosClientError, CosServiceError) as e:
            raise RuntimeError(f"下载目录失败: {e}")

    def download_object(self, key, download_path, progress_callback=None):
        try:
            # 获取文件总大小
            head_response = self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
            total_size = int(head_response['Content-Length'])

            # 分块下载
            downloaded = 0
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key,
            )
            stream = response['Body']

            local_path = Path(download_path) / os.path.basename(key)
            with open(local_path, 'wb') as f:
                while True:
                    chunk = stream.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 计算进度
                    if progress_callback:
                        progress_callback(total=total_size, value=downloaded)

            return local_path
        except (CosClientError, CosServiceError) as e:
            raise RuntimeError(f"下载失败: {e}")
