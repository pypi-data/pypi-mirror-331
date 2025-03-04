from abc import ABC
import torch
from torch import nn
import torch.nn.functional as F

from ._text_cnn import TextCNN
from ._attention import RNNAttention, CNNRNNAttention, RNNCNNAttention, ResRNNCNNAttention, TransformerEncoder, TransformerDecoder


class Base2DModel(nn.Module, ABC):
	
	def __init__(self, in_features: int, embed_dim: int, hidden_size: int):
		super().__init__()
		if embed_dim <= 1:
			self.reshape = nn.Unflatten(1, (-1, 1))
		else:
			self.reshape = nn.Sequential(
				nn.Linear(in_features, hidden_size),
				nn.Unflatten(1, (-1, embed_dim))
			)
		self.model = None

	def forward(self, inputs: torch.Tensor):
		"""
		:param inputs: [(batch_size, in_features)]
		:return: [(batch_size, out_features)]
		"""
		output = self.reshape(inputs)  # [(batch_size, hidden_size / embed_dim, embed_dim)]]
		return self.model(output)


class TextCNN2D(Base2DModel):
	""" 
	Examples
	--------
	>>> model = TextCNN2D(embed_dim, out_features=len(classes))
	"""

	def __init__(self, in_features: int, out_features: int, embed_dim: int = 16, hidden_size: int = 128, 
			  kernel_sizes=(2, 3, 4), cnn_channels: int = 64, activation=None, num_hidden_layer: int = 0,
              layer_norm=False, batch_norm=False, residual=False, dropout: float = 0.0, bias=False):
		super().__init__(in_features, embed_dim, hidden_size)
		self.model = TextCNN(embed_dim, kernel_sizes, cnn_channels, out_features, activation, num_hidden_layer, 
                     layer_norm, batch_norm, residual, dropout, bias)
		

class RNNAttention2D(Base2DModel):
	""" forward()方法有inputs和sequence_lengths两个参数, 不能直接作为模型用moddel-wrapper训练，
	否则会把y作为sequence_lengths参数传入

	Examples
	--------
	>>> model = RNNAttention2D(embed_dim, out_features=len(classes))
	"""

	def __init__(self, in_features: int, out_features: int, embed_dim: int = 1, hidden_size: int = 128, 
			  num_heads: int = 1, num_layers: int = 2, rnn=nn.GRU, bidirectional=True, layer_norm=False, 
			  residual=False, dropout: float = 0.0):
		super().__init__(in_features, embed_dim, hidden_size)
		self.model = RNNAttention(embed_dim, out_features, hidden_size, num_layers, num_heads,rnn, bidirectional, 
						  layer_norm, residual, dropout)


class CNNRNNAttention2D(Base2DModel):
	"""
	Examples
	--------
	>>> model = CNNRNNAttention2D(embed_dim, out_features=2)
	"""
	
	def __init__(self, in_features: int, out_features: int, embed_dim: int = 1, seq_length: int = 16, cnn_channels: int = 64, 
			  	 kernel_sizes=(2, 3, 4), activation=None, hidden_size: int = 128, num_layers: int = 2, 
				 num_heads: int = 1, rnn=nn.GRU, bidirectional=True, layer_norm=False, batch_norm=False,
	             residual=False, dropout: float = 0.0, bias=False):
		super().__init__(in_features, embed_dim, hidden_size)
		self.model = CNNRNNAttention(embed_dim, out_features, seq_length, cnn_channels, kernel_sizes, activation, hidden_size, 
							 num_layers, num_heads, rnn, bidirectional, layer_norm, batch_norm, residual, dropout, bias)
		

class RNNCNNAttention2D(Base2DModel):
	"""
	Examples
	--------
	>>> model = RNNCNNAttention2D(embed_dim, out_features=2)
	"""
	
	def __init__(self, in_features: int, out_features: int, embed_dim: int = 1, seq_length: int = 16, cnn_channels: int = 64,
			    kernel_sizes=(2, 3, 4), activation=None, hidden_size: int = 128, num_layers: int = 1, num_heads: int = 1,
	            rnn=nn.GRU, bidirectional=True, layer_norm=False, batch_norm=False,
	            dropout: float = 0.0, bias=False):
		super().__init__(in_features, embed_dim, hidden_size)
		self.model = RNNCNNAttention(embed_dim, out_features, seq_length, cnn_channels, kernel_sizes, activation, hidden_size, 
							 num_layers, num_heads, rnn, bidirectional, layer_norm, batch_norm, dropout, bias)
			


class ResRNNCNNAttention2D(Base2DModel):
	"""
	Examples
	--------
	>>> model = ResRNNCNNAttention2D(embed_dim, out_features=2)
	"""
	
	def __init__(self, in_features: int, out_features: int, embed_dim: int = 1, eq_length: int = 16, cnn_channels: int = 64, 
			  	 kernel_sizes=(2, 3, 4), activation=None, hidden_size: int = 128, num_layers: int = 2, 
				 num_heads: int = 1, rnn=nn.GRU, bidirectional=True, layer_norm=False, batch_norm=False,
	             dropout: float = 0.0, bias=False):
		super().__init__(in_features, embed_dim, hidden_size)
		self.model = ResRNNCNNAttention(embed_dim, out_features, eq_length, cnn_channels, kernel_sizes, activation, hidden_size, 
								  num_layers, num_heads, rnn, bidirectional, layer_norm, batch_norm, dropout, bias)


class MultiheadSelfAttention2D(nn.Module):
	def __init__(self, in_features: int, out_features: int, embed_dim: int = 1, hidden_size: int = 128, 
			  num_heads: int = 1, dropout=0.2, bias=True):
		super().__init__()
		self.head = nn.Linear(in_features, hidden_size)
		self.unflatten = nn.Unflatten(1, (-1, embed_dim))
		self.att = nn.MultiheadAttention(embed_dim, num_heads, dropout, bias=bias, batch_first=True)
		self.fc = nn.Linear(hidden_size, out_features)

	def forward(self, src: torch.Tensor):
		x = self.head(src)
		x = F.silu(x)
		x = self.unflatten(x)
		x, _= self.att(x, x, x)
		x = F.silu(x)
		return self.fc(x.flatten(1))
		

class TransformerEncoder2D(nn.Module):
	def __init__(self, in_features: int, out_features: int, embed_dim: int = 8, nhead: int = 1, 
				num_layers: int = 1, hidden_size: int = 128, dim_feedforward: int = 128, activation=F.relu, 
			    norm_first= False, dropout=0.2, bias=True):
		super().__init__()
		self.head = nn.Linear(in_features, hidden_size)
		self.unflatten = nn.Unflatten(1, (-1, embed_dim))
		self.encoder = TransformerEncoder(embed_dim, nhead, num_layers, dim_feedforward, activation, 
									norm_first, dropout, bias)
		self.fc = nn.Linear(hidden_size, out_features)

	def forward(self, src: torch.Tensor):
		x = self.head(src)
		x = F.silu(x)
		x = self.unflatten(x)
		x = self.encoder(x)
		return self.fc(x.flatten(1))
	

class TransformerDecoder2D(nn.Module):
	def __init__(self, src_in_features: int, out_features: int, embed_dim: int = 8, tgt_in_features: int = None, nhead: int = 2, 
				num_layers: int = 1, hidden_size: int = 128, dim_feedforward: int = 128, activation=F.relu, 
			  norm_first= False, dropout=0.2, bias=True):
		super().__init__()
		tgt_in_features = tgt_in_features or src_in_features
		self.src_head = nn.Linear(src_in_features, hidden_size)
		self.tgt_head = nn.Linear(tgt_in_features, hidden_size)
		self.unflatten = nn.Unflatten(1, (-1, embed_dim))
		self.decoder = TransformerDecoder(embed_dim, nhead, num_layers, dim_feedforward, activation, 
									norm_first, dropout, bias)
		self.fc = nn.Linear(hidden_size, out_features)

	def forward(self, src: torch.Tensor, tgt: torch.Tensor = None):
		src_out = self.src_head(src)
		src_out = F.silu(src_out)
		src_out = self.unflatten(src_out)
		tgt = tgt if tgt is not None else src
		tgt = self.tgt_head(tgt)
		tgt = F.silu(tgt)
		tgt = self.unflatten(tgt)
		out = self.decoder(src_out, tgt)
		return self.fc(out.flatten(1))


class Transformer2D(nn.Module):
	def __init__(self, src_in_features: int, out_features: int, embed_dim: int = 8, tgt_in_features: int = None, nhead: int = 2, 
				num_encoder_layers: int = 1, num_decoder_layers: int = 1, hidden_size: int = 128,
				dim_feedforward: int = 128, activation=F.relu, norm_first= False, dropout=0.2, bias=True):
		super().__init__()
		tgt_in_features = tgt_in_features or src_in_features
		self.src_head = nn.Linear(src_in_features, hidden_size)
		self.tgt_head = nn.Linear(tgt_in_features, hidden_size)
		self.unflatten = nn.Unflatten(1, (-1, embed_dim))
		self.transformer = nn.Transformer(d_model=embed_dim, nhead=nhead, num_encoder_layers=num_encoder_layers, 
									num_decoder_layers=num_decoder_layers, batch_first=True, activation=activation, 
									dim_feedforward=dim_feedforward, dropout=dropout, norm_first=norm_first, bias=bias)
		self.fc = nn.Linear(hidden_size, out_features)

	def forward(self, src: torch.Tensor, tgt: torch.Tensor = None):
		src_out = self.src_head(src)
		src_out = F.silu(src_out)
		src_out = self.unflatten(src_out)
		tgt = tgt if tgt is not None else src
		tgt = self.tgt_head(tgt)
		tgt = F.silu(tgt)
		tgt = self.unflatten(tgt)
		out = self.transformer(src_out, tgt)
		return self.fc(out.flatten(1))
	