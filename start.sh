#!/bin/bash
cd /tmp; git clone https://github.com/alibaba/graph-learn.git
# https://www.jianshu.com/p/d403f5bbc58e

cd /tmp/graph-learn/examples
pip install -r requirements.txt # networkx==1.11
pip install ipython

cd /tmp/graph-learn/examples/data
python arxiv.py; python blogcatelog.py; python cora.py; python fb15k_237.py; python ppi.py; python u2i.py; python utils.py

cd /tmp/graph-learn/examples/tf
cd graphsage
python train_supervised.py

cd ../gcn
python train_supervised.py

# ......