import torch 
import torch.nn as nn 
import math 

class PositionalEncoding(nn.Module):
    """
    Implements sinusoidal positional encoding as described in "Attention is All You Need"
    
    This will add positional information to the input embeddings since transformer architectures 
    don't inherently understand the sequence order
    """
    def __init__(self,
                 embedding_dim: int,
                 max_sequence_length: int,
                 dropout_prob: float):
        super().__init__()
        
        self.dropout = nn.Dropout(p=dropout_prob)
        
        position = torch.arange(max_sequence_length).unsqueeze(1)
        # implement the sinusoidal encoding (formula at page 6 of the paper)
        denominator = torch.exp(torch.arange(0, embedding_dim, 2) * (-math.log(10000.0) / embedding_dim))
        
        pe = torch.zeros(1, max_sequence_length, embedding_dim)
        pe[0,:,0::2] = torch.sin(position * denominator)
        pe[0,:,1::2] = torch.cos(position * denominator)
        
        # since the positional encoding are not learned, we can simply store them in model state
        self.register_buffer('pe', pe)
    
    def forward(self, 
                x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input Tensor of shape [batch size, seq len, embedding dim]
        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)

class TokenEmbedding(nn.Module):
    """
    Embeds the input tokens into a vector space of dimension d_model
    Also we have to scale the embeddings by sqrt(d_model) as described in the paper page 5
    """
    def __init__(self,
                 vocab_size: int,
                 embedding_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.embedding_dim = embedding_dim
        
    def forward(self, 
                x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input Tensor of shape [batch size, seq len]
        
        Returns:
            Embedded tokens scaled by sqrt(d_model) [batch size, seq len, embedding dim]
        """
        return self.embedding(x) * math.sqrt(self.embedding_dim)
    
        
        
        