import os
import numpy as np
import torch
import pdb
from sklearn import metrics
import torch.nn.functional as F
from torch.utils.data import DataLoader


class Evaluator():
    def __init__(self, params, graph_classifier, data):
        self.params = params
        self.graph_classifier = graph_classifier
        self.data = data

    def eval(self, save=False):
        pos_scores = []
        pos_labels = []
        neg_scores = []
        neg_labels = []
        dataloader = DataLoader(self.data, batch_size=self.params.batch_size, shuffle=False, num_workers=self.params.num_workers, collate_fn=self.params.collate_fn)

        self.graph_classifier.eval()
        with torch.no_grad():
            try:
                for b_idx, batch in enumerate(dataloader):

                    data_pos, targets_pos, data_neg, targets_neg = self.params.move_batch_to_device(batch, self.params.device)
                    # print([self.data.id2relation[r.item()] for r in data_pos[1]])
                    # pdb.set_trace()
                    score_pos = self.graph_classifier(data_pos)
                    score_neg = self.graph_classifier(data_neg)
    
                    # preds += torch.argmax(logits.detach().cpu(), dim=1).tolist()
                    pos_scores += score_pos.squeeze(1).detach().cpu().tolist()
                    neg_scores += score_neg.squeeze(1).detach().cpu().tolist()
                    pos_labels += targets_pos.tolist()
                    neg_labels += targets_neg.tolist()
            except Exception as e:
                print("Error durante la iteración del DataLoader:", e)
        auc = 0.0
        auc_pr = 0.0
        # acc = metrics.accuracy_score(labels, preds)
        if len(pos_labels) == 0 or len(neg_labels) == 0:
            print("No hay muestras disponibles para calcular el AUC.")
        else:
            auc = metrics.roc_auc_score(pos_labels + neg_labels, pos_scores + neg_scores)

        if len(pos_labels) == 0 or len(neg_labels) == 0:
            print("No hay muestras disponibles para calcular la curva de precisión-recall.")
        else:
            auc_pr = metrics.average_precision_score(pos_labels + neg_labels, pos_scores + neg_scores)


        if save:
            pos_test_triplets_path = os.path.join(self.params.main_dir, 'data/{}/{}.txt'.format(self.params.dataset, self.data.file_name))
            with open(pos_test_triplets_path) as f:
                pos_triplets = [line.split() for line in f.read().split('\n')[:-1]]
            pos_file_path = os.path.join(self.params.main_dir, 'data/{}/grail_{}_predictions.txt'.format(self.params.dataset, self.data.file_name))
            with open(pos_file_path, "w") as f:
                for ([s, r, o], score) in zip(pos_triplets, pos_scores):
                    f.write('\t'.join([s, r, o, str(score)]) + '\n')

            neg_test_triplets_path = os.path.join(self.params.main_dir, 'data/{}/neg_{}_0.txt'.format(self.params.dataset, self.data.file_name))
            with open(neg_test_triplets_path) as f:
                neg_triplets = [line.split() for line in f.read().split('\n')[:-1]]
            neg_file_path = os.path.join(self.params.main_dir, 'data/{}/grail_neg_{}_{}_predictions.txt'.format(self.params.dataset, self.data.file_name, self.params.constrained_neg_prob))
            with open(neg_file_path, "w") as f:
                for ([s, r, o], score) in zip(neg_triplets, neg_scores):
                    f.write('\t'.join([s, r, o, str(score)]) + '\n')

        return {'auc': auc, 'auc_pr': auc_pr}
