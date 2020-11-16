from base64 import b64decode
from os import path
from io import BytesIO

import requests
from torch import zeros, device, load
from torch import nn
from torchvision.transforms.functional import to_tensor
from collections import OrderedDict
from string import digits, ascii_lowercase
from PIL import Image

# 基本的参数
characters = '-' + digits + ascii_lowercase
width, height, n_len, n_classes = 100, 40, 5, len(characters)
n_input_length = 12


class Model(nn.Module):
    def __init__(self, n_classes, input_shape=(3, 64, 128)):
        super(Model, self).__init__()
        self.input_shape = input_shape
        channels = [32, 64, 128, 256, 256]
        layers = [2, 2, 2, 2, 2]
        kernels = [3, 3, 3, 3, 3]
        # pools = [2, 2, 2, 2, (2, 1)]
        # 减少一个池化层
        pools = [2, 2, 2, (2, 1)]
        modules = OrderedDict()

        def cba(name, in_channels, out_channels, kernel_size):
            modules[f'conv{name}'] = nn.Conv2d(in_channels, out_channels, kernel_size,
                                               padding=(1, 1) if kernel_size == 3 else 0)
            modules[f'bn{name}'] = nn.BatchNorm2d(out_channels)
            modules[f'relu{name}'] = nn.ReLU(inplace=True)

        last_channel = 3
        for block, (n_channel, n_layer, n_kernel, k_pool) in enumerate(zip(channels, layers, kernels, pools)):
            for layer in range(1, n_layer + 1):
                cba(f'{block + 1}{layer}', last_channel, n_channel, n_kernel)
                last_channel = n_channel
            modules[f'pool{block + 1}'] = nn.MaxPool2d(k_pool)
        modules[f'dropout'] = nn.Dropout(0.25, inplace=True)

        self.cnn = nn.Sequential(modules)
        self.lstm = nn.LSTM(input_size=self.infer_features(), hidden_size=128, num_layers=2, bidirectional=True)
        self.fc = nn.Linear(in_features=256, out_features=n_classes)

    def infer_features(self):
        x = zeros((1,) + self.input_shape)
        x = self.cnn(x)
        x = x.reshape(x.shape[0], -1, x.shape[-1])
        return x.shape[1]

    def forward(self, x):
        x = self.cnn(x)
        x = x.reshape(x.shape[0], -1, x.shape[-1])
        x = x.permute(2, 0, 1)
        x, _ = self.lstm(x)
        x = self.fc(x)
        return x


def decode(sequence):
    a = ''.join([characters[x] for x in sequence])
    s = ''.join([x for j, x in enumerate(a[:-1]) if x != characters[0] and x != a[j + 1]])
    if len(s) == 0:
        return ''
    if a[-1] != characters[0] and s[-1] != a[-1]:
        s += a[-1]
    return s


def decode_target(sequence):
    return ''.join([characters[x] for x in sequence]).replace(' ', '')


""" 加载训练后的模型 """
import sys
model = Model(n_classes, input_shape=(3, height, width))
filename = path.dirname(path.realpath(sys.argv[0]))
# if not path.exists(path.join(filename, 'ctc_625_22.pth')):
#     print("正在下载验证码模型文件......")
#     url = "https://cdn.jsdelivr.net/gh/skygongque/captcha-weibo/ctc_625_22.pth"
#     res = requests.get(url=url)
#     with open(path.join(filename, 'ctc_625_22.pth'), 'wb') as f:
#         f.write(res.content)
#         print("ctc_625_22.pth下载完成......")
model.load_state_dict(load(path.join(filename, 'ctc_625_22.pth'), map_location=device('cpu')))
model.eval()


def predict(base64_img):
    image = Image.open(BytesIO(b64decode(base64_img)))
    # 转换成3通道
    image = to_tensor(image.convert("RGB"))
    output = model(image.unsqueeze(0))
    output_argmax = output.detach().permute(1, 0, 2).argmax(dim=-1)
    pred_str = decode(output_argmax[0])
    return pred_str
