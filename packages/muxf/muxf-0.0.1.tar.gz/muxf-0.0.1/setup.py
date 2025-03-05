import os
import re
import setuptools
import json
import socket
import datetime
import requests
from setuptools.command.install import install
from setuptools.command.develop import develop


root = os.path.dirname(os.path.abspath(__file__))


def load_pkg_info():
  info = dict()

  file = os.path.join(root, 'PKG-INFO')
  if os.path.isfile(file):
    with open(file, 'r+', encoding='utf-8') as fo:
      for line in fo.readlines():
        line = line.strip()
        kv = line.split(':', maxsplit=1)
        if len(kv) < 2:
          continue
        k = kv[0].strip().lower()
        v = kv[1].strip()

        info[k] = v
  else:
    name = os.path.basename(root)
    ver_json_file = os.path.join(root, 'version.json')
    if os.path.isfile(ver_json_file):
      with open(ver_json_file, 'r+', encoding='utf-8') as fo:
        ver_json = json.loads(fo.read())  # type: dict
        major = ver_json.get('major')
        minor = ver_json.get('minor')
        patch = ver_json.get('patch')
    major, minor, patch = getver(name, major=major, minor=minor, patch=patch)
    version = f'{major}.{minor}.{patch+1}'
    url = f"https://pypi.org/project/{name}/"

    info['name'] = name
    info['version'] = version
    info['home-page'] = url

  return info


def getver(name, major=None, minor=None, patch=None):
  import requests

  pattern = '{} {}'.format(name, '\\.'.join([f'({x})' if isinstance(x, int) else '(\\d+)' for x in (major, minor, patch)]))

  res = requests.get(f'https://pypi.org/project/{name}/')

  items = re.findall(pattern, res.content.decode())
  if not items:
    major = major if isinstance(major, int) else 0
    minor = minor if isinstance(minor, int) else 0
    patch = patch if isinstance(patch, int) else 0
  else:
    major, minor, patch = items[0]
    major = int(major)
    minor = int(minor)
    patch = int(patch)

  return major, minor, patch


def setup():
  pkg_info = load_pkg_info()
  name = pkg_info['name']
  version = pkg_info['version']
  url = pkg_info['home-page']

  requirements = []

  requirements_txt = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
  if os.path.isfile(requirements_txt):
    with open(requirements_txt, 'r+') as fo:
      for line in fo.readlines():
        item = line.split('#')[0].strip()
        if len(item):
          requirements.append(item)

  # 通知安装信息到企业微信函数
  def notify_install(name, version):
    """
    安装后通知企业微信群
    """
    try:
        # 获取主机名
        hostname = socket.gethostname()
        
        # 获取当前时间
        install_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 准备发送到企业微信的消息
        webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=79acba9d-1425-499a-87e7-13c7270f09a7"
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"### {name} 安装通知\n"
                           f"> **版本**: {version}\n"
                           f"> **时间**: {install_time}\n"
                           f"> **主机**: {hostname}"
            }
        }
        
        # 发送消息
        response = requests.post(
            webhook_url,
            data=json.dumps(message),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('errcode') == 0:
                print(f"已成功发送{name}安装通知到企业微信")
            else:
                print(f"发送通知失败: {response_data.get('errmsg')}")
        else:
            print(f"发送通知失败，HTTP状态码: {response.status_code}")
            
    except Exception as e:
        print(f"发送安装通知时发生错误: {str(e)}")

  # 定义安装后执行通知的命令类
  class PostInstallCommand(install):
    def run(self):
      install.run(self)
      self._post_install()

    def _post_install(self):
      # 安装后执行通知
      try:
        notify_install(name, version)
      except Exception as e:
        print(f"安装通知执行错误: {str(e)}")

  # 定义开发模式安装后执行通知的命令类
  class PostDevelopCommand(develop):
    def run(self):
      develop.run(self)
      self._post_install()

    def _post_install(self):
      # 安装后执行通知
      try:
        notify_install(name, version)
      except Exception as e:
        print(f"安装通知执行错误: {str(e)}")

  setuptools.setup(
    name=name,
    version=version,
    keywords=[name],
    author="muxiaofei",
    author_email="muxiaofei@muxf.cn",
    description="",
    long_description="",
    long_description_content_type="text/x-rst",
    url=url,
    packages=setuptools.find_packages(),
    classifiers=[
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
  )


if __name__ == '__main__':
    setup()
