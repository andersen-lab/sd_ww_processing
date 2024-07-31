from freyja.utils import prepLineageDict
import pandas as pd
# below supresses SettingWithCopyWarning
pd.options.mode.chained_assignment = None
from datetime import date,timedelta,datetime
import yaml
# import sys
# # replace with freyja path
# sys.path.insert(1, '/shared/workspace/software/freyja')
def get_col_date(short_name, site):
    col_date = short_name.strip(site)
    day = ''
    if 'JAN' in col_date:
        month = 1
        day = col_date.strip('JAN')
    elif 'FEB' in col_date:
        month = 2
        day = col_date.strip('FEB')
    elif 'MAR' in col_date:
        month = 3
        day = col_date.strip('MAR')
    elif 'APR' in col_date:
        month = 4
        day = col_date.strip('APR')
    elif 'MAY' in col_date:
        month = 5
        day = col_date.strip('MAY')
    elif 'JUN' in col_date:
        month = 6
        day = col_date.strip('JUN')
    elif 'JUL' in col_date:
        month = 7
        day = col_date.strip('JUL')
    elif 'AUG' in col_date:
        month = 8
        day = col_date.strip('AUG')
    elif 'SEP' in col_date:
        month = 9
        day = col_date.strip('SEP')
    elif 'OCT' in col_date:
        month = 10
        day = col_date.strip('OCT')
    elif 'NOV' in col_date:
        month = 11
        day = col_date.strip('NOV')
    elif 'DEC' in col_date:
        month = 12
        day = col_date.strip('DEC')
    return str(month) + '/' + str(day) + '/' + str(datetime.now().year)[-2:]
with open("plot_config.yml", "r" ) as f :
    plot_config = yaml.safe_load(f)
#make copy of config for later
plot_config_ = dict(plot_config)
#remove the "Recombinants" and "Other" keys for now.
del plot_config['Other']
del plot_config['Recombinants']
for key in reversed( list( plot_config.keys() ) ):
    plot_config[key]['members'] = [mem.replace('.X','*') for mem in plot_config[key]['members']]
   #----#
# update the file below with the update freyja command
with open('lineages.yml', 'r') as f:
        try:
            lineages_yml = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError('Error in lineages.yml file: ' + str(exc))
lineage_info = {}
for lineage in lineages_yml:
    lineage_info[lineage['name']] = {'children': lineage['children']}
agg_df = pd.read_csv(f'agg_outputs.tsv', skipinitialspace=True, sep='\t',index_col=0)
agg_df = agg_df[agg_df['coverage'] > 70]
agg_df = prepLineageDict(agg_df,thresh=0.0000000001,config=plot_config,lineage_info=lineage_info)
formatted_agg = agg_df['linDict'].apply(pd.Series)
# drop any columns that aren't in the plot_config file
formatted_agg = formatted_agg[[key for key in plot_config_.keys() if key in formatted_agg.columns]]
#add abundance associated with things not in the plot config to recombinants or other
recombs = [fc for fc in formatted_agg.columns if (fc not in plot_config.keys()) and (fc[0]=='X')]
formatted_agg['Recombinants'] = formatted_agg[recombs].sum(axis=1)
#formatted_agg = formatted_agg.drop(columns=recombs)
others = [fc for fc in formatted_agg.columns if (fc not in plot_config.keys()) and fc!='Recombinants']
formatted_agg['Other'] = formatted_agg[others].sum(axis=1)
#formatted_agg = formatted_agg.drop(columns=others)
formatted_agg = formatted_agg.mul(100)
#separate out by site
pl_agg = formatted_agg[formatted_agg.index.str.contains('PL')]
enc_agg = formatted_agg[formatted_agg.index.str.contains('ENC')]
sb_agg = formatted_agg[formatted_agg.index.str.contains('SB')]
pl_agg = pl_agg.reset_index()
enc_agg = enc_agg.reset_index()
sb_agg = sb_agg.reset_index()
for i in range(len(pl_agg)):
    pl_agg['index'][i] = pl_agg['index'][i].replace(pl_agg['index'][i], get_col_date(pl_agg['index'][i].split('__')[0].split('_')[3], "PL"))
for i in range(len(enc_agg)):
    enc_agg['index'][i] = enc_agg['index'][i].replace(enc_agg['index'][i], get_col_date(enc_agg['index'][i].split('__')[0].split('_')[3], "ENC"))
for i in range(len(sb_agg)):
    sb_agg['index'][i] = sb_agg['index'][i].replace(sb_agg['index'][i], get_col_date(sb_agg['index'][i].split('__')[0].split('_')[3], "SB"))
pl_agg = pl_agg.rename(columns={"index": "Date"})
enc_agg = enc_agg.rename(columns={"index": "Date"})
sb_agg = sb_agg.rename(columns={"index": "Date"})
# pull the latest summary files from github and read as df
# https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/PointLoma_sewage_seqs.csv
# https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/Encina_sewage_seqs.csv
# https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/SouthBay_sewage_seqs.csv
pl_agg['Date'] = pd.to_datetime(pl_agg['Date'], format='%m/%d/%y')
pl_git_df = pd.read_csv("https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/PointLoma_sewage_seqs.csv")
# pl_git_df = pl_git_df.drop(pl_git_df.tail(16).index)
pl_git_df['Date'] = pd.to_datetime(pl_git_df['Date'])
pl_out_df = pd.concat([pl_git_df, pl_agg])
# pl_out_df = pl_out_df[['Date', 'BA.1', 'BA.1.1.X', 'BA.2.X', 'BA.2.12.X', 'BA.4.X', 'BA.5.X', 'B.1.1.529', 'AY.113', 'AY.100', 'AY.20', 'AY.25', 'AY.3', 'AY.44', 'AY.119', 'AY.3.1', 'AY.103', 'AY.46.4', 'AY.25.1', 'AY.116', 'AY.43.4', 'Other Delta sub-lineages','BA.2.75', 'BA.4.6', 'BQ.1.X', 'BQ.1.1.X', 'BF.7.X','BN.1.X', 'XBB.X', 'XBB.1.5.X', 'XBB.1.9.X', 'XBB.1.16.X', 'XBB.2.3.X', 'EG.5.X', 'BA.2.86.X', 'HV.1.X', 'JN.1.X', 'JN.1.7.X', 'JN.1.4.X', 'KQ.1.X', 'JN.1.11.X', 'KP.2.X', 'Recombinants', 'Other']]
pl_out_df = pl_out_df.fillna(0.00).round(2).drop_duplicates(subset=['Date'],keep='last')
pl_out_df = pl_out_df.sort_values(by=['Date'])
pl_out_df.to_csv('PointLoma_sewage_seqs.csv', index=False)
# pl_out_df.to_csv('freyja_reports/output/PointLoma_sewage_seqs.csv')
enc_agg['Date'] = pd.to_datetime(enc_agg['Date'], format='%m/%d/%y')
enc_git_df = pd.read_csv("https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/Encina_sewage_seqs.csv")
# enc_git_df = enc_git_df.drop(enc_git_df.tail(7).index)
enc_git_df['Date'] = pd.to_datetime(enc_git_df['Date'])
enc_out_df = pd.concat([enc_git_df, enc_agg])
# enc_out_df = enc_out_df[['Date', 'BA.1', 'BA.1.1.X', 'BA.2.X', 'BA.2.12.X', 'BA.4.X', 'BA.5.X', 'BA.2.75', 'BA.4.6', 'BQ.1.X', 'BQ.1.1.X', 'BF.7.X', 'XBB.X', 'XBB.1.5.X', 'XBB.1.9.X', 'XBB.1.16.X', 'XBB.2.3.X', 'EG.5.X', 'BA.2.86.X', 'HV.1.X', 'JN.1.X', 'JN.1.7.X', 'JN.1.4.X', 'KQ.1.X', 'JN.1.11.X', 'KP.2.X', 'Recombinants', 'Other']]
enc_out_df = enc_out_df.fillna(0.00).round(2).drop_duplicates(subset=['Date'],keep='last')
enc_out_df = enc_out_df.sort_values(by=['Date'])
enc_out_df.to_csv('Encina_sewage_seqs.csv', index=False)
# enc_out_df.to_csv('freyja_reports/output/Encina_sewage_seqs.csv')
sb_agg['Date'] = pd.to_datetime(sb_agg['Date'], format='%m/%d/%y')
sb_git_df = pd.read_csv("https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/SouthBay_sewage_seqs.csv")
# sb_git_df = sb_git_df.drop(sb_git_df.tail(8).index)
sb_git_df['Date'] = pd.to_datetime(sb_git_df['Date'])
sb_out_df = pd.concat([sb_git_df, sb_agg])
# sb_out_df = sb_out_df[['Date', 'BA.1', 'BA.1.1.X', 'BA.2.X', 'BA.2.12.X', 'BA.4.X', 'BA.5.X', 'BA.2.75', 'BA.4.6', 'BQ.1.X', 'BQ.1.1.X', 'BF.7.X', 'XBB.X', 'XBB.1.5.X', 'XBB.1.9.X', 'XBB.1.16.X', 'XBB.2.3.X', 'EG.5.X', 'BA.2.86.X', 'HV.1.X', 'JN.1.X', 'JN.1.7.X', 'JN.1.4.X', 'KQ.1.X', 'JN.1.11.X', 'KP.2.X', 'Recombinants', 'Other']]
sb_out_df = sb_out_df.fillna(0.00).round(2).drop_duplicates(subset=['Date'],keep='last')
sb_out_df = sb_out_df.sort_values(by=['Date'])
sb_out_df.to_csv('SouthBay_sewage_seqs.csv', index=False)