import os
import matplotlib.pyplot as plt
import sys
import pandas as pd
sys.path.append('functions/')

MAX_SAMPLES = 100
MIN_SAMPLES = 10

script_path = os.path.dirname(__file__)
data_dir = os.path.join(script_path, '../data')
processed_data_dir = os.path.join(data_dir, 'processed')
pdb_files_path = os.path.join(data_dir, 'pdbs')
point_cloud_path = os.path.join(data_dir, 'point_cloud_dataset')
datasets_dir = os.path.join(data_dir, 'datasets')

# open data sets
pc_data_path = os.path.join(data_dir, 'datasets/08_point_cloud_dataset.csv')
ec_data_path = os.path.join(data_dir, 'processed/02_uniprotID_and_EC_reduced.csv')
pc_data = pd.read_csv(pc_data_path)
ec_data = pd.read_csv(ec_data_path)

# remove rows when no point cloud available
point_clouds = pc_data['point_cloud'].to_list()
pcs = []
for i, row in ec_data.iterrows():
    protein = row[0] + '.txt'
    if protein not in point_clouds:
        ec_data = ec_data.drop(i)
    else:
        pcs.append(protein)

# find number of enzymes per EC number
ec_nums = ec_data['EC'].to_list()

ec_data['EC'] = ec_nums
ec_data['protein'] = pcs

# filter low_counts
ec_data = ec_data[ec_data.groupby('EC')['EC'].transform('count')>=MIN_SAMPLES].copy()

print(ec_data['EC'].value_counts())


ec_data.to_csv(os.path.join(datasets_dir, '09_balanced_data_set.csv'), index=False)

# split data to train, test, validate
data = ec_data

# find number of enzymes per EC number
labels = data['EC'].unique()

train_x = []
train_y = []
test_x = []
test_y = []
val_x = []
val_y = []
for label in labels:
    df = data[data['EC'] == label]
    num_data = len(df)
    if num_data >= 20:
        test = df.sample(frac=0.2, random_state=1)
        valid = test.sample(frac=0.25, random_state=1)
        train = df.drop(test.index)
        test = test.drop(valid.index)
        for i, row in train.iterrows():
            train_x.append(row[0])
            train_y.append(row[1])
        for i, row in test.iterrows():
            test_x.append(row[0])
            test_y.append(row[1])
        for i, row in valid.iterrows():
            val_x.append(row[0])
            val_y.append(row[1])
    else:
        test = df.sample(frac=0.2, random_state=1)
        valid = test.sample(frac=0.5, random_state=1)
        train = df.drop(test.index)
        test = test.drop(valid.index)
        for i, row in train.iterrows():
            train_x.append(row[0])
            train_y.append(row[1])
        for i, row in test.iterrows():
            test_x.append(row[0])
            test_y.append(row[1])
        for i, row in valid.iterrows():
            val_x.append(row[0])
            val_y.append(row[1])


train = pd.DataFrame({
    'point_cloud': train_x,
    'EC': train_y
})

test = pd.DataFrame({
    'point_cloud': test_x,
    'EC': test_y
})

valid = pd.DataFrame({
    'point_cloud': val_x,
    'EC': val_y
})

train.to_csv(os.path.join(datasets_dir, '09_train.csv'), index=False)
test.to_csv(os.path.join(datasets_dir, '09_test.csv'), index=False)
valid.to_csv(os.path.join(datasets_dir, '09_valid.csv'), index=False)