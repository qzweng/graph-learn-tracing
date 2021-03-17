import sys
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# <2021.01>, deprecated
def timeline_dur_retrieve_2_col(input_file):
    try:
        with open(input_file,'r') as json_file:
            data = json.load(json_file)
            events = data['traceEvents']
            op_dur_list = []
            for event in events:
                name = event.get("name", None)
                dur  = event.get("dur", None)
                if name is None or dur is None:
                    continue
                if "#id=" in name:
                    name = name.split('#id=')[0]
                op_dur_list.append([name, dur])
        return pd.DataFrame(op_dur_list, columns=['name','dur'])
    except:    
        return None
# </2021.01>

# <2021.02>
def simplify_metadata_to_3_cat(metadata):
    metadata_simple = {}
    for key, val in metadata.items():
        if 'memcpy' in val:
            device = 'MEMCPY'
        elif 'GPU' in val and 'CPU' not in val:
            device = 'GPU'
        elif 'CPU' in val and 'GPU' not in val:
            device = 'CPU'
        else:
            device = 'NA'
        metadata_simple[key] = device
    return metadata_simple

def timeline_dur_retrieve(input_file):
    try:
        with open(input_file,'r') as json_file:
            data = json.load(json_file)
            events = data['traceEvents']
            op_dur_list = []
            metadata = {}
            for event in events:
                name = event.get("name", None)
                dur  = event.get("dur", None)
                pid = event.get('pid', None)
                cat = event.get('cat', None)
                phrase = event.get("ph", None)
                args = event.get('args', dict())
                if phrase == 'M': # metadata
                    if len(args) > 0:
                        device = args.get('name', None)
                    metadata[pid] = device
                if name is None or dur is None:
                    continue
                if "#id=" in name:
                    name = name.split('#id=')[0]
                op_dur_list.append([name, dur, pid, cat, phrase])
        output_df = pd.DataFrame(op_dur_list, columns=['name','dur','pid','cat','phrase'])

        metadata_simple = simplify_metadata_to_3_cat(metadata)
        output_df['device'] = output_df.pid.apply(lambda x: metadata_simple.get(x, None))
        output_df['name'] = output_df.apply(lambda row:
            "{}/{}".format(row['device'], row['name']), axis=1)
        return output_df[['name','dur']]
    except:
        return None
# </2021.02>

def summarize_df(df):
    if df is None:
        return None
    dfg = df.groupby('name').sum()
    dfg.columns=['dur_sum']
    dfg = dfg.join(df.groupby('name').count())
    dfg.columns=['dur_sum','dur_num']
    dfg = dfg.sort_values('dur_sum', ascending=False).reset_index()
    dfg['ratio'] = dfg['dur_sum']/dfg.dur_sum.sum()
    return dfg

def compat_format(df):
    return df.set_index('name')[['ratio']] if df is not None else None

"""
                     name  dur_sum  dur_num
0              MEMCPYDtoH        6        6
1                    Size        8        1
2               RefSwitch        8        1
......
43                    Sum      560       33
44                    Mul     1407       96
45                 MatMul     2425       45
46             MEMCPYHtoD     6286        6
47        IteratorGetNext    32059        1
"""

def barplot_ratio(df, num_col=10, figname='barplot.png'):
    col_order = df.columns[:num_col].to_list()
    df = pd.melt(df[df.columns[:num_col]])
    df.columns=['Ops','Duration Proportion']
    df.sort_values('Duration Proportion', ascending=False, inplace=True)
    df['Duration Proportion'] *= 100
    plt.figure(figsize=(16, 8), dpi=120)
    sns.barplot(data=df, x='Ops', y='Duration Proportion', capsize=.1, ci=95, order=col_order) # 95% confidence interval as error bar
    plt.ylabel('Duration Proportion in %')
    plt.grid(alpha=0.8, linestyle='-.')
    plt.savefig(figname)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python this.py file1.json, file2.json, ...")
        exit
    file_list = sys.argv[1:]
    op_dur_df_list = []
    for json_file in file_list:
        if not json_file.endswith('json'):
            continue
        opdur_stats = timeline_dur_retrieve(json_file)
        op_dur_df_list.append(compat_format(summarize_df(opdur_stats)))
    res_df = pd.concat(op_dur_df_list, axis=1).T
    sorted_column_order = res_df.T.mean(axis=1).sort_values(ascending=False).index.tolist()
    res_df = res_df[sorted_column_order]
    output_file_prefix = 'timeline-{}-combined'.format(len(op_dur_df_list))
    res_df.to_csv(output_file_prefix+'.csv')
    barplot_ratio(res_df, figname=output_file_prefix+'.png')
    print('output to', output_file_prefix)

"""
"name": "IteratorGetNext",
"MEMCPYHtoD"
"MEMCPYDtoH"
"""

# file_list = ['timeline-10.json', 'timeline-144.json', 'timeline-190.json', 'timeline-6.json', 'timeline-100.json', 'timeline-146.json', 'timeline-192.json', 'timeline-60.json', 'timeline-102.json', 'timeline-148.json', 'timeline-194.json', 'timeline-62.json', 'timeline-104.json', 'timeline-150.json', 'timeline-2.json', 'timeline-64.json', 'timeline-106.json', 'timeline-152.json', 'timeline-20.json', 'timeline-66.json', 'timeline-108.json', 'timeline-154.json', 'timeline-22.json', 'timeline-68.json', 'timeline-110.json', 'timeline-156.json', 'timeline-24.json', 'timeline-70.json', 'timeline-112.json', 'timeline-158.json', 'timeline-26.json', 'timeline-72.json', 'timeline-114.json', 'timeline-16.json', 'timeline-28.json', 'timeline-74.json', 'timeline-116.json', 'timeline-160.json', 'timeline-30.json', 'timeline-76.json', 'timeline-118.json', 'timeline-162.json', 'timeline-32.json', 'timeline-78.json', 'timeline-12.json', 'timeline-164.json', 'timeline-34.json', 'timeline-8.json', 'timeline-120.json', 'timeline-166.json', 'timeline-36.json', 'timeline-80.json', 'timeline-122.json', 'timeline-168.json', 'timeline-38.json', 'timeline-82.json', 'timeline-124.json', 'timeline-170.json', 'timeline-4.json', 'timeline-84.json', 'timeline-126.json', 'timeline-172.json', 'timeline-40.json', 'timeline-86.json', 'timeline-128.json', 'timeline-174.json', 'timeline-42.json', 'timeline-88.json', 'timeline-130.json', 'timeline-176.json', 'timeline-44.json', 'timeline-90.json', 'timeline-132.json', 'timeline-178.json', 'timeline-46.json', 'timeline-92.json', 'timeline-134.json', 'timeline-18.json', 'timeline-48.json', 'timeline-94.json', 'timeline-136.json', 'timeline-180.json', 'timeline-50.json', 'timeline-96.json', 'timeline-138.json', 'timeline-182.json', 'timeline-52.json', 'timeline-98.json', 'timeline-14.json', 'timeline-184.json', 'timeline-54.json', 'timeline-140.json', 'timeline-186.json', 'timeline-56.json', 'timeline-142.json', 'timeline-188.json', 'timeline-58.json']