# sacct-analyze

The script calls `sacct --json` and parses it. 

## Usage
```
usage: sacct-analyze.py [-h] [--name NAME]

optional arguments:
  -h, --help   show this help message and exit
  --name NAME  Should have these contents in the name
```

### Example
```
python3 sacct-analyze.py --name 'common_job_prefix' > results.tsv
```


## Example output

Name | Requested CPU | Available CPU time (hours) | Used CPU time (hours)|CPU Efficiency (%)|Requested Memory (GiB)|Used Memory (GiB)|Memory efficiency (%)|Requested Time (hours)|Used Time (hours)|Time Efficiency (%)
--- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --:
call-deepVariantTask-2|4|17.83|17.13|96.03%|48.00|8.03|16.73%|83.33|4.46|5.35%
call-deepVariantTask-6|4|17.30|16.45|95.09%|48.00|7.98|16.63%|83.33|4.33|5.19%
call-deepVariantTask-1|4|50.05|48.72|97.33%|48.00|9.30|19.38%|83.33|12.51|15.02%
call-deepVariantTask-3|4|50.53|49.26|97.49%|48.00|9.39|19.57%|83.33|12.63|15.16%
call-deepVariantTask-0|4|40.17|39.08|97.29%|48.00|8.04|16.74%|83.33|10.04|12.05%
call-deepVariantTask-4|4|35.69|34.60|96.94%|48.00|8.06|16.79%|83.33|8.92|10.71%
