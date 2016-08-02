import numpy as np
import argparse
from PIL import Image
import time, os, glob

import chainer
from chainer import cuda, Variable, serializers
from net import *

parser = argparse.ArgumentParser(description='Real-time style transfer image generator')
parser.add_argument('input')
parser.add_argument('--gpu', '-g', default=-1, type=int,
                    help='GPU ID (negative value indicates CPU)')
parser.add_argument('--model', '-m', default='models/style.model', type=str)
parser.add_argument('--out', '-o', default='out.jpg', type=str)
args = parser.parse_args()

model = FastStyleNet()
serializers.load_npz(args.model, model)
if args.gpu >= 0:
    cuda.get_device(args.gpu).use()
    model.to_gpu()
xp = np if args.gpu < 0 else cuda.cupy

imagelist = glob.glob(args.input)
multi = True if len(imagelist) > 1 else False
for filename in imagelist:
    start = time.time()
    image = xp.asarray(Image.open(filename).convert('RGB'), dtype=xp.float32).transpose(2, 0, 1)
    image = image.reshape((1,) + image.shape)
    x = Variable(image)

    y = None
    y = model(x)
    result = cuda.to_cpu(y.data)

    result = result.transpose(0, 2, 3, 1)
    result = result.reshape((result.shape[1:]))
    result = np.uint8(result)
    print filename, time.time() - start, 'sec'

    Image.fromarray(result).save('{}{}'.format(args.out, os.path.basename(filename) if multi else ''))
