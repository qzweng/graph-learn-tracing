import tensorflow as tf
from tensorflow.python.client import timeline

run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
run_metadata = tf.RunMetadata()

predictions = use_sess.run(use_out, {'DecodeJpeg/contents:0': image_file.file.getvalue()}, options=run_options, run_metadata=run_metadata)

# Create the Timeline object, and write it to a json
tl = timeline.Timeline(run_metadata.step_stats)
ctf = tl.generate_chrome_trace_format()
with open('timeline.json', 'w') as f:
    f.write(ctf)

"""
作者：lyyyyy
链接：https://juejin.cn/post/6844903597004554254
来源：掘金
"""