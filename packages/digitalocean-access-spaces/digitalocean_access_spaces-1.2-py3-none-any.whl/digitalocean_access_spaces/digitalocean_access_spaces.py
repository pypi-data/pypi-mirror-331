import os
import boto3
import botocore

class digitalocean_spaces :

    session = None
    client  = None
    SPACES_BUCKET_NAME = None

    def __init__(self):
        # 環境変数を取得
        SPACES_ACCESS_KEY  = os.getenv('SPACES_ACCESS_KEY')
        SPACES_SECRET_KEY  = os.getenv('SPACES_SECRET_KEY')
        SPACES_REGION      = os.getenv('SPACES_REGION')
        SPACES_BUCKET_NAME = os.getenv('SPACES_BUCKET_NAME')

        # Boto3セッションの作成
        self.session = boto3.session.Session()
        self.client = self.session.client(
            's3',
            endpoint_url            = f'https://{SPACES_REGION}.digitaloceanspaces.com',
            config                  = botocore.config.Config(s3={'addressing_style': 'virtual'}),
            region_name             = SPACES_REGION,
            aws_access_key_id       = SPACES_ACCESS_KEY,
            aws_secret_access_key   = SPACES_SECRET_KEY
        )
        self.SPACES_BUCKET_NAME = SPACES_BUCKET_NAME
    
    def sendfile_to_spaces(self, targetfile_path: str, targetfld_to: str):
        """
        指定されたファイルをDigitalOcean Spacesにアップロードする関数です。

        Args:
            targetfile_path (str): アップロードするファイルのパス。このファイルがSpacesにアップロードされます。
            targetfld_to (str): アップロード先のSpaces内のフォルダパス。このパスにファイルが保存されます。
                                ルートフォルダに保存する場合は、空白にしてください。（"."ではなく）
        """
        # ファイルのサイズを取得
        file_size = os.path.getsize(targetfile_path)

        # ファイルをS3バケットにアップロード
        targetfile_to = os.path.join(targetfld_to, os.path.basename(targetfile_path))
        targetfile_to = targetfile_to.replace('\\', '/')
        with open(targetfile_path, 'rb') as data:
            self.client.put_object(
                Bucket   = self.SPACES_BUCKET_NAME,
                Key      = targetfile_to,
                Body     = data,
                ACL      = 'private',
                Metadata = {'x-amz-meta-my-key': 'your-value'},
                ContentLength = file_size  # Content-Lengthを追加
            )

    def send_to_spaces(self, target, rootfld:str=""):
        """
        指定されたファイルまたはフォルダをDigitalOcean Spacesにアップロードする関数です。

        Args:
            target (str): アップロードするファイルまたはフォルダのパス。
        """
        if os.path.isdir(target):
            # フォルダの場合、再帰的にすべてのファイルを表示
            for root, dirs, files in os.walk(target):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.sendfile_to_spaces(file_path, f'{rootfld}/{root}')
                    print(f"DigitalOcean Spaces-Upload: {file_path}")
        elif os.path.isfile(target):
            parent_folder = os.path.dirname(target)
            spacefld = os.path.join(rootfld, parent_folder)
            self.sendfile_to_spaces(target, spacefld)
            print(f"DigitalOcean Spaces-Upload: {target}")
        else:

            print(f"'{target}' という名前のファイルまたはフォルダは存在しません。")


    def __download_file(self, targetfile_fullpath:str, targetfld_to:str):
        file_from = targetfile_fullpath.replace('\\', '/')
        fn = os.path.basename(targetfile_fullpath)
        file_to   = os.path.join(targetfld_to, fn)
        self.client.download_file(self.SPACES_BUCKET_NAME, file_from, file_to)

    def download_from_spaces(self, targetfile_fullpath:str, targetfld_to:str):
        """
        DigitalOcean Spacesから指定されたファイルをダウンロードする関数です。

        Args:
            targetfile_fullpath (str): ダウンロードするファイルのSpaces内での完全なパス。もしフォルダを指定していたら、そのフォルダ下のファイル/フォルダをまるっとDL
            targetfld_to (str): ダウンロードしたファイルを保存するローカルフォルダ名。
                                このパスにファイルが保存されます。
        """

        contents = self.list_files_and_folders(targetfile_fullpath)
        if len(contents['file']) == 0 and len(contents['folder']) == 0 :
            #`targetfile_fullpath`がファイルだったケース
            self.__download_file(targetfile_fullpath, targetfld_to)
        else :
            #`targetfile_fullpath`がフォルダだったケース
            target_folder_to   = os.path.join(targetfld_to, targetfile_fullpath)
            target_folder_to   = target_folder_to.replace('\\', '/')
            target_folder_from = targetfile_fullpath
            if not os.path.exists(target_folder_to) :
                os.makedirs(target_folder_to)

            for fld_key in contents['folder']:
                fld_from = os.path.join(target_folder_from, fld_key)
                self.download_from_spaces(fld_from, targetfld_to)

            #そのフォルダにあるファイルをDL
            for file_key in contents['file']:
                file_path = os.path.join(target_folder_from, file_key)
                self.__download_file(file_path, target_folder_to)


    def download_from_spaces2(self, targetfile_fullpath:str, targetfld_to:str):
        # フォルダを指定したら、そのフォルダ下のファイル/フォルダをまるっとDL(targetfile_fullpathは考慮しないパターン)
        contents = self.list_files_and_folders(targetfile_fullpath)
        if len(contents['file']) == 0 and len(contents['folder']) == 0 :
            #`targetfile_fullpath`がファイルだったケース
            self.__download_file(targetfile_fullpath, targetfld_to)
        else :
            #`targetfile_fullpath`がフォルダだったケース
            target_folder_to   = targetfld_to
            target_folder_to   = target_folder_to.replace('\\', '/')
            target_folder_from = targetfile_fullpath
            if not os.path.exists(target_folder_to) :
                os.makedirs(target_folder_to)

            for fld_key in contents['folder']:
                fld_from = os.path.join(target_folder_from, fld_key)
                self.download_from_spaces(fld_from, targetfld_to)

            #そのフォルダにあるファイルをDL
            for file_key in contents['file']:
                file_path = os.path.join(target_folder_from, file_key)
                self.__download_file(file_path, target_folder_to)


    def list_files_and_folders(self, folder_name:str) -> dict:
        """
        指定されたフォルダ内のファイルとサブフォルダの一覧を取得する関数です。

        Args:
            folder_name (str): 一覧を取得したいフォルダの名前。このフォルダ内のファイルとサブフォルダがリストされます。
                               フォルダ名の末尾にスラッシュがない場合は自動的に追加されます。

        Returns:
            dict: 'file' キーにはフォルダ内のファイルのリストが、'folder' キーにはサブフォルダのリストが含まれます。
        """

        prefix = folder_name + ('/' if folder_name[-1:] != '/' else  '')
        prefix = prefix.replace('\\', '/')
        contents = {'file': [], 'folder': []}
        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.SPACES_BUCKET_NAME, Prefix=prefix, Delimiter='/'):
            # ファイルを追加
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key != prefix:  # プレフィックス自体は除外
                    contents['file'].append(key[len(prefix):])

            # フォルダを追加
            for prefix_info in page.get('CommonPrefixes', []):
                folder_name = prefix_info['Prefix'][len(prefix):-1]  # 末尾のスラッシュを除去
                contents['folder'].append(folder_name)

        return contents





# サンプルコード
if __name__ == '__main__':

    spaces = digitalocean_spaces()

    #ファイルのアップロード
    spaces.sendfile_to_spaces('digitalocean_access_spaces/__init__.py', 'Kondate/data')
    
    # #ファイルのダウンロード(指定するのがフォルダだったら、そのフォルダ下のファイル・フォルダをマルっとDL)
    # os.mkdir('temp_data')
    spaces.download_from_spaces('test', f'temp_data')
