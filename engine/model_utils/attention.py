import torch
import torch.nn as nn
import torch.nn.functional as F
import math 
import yaml
from typing import Optional 

def load_model_config():
    with open('engine/general_utils/model_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config
    
model_config = load_model_config()
d_model = model_config['d_model']
num_heads = model_config['num_heads']
dropout = model_config['dropout']

class MultiHeadAttention(nn.Module):
    """
    Multi-head attention mechanism similar to what is described in 'Attention is all you need'
    You linearly project each of the queries, keys and values with different learned projections
    And in each head, self attention is applied, the result are concatenated and projected to the output
    
    This basically helps the model to jointly attend to information from different positions, with different represenatational subspaces
    For example, if we have a sentence "He went to the bank to get some money, and later went for a walk along the river bank"
    The model should be able to attend to the words "bank" in different ways:
    - "bank" as a place to get money
    - "bank" as a place to walk along the river
    """
    def __init__(self, d_model: int = d_model, num_heads: int = num_heads, dropout: float = dropout):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # dk is the dimension of each head's key, query and value 
        
        # linear layers for queries, keys and values projections
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        
        self.out_proj = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)
        
    def self_attention(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        The popular self attention 
        
        Args: 
            query: [batch size, num heads, seq len q, d_k]
            key: [batch size, num heads, seq len k, d_k]
            value: [batch size, num heads, seq len v, d_k]
            mask: [batch size, 1, seq len q, seq len k]
        Returns:
            Tensor of shape [batch size, num heads, seq len, d_k]
        """
        similarity = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            similarity = similarity.masked_fill(mask == 0, -1e9)
        attention_weights = F.softmax(similarity, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        attention_scores = torch.matmul(attention_weights, v)
        return attention_scores, attention_weights
    
    