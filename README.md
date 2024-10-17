## Dependencies
All the required packages can be installed by running
```
pip install -r requirements.txt
```
## Usage
To start training the Clust-LP model (on WN18RR v1 as an example), run the following command:
```
python train.py -d WN18RR_v1 -e grail_wn_v1
```

To test the model, run the following commands:
```
- python test_auc.py -d WN18RR_v1_ind -e grail_wn_v1
- python test_ranking.py -d WN18RR_v1_ind -e grail_wn_v1
```
