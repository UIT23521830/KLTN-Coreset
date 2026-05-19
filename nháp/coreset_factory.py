import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

class CoreTabBase:
    """
    Base class for CoreTab and its variants.
    Provides Datamap calculation (Confidence, Variability).
    """
    def __init__(self, n_trees=30, random_state=42):
        self.n_trees = n_trees
        self.random_state = random_state
        self.confidences = None
        self.variabilities = None

    def _compute_dynamics_xgboost(self, X, y):
        print(f"[*] Computing dynamics using XGBoost ({self.n_trees} trees)...")
        model = XGBClassifier(
            n_estimators=self.n_trees, 
            random_state=self.random_state, 
            objective='multi:softprob'
        )
        model.fit(X, y)
        
        all_probas = []
        for i in range(1, self.n_trees + 1):
            p = model.predict_proba(X, iteration_range=(0, i))
            all_probas.append(p)
            
        all_probas = np.array(all_probas)
        n_samples = X.shape[0]
        # Get proba of correct class
        correct_probas = all_probas[np.arange(self.n_trees)[:, None], np.arange(n_samples), y]
        
        self.confidences = np.mean(correct_probas, axis=0)
        self.variabilities = np.std(correct_probas, axis=0)
        return self.confidences, self.variabilities

    def get_regions(self):
        conf_thresh = np.median(self.confidences)
        var_thresh = np.median(self.variabilities)
        
        is_hard = (self.confidences <= conf_thresh) & (self.variabilities <= var_thresh)
        is_ambiguous = (self.variabilities > var_thresh)
        is_easy = (self.confidences > conf_thresh) & (self.variabilities <= var_thresh)
        
        return is_hard, is_ambiguous, is_easy

# =============================================================================
# PROPOSED VARIANTS
# =============================================================================

class CoreTab(CoreTabBase):
    """ ORIGINAL CoreTab (for base comparison) """
    def select(self, X, y, budget_ratio):
        self._compute_dynamics_xgboost(X, y)
        is_hard, is_amb, is_easy = self.get_regions()
        target_n = int(len(X) * budget_ratio)
        
        # Priority: Hard > Ambiguous > Easy
        importance = np.zeros(len(X))
        importance[is_hard] = 3
        importance[is_amb] = 2
        importance[is_easy] = 1
        
        idx_sorted = np.argsort(-importance)
        return idx_sorted[:target_n]

class CoreSynth(CoreTabBase):
    """ Variant A: Core-Synth (Datamap + Synthesis focus) """
    def select(self, X, y, budget_ratio):
        self._compute_dynamics_xgboost(X, y)
        is_hard, is_amb, _ = self.get_regions()
        target_n = int(len(X) * budget_ratio)
        
        # Simulates synthesis impact by picking even more 'hard' samples 
        # or prioritizing samples in low-density hard regions.
        hard_idx = np.where(is_hard)[0]
        amb_idx = np.where(is_amb)[0]
        
        # Take all Hard, fill with Amb
        selected = np.concatenate([hard_idx, amb_idx])
        return selected[:target_n]

class CoreFair(CoreTabBase):
    """ Variant B: Core-Fair (Datamap + Fairness/Class-balancing) """
    def select(self, X, y, budget_ratio):
        self._compute_dynamics_xgboost(X, y)
        is_hard, is_amb, _ = self.get_regions()
        target_n = int(len(X) * budget_ratio)
        
        unique_classes = np.unique(y)
        samples_per_class = max(1, target_n // len(unique_classes))
        
        selected_indices = []
        for cls in unique_classes:
            cls_idx = np.where(y == cls)[0]
            # Prioritize Hard/Amb in this class
            mask = is_hard[cls_idx] | is_amb[cls_idx]
            cls_important = cls_idx[mask]
            cls_other = cls_idx[~mask]
            
            combined = np.concatenate([cls_important, cls_other])
            selected_indices.extend(combined[:samples_per_class])
            
        return np.array(selected_indices[:target_n])

class SimpleMLP(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(SimpleMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
            nn.Softmax(dim=1)
        )
    def forward(self, x):
        return self.net(x)

class CoreNeural(CoreTabBase):
    """ Variant C: Core-Neural (Neural Proxy) """
    def select(self, X, y, budget_ratio, epochs=5):
        print(f"[*] Computing dynamics using Neural Proxy ({epochs} epochs)...")
        input_dim = X.shape[1]
        output_dim = len(np.unique(y))
        model = SimpleMLP(input_dim, output_dim)
        optimizer = optim.Adam(model.parameters())
        criterion = nn.CrossEntropyLoss()
        
        X_t = torch.FloatTensor(X)
        y_t = torch.LongTensor(y)
        dataset = TensorDataset(X_t, y_t)
        loader = DataLoader(dataset, batch_size=128, shuffle=True)
        
        history_probas = []
        for epoch in range(epochs):
            model.eval()
            with torch.no_grad():
                probas = model(X_t).numpy()
                history_probas.append(probas)
            
            model.train()
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
        
        history_probas = np.array(history_probas) # (epochs, n_samples, n_classes)
        n_samples = X.shape[0]
        correct_probas = history_probas[np.arange(epochs)[:, None], np.arange(n_samples), y]
        
        self.confidences = np.mean(correct_probas, axis=0)
        self.variabilities = np.std(correct_probas, axis=0)
        
        is_hard, is_amb, _ = self.get_regions()
        target_n = int(len(X) * budget_ratio)
        importance = is_hard.astype(int)*3 + is_amb.astype(int)*2
        idx_sorted = np.argsort(-importance)
        return idx_sorted[:target_n]

class CoreCRAIG(CoreTabBase):
    """ Variant D: Core-CRAIG (Datamap + Gradient Matching Proxy) """
    def select(self, X, y, budget_ratio):
        self._compute_dynamics_xgboost(X, y)
        is_hard, is_amb, _ = self.get_regions()
        target_n = int(len(X) * budget_ratio)
        
        # Hybrid: Keep Hard. Match gradients for the rest.
        # Simplified matching: pick samples that spread across the feature space (diversity)
        hard_idx = np.where(is_hard)[0]
        rem_idx = np.where(~is_hard)[0]
        
        if len(hard_idx) >= target_n:
            return hard_idx[:target_n]
            
        selected = list(hard_idx)
        rem_budget = target_n - len(hard_idx)
        
        # Strided sampling as a proxy for diversity
        step = max(1, len(rem_idx) // rem_budget)
        selected.extend(rem_idx[::step][:rem_budget])
        return np.array(selected)

class CoreEnsemble(CoreTabBase):
    """ Variant E: Core-Ensemble (Hybrid Strategy) """
    def select(self, X, y, budget_ratio):
        self._compute_dynamics_xgboost(X, y)
        is_hard, is_amb, is_easy = self.get_regions()
        target_n = int(len(X) * budget_ratio)
        
        # Mix selection: 50% Hard, 30% Ambiguous, 20% Easy
        h = np.where(is_hard)[0]
        a = np.where(is_amb)[0]
        e = np.where(is_easy)[0]
        
        n_h = int(target_n * 0.5)
        n_a = int(target_n * 0.3)
        n_e = target_n - n_h - n_a
        
        res = list(h[:n_h]) + list(a[:n_a]) + list(e[:n_e])
        return np.array(res)[:target_n]

if __name__ == "__main__":
    # Smoke test
    X_test = np.random.rand(1000, 5)
    y_test = np.random.randint(0, 2, 1000)
    
    variants = [CoreTab(), CoreSynth(), CoreFair(), CoreNeural(), CoreCRAIG(), CoreEnsemble()]
    for v in variants:
        idx = v.select(X_test, y_test, 0.1)
        print(f"[+] {v.__class__.__name__} selected {len(idx)} samples.")
