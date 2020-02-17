#!/usr/bin/env python
# -*- coding:utf-8 -*-
import glob
import hashlib
import json
import os
import shutil
import tempfile
from os.path import join

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

_ = join


def generate_distribution_file(url,
                               mod_file_path,
                               out_file_path):
    """
    trielaで使用する配布用設定ファイルを作成する。
    :param url:
    :param mod_file_path:
    :param out_file_path:
    :return:
    """

    with open(mod_file_path, 'rb') as fr:
        md5 = hashlib.md5(fr.read()).hexdigest()

    d_new = {'file_md5': md5,
             'url': url,
             'file_size': os.path.getsize(mod_file_path)}

    with open(out_file_path, "w", encoding="utf-8") as fw:
        json.dump(d_new, fw, indent=2, ensure_ascii=False)


def upload_mod_to_google_drive(upload_file_path,
                               name,
                               folder_id):
    """
    GoogleDriveにファイルをアップロードする
    :param upload_file_path:
    :param name:
    :param folder_id:
    :return: CDNのURL
    """

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    drive = GoogleDrive(gauth)

    file1 = drive.CreateFile({
        'title': name,
        'parents': [
            {
                "kind": "drive#fileLink",
                "id": folder_id
            }
        ]
    })
    file1.SetContentFile(upload_file_path)
    file1.Upload()

    file1.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'})

    file1.FetchMetadata()

    return "{}/{}?key={}&alt=media".format("https://www.googleapis.com/drive/v3/files",
                                           file1['id'],
                                           "AIzaSyAAt1kNBcu9uiPWPIxAcR0gZefmWHcjjpM")


def generate_dot_mod_file(mod_title_name,
                          mod_file_name,
                          mod_tags,
                          mod_dependencies,
                          mod_image_file_path,
                          out_dir_path,
                          mod_user_dir_name=None):
    """
    .mod.modファイルを作る
    :param mod_title_name:
    :param mod_file_name: zipファイルの名前（.zipを含まない）
    :param mod_user_dir_name:ユーザ作業ディレクトリ名
    :param mod_tags: Set<String>型
    :param mod_dependencies: Set<String>型 依存先MOD
    :param mod_image_file_path:
    :param out_dir_path: 出力ディレクトリのパス
    :return: 出力ファイルパス
    """

    os.makedirs(out_dir_path, exist_ok=True)

    out_file_path = _(out_dir_path, "{}.mod.mod".format(mod_file_name))

    if mod_user_dir_name is None:
        mod_user_dir_name = mod_file_name

    with open(out_file_path, "w", encoding="utf-8") as fw:
        lines = [
            'name="{}"'.format(mod_title_name),
            'archive="mod/{}.zip"'.format(mod_file_name),
            'user_dir="{}"'.format(mod_user_dir_name),
            'tags={}'.format("{" + " ".join(map(lambda c: '"{}"'.format(c), mod_tags)) + "}"),
            'picture="{}"'.format(mod_image_file_path),
            'dependencies={}'.format("{" + " ".join(map(lambda c: '"{}"'.format(c), mod_dependencies)) + "}"),
        ]

        fw.write("\n".join(lines))

    return out_file_path


def pack_mod(out_file_path,
             mod_zip_path,
             mod_title_name,
             mod_file_name,
             mod_tags,
             mod_dependencies,
             mod_image_file_path,
             mod_user_dir_name=None):
    with tempfile.TemporaryDirectory() as temp_dir_path:
        # .mod.modファイルを作成する
        generate_dot_mod_file(
            mod_title_name=mod_title_name,
            mod_file_name=mod_file_name,
            mod_tags=mod_tags,
            mod_dependencies=mod_dependencies,
            mod_user_dir_name=mod_user_dir_name,
            mod_image_file_path=mod_image_file_path,
            out_dir_path=temp_dir_path)

        # zipをコピー
        shutil.copy(mod_zip_path, _(temp_dir_path, "{}.zip".format(mod_file_name)))

        return shutil.make_archive(out_file_path, 'zip', root_dir=temp_dir_path)


def assembly_app_mod_zip_file(out_file_path):
    """
    Appモッドを作成
    :param out_file_path: 出力ファイルパス
    :return:
    """
    with tempfile.TemporaryDirectory() as temp_dir_path:
        os.makedirs(_(temp_dir_path, 'gfx'), exist_ok=True)
        os.makedirs(_(temp_dir_path, 'gfx', 'fonts'), exist_ok=True)

        for file in glob.glob('**/*.dds', recursive=True):
            print(file)
            shutil.copy(file, _(temp_dir_path, 'gfx', 'fonts'))

        for file in glob.glob('**/*.tga', recursive=True):
            print(file)
            shutil.copy(file, _(temp_dir_path, 'gfx', 'fonts'))

        for file in glob.glob('**/*.fnt', recursive=True):
            print(file)
            shutil.copy(file, _(temp_dir_path, 'gfx', 'fonts'))

        # zip化する
        return shutil.make_archive(out_file_path, 'zip', root_dir=temp_dir_path)


def init_workspace():
    # 初期化
    out_dir_path = _(".", "out")
    tmp_dir_path = _(".", "tmp")

    if os.path.exists(out_dir_path):
        shutil.rmtree(out_dir_path)
    if os.path.exists(tmp_dir_path):
        shutil.rmtree(tmp_dir_path)

    # 一時フォルダ用意
    os.makedirs(tmp_dir_path, exist_ok=True)
    os.makedirs(out_dir_path, exist_ok=True)


def main():
    init_workspace()

    # main name
    mod_file_name = "jpmod_font_gothic"

    # AppModを構築する
    app_mod_zip_file_path = assembly_app_mod_zip_file(_('.', 'tmp', mod_file_name))

    # packする
    mod_pack_file_path = pack_mod(
        out_file_path=_(".", "out", mod_file_name),
        mod_file_name=mod_file_name,
        mod_zip_path=app_mod_zip_file_path,
        mod_title_name="JPMOD Font: Gothic",
        mod_tags={"Translation", "Localisation"},
        mod_dependencies=["JPMOD Main 1: Fonts and UI"],
        mod_image_file_path="title.jpg",
        mod_user_dir_name="JLM")

    print("mod_pack_file_path:{}".format(mod_pack_file_path))

    # FileをGoogle Driveにアップロード from datetime import datetime as dt
    from datetime import datetime as dt
    cdn_url = upload_mod_to_google_drive(
        upload_file_path=mod_pack_file_path,
        name=dt.now().strftime('%Y-%m-%d_%H-%M-%S-{}.zip'.format("ck2-font-gothic")),
        folder_id='1MUdH6S6O-M_Y5jRUzNrzQ8tPZOhm_aES')

    print("cdn_url:{}".format(cdn_url))

    # distributionファイルを生成する
    generate_distribution_file(url=cdn_url,
                               out_file_path=_(".", "out", "dist.v2.json"),
                               mod_file_path=mod_pack_file_path)


if __name__ == "__main__":
    main()
